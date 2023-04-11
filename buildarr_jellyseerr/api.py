# Copyright (C) 2023 Callum Dickinson
#
# Buildarr is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# Buildarr is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Buildarr.
# If not, see <https://www.gnu.org/licenses/>.


"""
Jellyseerr plugin API functions.
"""


from __future__ import annotations

import json

from datetime import datetime, timezone
from http import HTTPStatus
from logging import getLogger
from typing import TYPE_CHECKING

import requests

from buildarr.state import state

from .exceptions import JellyseerrAPIError

if TYPE_CHECKING:
    from typing import Any, Mapping, Optional

    from .secrets import JellyseerrSecrets


logger = getLogger(__name__)


def api_get(
    secrets: JellyseerrSecrets,
    api_url: str,
    session: Optional[requests.Session] = None,
    use_api_key: bool = True,
    expected_status_code: HTTPStatus = HTTPStatus.OK,
) -> Any:
    """
    Send a `GET` request to a Jellyseerr instance.

    Args:
        secrets (JellyseerrSecrets): Jellyseerr secrets metadata.
        api_url (str): Jellyseerr API command.
        expected_status_code (HTTPStatus): Expected response status. Defaults to `200 OK`.

    Returns:
        Response object
    """

    url = f"{secrets.host_url}/{api_url.lstrip('/')}"
    logger.debug("GET %s", url)
    if not session:
        session = requests.Session()
    res = session.get(
        url,
        headers={"X-Api-Key": secrets.api_key.get_secret_value()} if use_api_key else None,
        timeout=state.config.buildarr.request_timeout,
    )
    res_json = res.json()
    logger.debug("GET %s -> status_code=%i res=%s", url, res.status_code, repr(res_json))
    if res.status_code != expected_status_code:
        api_error(method="GET", url=url, response=res)
    return res_json


def api_post(
    secrets: JellyseerrSecrets,
    api_url: str,
    req: Any = None,
    session: Optional[requests.Session] = None,
    use_api_key: bool = True,
    expected_status_code: HTTPStatus = HTTPStatus.CREATED,
) -> Any:
    """
    Send a `POST` request to a Jellyseerr instance.

    Args:
        secrets (JellyseerrSecrets): Jellyseerr secrets metadata.
        api_url (str): Jellyseerr API command.
        req (Any): Request (JSON-serialisable).
        expected_status_code (HTTPStatus): Expected response status. Defaults to `201 Created`.

    Returns:
        Response object
    """

    url = f"{secrets.host_url}/{api_url.lstrip('/')}"
    logger.debug("POST %s <- req=%s", url, repr(req))
    headers = {"X-Api-Key": secrets.api_key.get_secret_value()} if use_api_key else None
    if not state.dry_run:
        if not session:
            session = requests.Session()
        res = session.post(
            url,
            headers=headers,
            timeout=state.config.buildarr.request_timeout,
            **({"json": req} if req is not None else {}),
        )
    else:
        res = _create_dryrun_response("POST", url, content=json.dumps(req))
    res_json = res.json()
    logger.debug("POST %s -> status_code=%i res=%s", url, res.status_code, repr(res_json))
    if res.status_code != expected_status_code:
        api_error(method="POST", url=url, response=res)
    return res_json


def api_put(
    secrets: JellyseerrSecrets,
    api_url: str,
    req: Any,
    session: Optional[requests.Session] = None,
    use_api_key: bool = True,
    expected_status_code: HTTPStatus = HTTPStatus.OK,
) -> Any:
    """
    Send a `PUT` request to a Jellyseerr instance.

    Args:
        secrets (JellyseerrSecrets): Jellyseerr secrets metadata.
        api_url (str): Jellyseerr API command.
        req (Any): Request (JSON-serialisable).
        expected_status_code (HTTPStatus): Expected response status. Defaults to `200 OK`.

    Returns:
        Response object
    """

    url = f"{secrets.host_url}/{api_url.lstrip('/')}"
    logger.debug("PUT %s <- req=%s", url, repr(req))
    headers = {"X-Api-Key": secrets.api_key.get_secret_value()} if use_api_key else None
    if not state.dry_run:
        if not session:
            session = requests.Session()
        res = session.put(
            url,
            headers=headers,
            json=req,
            timeout=state.config.buildarr.request_timeout,
        )
    else:
        res = _create_dryrun_response("PUT", url, content=json.dumps(req))
    res_json = res.json()
    logger.debug("PUT %s -> status_code=%i res=%s", url, res.status_code, repr(res_json))
    if res.status_code != expected_status_code:
        api_error(method="PUT", url=url, response=res)
    return res_json


def api_delete(
    secrets: JellyseerrSecrets,
    api_url: str,
    session: Optional[requests.Session] = None,
    use_api_key: bool = True,
    expected_status_code: HTTPStatus = HTTPStatus.OK,
) -> None:
    """
    Send a `DELETE` request to a Jellyseerr instance.

    Args:
        secrets (JellyseerrSecrets): Jellyseerr secrets metadata.
        api_url (str): Jellyseerr API command.
        expected_status_code (HTTPStatus): Expected response status. Defaults to `200 OK`.
    """

    url = f"{secrets.host_url}/{api_url.lstrip('/')}"
    logger.debug("DELETE %s", url)
    headers = {"X-Api-Key": secrets.api_key.get_secret_value()} if use_api_key else None
    if not state.dry_run:
        if not session:
            session = requests.Session()
        res = session.delete(
            url,
            headers=headers,
            timeout=state.config.buildarr.request_timeout,
        )
    else:
        res = _create_dryrun_response("DELETE", url)
    logger.debug("DELETE %s -> status_code=%i", url, res.status_code)
    if res.status_code != expected_status_code:
        api_error(method="DELETE", url=url, response=res, parse_response=False)


def api_error(
    method: str,
    url: str,
    response: requests.Response,
    parse_response: bool = True,
) -> None:
    """
    Process an error response from the Jellyseerr API.

    Args:
        method (str): HTTP method.
        url (str): API command URL.
        response (requests.Response): Response metadata.
        parse_response (bool, optional): Parse response error JSON. Defaults to True.

    Raises:
        Jellyseerr API exception
    """

    error_message = (
        f"Unexpected response with status code {response.status_code} from from '{method} {url}':"
    )
    if parse_response:
        res_json = response.json()
        try:
            error_message += f" {_api_error(res_json)}"
        except TypeError:
            for error in res_json:
                error_message += f"\n{_api_error(error)}"
        except KeyError:
            error_message += f" {res_json}"
    raise JellyseerrAPIError(error_message, status_code=response.status_code)


def _api_error(res_json: Any) -> str:
    """
    Generate an error message from a response object.

    Args:
        res_json (Any): Response object

    Returns:
        String containing one or more error messages
    """

    try:
        return res_json["message"]
    except KeyError:
        pass
    try:
        return res_json["error"]
    except KeyError:
        return f"(Unsupported error JSON format) {res_json}"


def _create_dryrun_response(
    method: str,
    url: str,
    headers: Optional[Mapping[str, str]] = None,
    status_code: Optional[int] = None,
    content_type: str = "application/json",
    charset: str = "utf-8",
    content: str = "{}",
) -> requests.Response:
    """
    A utility function for generating `requests.Response` objects in dry-run mode.

    Args:
        method (str): HTTP method of the response to simulate.
        url (str): URL of the request.
        status_code (Optional[int], optional): Status code for the response. Default: auto-detect
        content_type (str, optional): MIME type of response content. Default: `application/json`
        charset (str, optional): Encoding of response content. Default: `utf-8`
        content (str, optional): Response content. Default: `{}`

    Raises:
        ValueError: When an unsupported HTTP method is used

    Returns:
        Generated `requests.Response` object
    """

    method = method.upper()

    response = requests.Response()
    response.url = url
    response.headers["Vary"] = "Accept"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Content-Type"] = f"{content_type}; charset={charset}"
    response.headers["Server"] = "Mono-HTTPAPI/1.0"
    response.headers["Date"] = datetime.now(tz=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %Z")
    response.headers["Transfer-Encoding"] = "chunked"
    if headers:
        response.headers.update(headers)
    if status_code is not None:
        response.status_code = status_code
    elif method == "POST":
        response.status_code = int(HTTPStatus.CREATED)
    elif method == "PUT":
        response.status_code = int(HTTPStatus.ACCEPTED)
    elif method == "DELETE":
        response.status_code = int(HTTPStatus.OK)
    else:
        raise ValueError(
            f"Unsupported HTTP method for creating dry-run response: {str(method)}",
        )
    response.encoding = charset
    if content is not None:
        response._content = content.encode("UTF-8")

    return response

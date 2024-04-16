# Copyright (C) 2015 Johnny Vestergaard <jkv@unixcluster.dk>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
from urllib import parse as urlparse
from io import BytesIO
from http.server import BaseHTTPRequestHandler
import logging

logger = logging.getLogger(__name__)

class HTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, request_bytes, client_address, server_version=None, sys_version=None):
        self.rfile = BytesIO(request_bytes)
        self.wfile = BytesIO()
        self.rfile.seek(0)

        self.client_address = client_address
        self.requestline = ''
        self.request_version = 'HTTP/1.0'
        self.path = ''
        self.command = ''
        self.query = ''
        self.raw_requestline = ''
        self.close_connection = None
        self.request_body = ''
        self.http_host = ''

        self.handle_one_request()

        self.server_version = server_version if server_version is not None else 'HTTPServer'
        self.sys_version = sys_version if sys_version is not None else 'Python'

        url = urlparse.urlparse(self.path)
        self.request_url = self.path
        self.request_raw = request_bytes
        self.request_query = urlparse.parse_qs(url.query, True)
        self.request_params = url.params
        self.request_path = url.path
        self.request_verb = self.command
        self.request_headers = self.headers if hasattr(self, 'headers') else BaseHTTPRequestHandler.MessageClass

    def handle_one_request(self):
        self.raw_requestline = self.rfile.readline(65537)
        if len(self.raw_requestline) > 65536:
            self.send_error(414)
            return
        if not self.raw_requestline:
            self.close_connection = 1
            return
        if not self.parse_request():
            return
        if self.command not in ('PUT', 'GET', 'POST', 'HEAD', 'TRACE', 'OPTIONS'):
            self.send_error(501, f"Unsupported method ({self.command})")
            return
        self.request_body = self.rfile.read()

    def parse_request(self):
        logger.debug(f"Raw request line: {self.raw_requestline}")
        try:
            result = super().parse_request()
            logger.debug(f"Request parsed successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to parse request: {e}")
            self.send_error(400, 'Bad request syntax')
            return False

    def set_response(self, body, http_code=200, headers=(('Content-type', 'text/html; charset=utf-8'),)):
        self.send_response(http_code)
        for header in headers:
            self.send_header(header[0], header[1])
        self.end_headers()
        self.wfile.write(body.encode('utf-8') if isinstance(body, str) else body)

    def send_error(self, code, message=None):
        super().send_error(code, message)
        raise HTTPError(self.get_response())

    def get_response(self):
        return self.wfile.getvalue()

    def get_response_header(self):
        response = self.wfile.getvalue()
        header_end_idx = response.find(b'\r\n\r\n') + 4
        return response[:header_end_idx] if header_end_idx > 4 else b''

    def get_response_body(self):
        response = self.wfile.getvalue()
        body_start_idx = response.find(b'\r\n\r\n') + 4
        return response[body_start_idx:] if body_start_idx > 4 else b''

    def version_string(self):
        return f'{self.server_version} {self.sys_version}'

class HTTPError(Exception):
    def __init__(self, error_text):
        self.error_text = error_text


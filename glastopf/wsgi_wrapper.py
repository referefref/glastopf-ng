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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
from webob import Request, Response

class GlastopfWSGI(object):
    def __init__(self, honeypot):
        self.honeypot = honeypot

    def remove_hop_by_hop_headers(self, headers):
        hop_by_hop_names = ("connection", "keep-alive", "proxy-authenticate",
                            "proxy-authorization", "te", "trailers",
                            "transfer-encoding", "upgrade")
        for header in hop_by_hop_names:
            if header in headers:
                del headers[header]

    def application(self, environ, start_response):
        req_webob = Request(environ)
        res_webob = Response()

        # Handle request_body as bytes directly from WSGI environment
        request_body = environ['wsgi.input'].read()

        # Adjust address handling to ensure correct types
        remote_addr = (req_webob.remote_addr, int(environ["REMOTE_PORT"]))
        sensor_addr = (environ['SERVER_NAME'], int(environ.get('SERVER_PORT', 80)))

        # Handle request and manage response headers and body properly
        header, body = self.honeypot.handle_request(request_body, remote_addr, sensor_addr)
        
        # Ensure the header is treated as a string
        if isinstance(header, bytes):
            header = header.decode('utf-8')
        
        proto, code, msg = ['HTTP/1.0', '200', 'OK']

        # Process headers
        for h in header.split('\n'):
            if ":" in h:
                h, v = h.split(":", 1)
                res_webob.headers[str(h.strip())] = str(v.strip())
            elif "HTTP/" in h:
                proto, code, msg = h.split(" ", 2)

        # Set response status, charset, and body
        res_webob.status = code
        res_webob.charset = "utf-8"
        res_webob.body = body if isinstance(body, bytes) else body.encode('utf-8')

        # Remove hop-by-hop headers
        self.remove_hop_by_hop_headers(res_webob.headers)
        return res_webob(environ, start_response)


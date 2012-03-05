
#
# rpclib - Copyright (C) Rpclib contributors.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#


"""This module contains a server implementation that uses a raw tcp socket that
processes ONE message per connection.

This module is a shameless rip-off from http://docs.python.org/library/socketserver.html
"""

import logging
logger = logging.getLogger(__name__)

import socket

import SocketServer

from rpclib._base import MethodContext
from rpclib.server import ServerBase


class DefaultTcpServer(object):
    def __init__(self, params, RequestHandler):
        self.host, self.port = params
        self.RequestHandler = RequestHandler

    def serve_forever(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))

        s.listen(10)

        while True:
            conn, addr = s.accept()
            data_q = []
            print 'Connection address:', addr
            while True:
                data = conn.recv(1492)
                if data:
                    data_q.append(data)
                else:
                    break
            conn.close()

class TcpMethodContext(MethodContext):
    def __init__(self, app):
        MethodContext.__init__(self, app)
        self.transport.type = 'socket/tcp'
        self.transport.client_params = None
        self.transport.server_params = None

class TCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()

        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

backend_map = {
    'default': DefaultTcpServer,
}

class TcpServer(ServerBase):
    """The TCP Server transport."""
    transport = 'http://rpclib.org/socket/tcp'

    def __init__(self, app, app_params, interface_params=None, backend='default'):
        ServerBase.__init__(self, app)

        assert backend in backend_map

        self.app_params = app_params
        self.backend = backend
        if interface_params is not None:
            logger.warn("interface_params is currently ignored.")
        self.interface_params = interface_params

    def serve_forever(self):
        """Runs the TCP server."""

        HOST,PORT = self.app_params
        server = backend_map[self.backend]( (HOST, PORT), TCPHandler)
        logger.info("listening to %s:%d for application requests." %
                                                        self.app_params)
        if self.interface_params is not None:
            logger.info("listening to %s:%d for interface requests." %
                                                        self.interface_params)
        return server.serve_forever()

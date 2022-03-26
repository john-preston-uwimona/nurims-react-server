import os
import threading
import shared_objects
import time
import tracemalloc
import resource
from OpenSSL import SSL

from twisted.internet import ssl, reactor
from twisted.web import static
from twisted.web.server import Site
from api_service import ApiService, ApiServiceFactory
# from log_service import LogService
from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.resource import WebSocketResource
# from sensordb import SensorDb

# start memory monitor trace
tracemalloc.start()

# initialise shared objects
shared_objects.init('../config/config.json')

# # initialise database if necessary
# sdb = SensorDb.SensorDb(config=shared_objects.config, log=shared_objects.log)
# sdb.close()


class CtxFactory(ssl.ClientContextFactory):
    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file(shared_objects.relative_path(shared_objects.config["server"]["crt"]))
        ctx.use_privatekey_file(shared_objects.relative_path(shared_objects.config["server"]["key"]))

        return ctx


if __name__ == "__main__":
    try:
        # ensure paths are available
        for key in shared_objects.config["paths"]:
            p = os.path.join(os.path.dirname(os.path.abspath(__file__)), shared_objects.config["paths"][key]["path"])
            if not os.path.exists(p):
                shared_objects.log.info("creating system path: {}".format(p))
                os.makedirs(p)

        # config web and websocket server
        root = static.File('public')

        # factory1 = WebSocketServerFactory()
        factory1 = ApiServiceFactory("ws://0.0.0.0/{}:{}".format(shared_objects.config["server"]["websocket"],
                                                                 shared_objects.config["server"]["port"]))
        factory1.protocol = ApiService
        factory1.startFactory()  # when wrapped as a Twisted Web resource, start the underlying factory manually
        root.putChild(shared_objects.config["server"]["websocket"].encode(), WebSocketResource(factory1))

        # factory2 = WebSocketServerFactory()
        # factory2.protocol = LogService
        # factory2.startFactory()  # when wrapped as a Twisted Web resource, start the underlying factory manually
        # root.putChild(shared_objects.config["logger"]["websocket"].encode(), WebSocketResource(factory2))

        # both under one Twisted Web Site
        site = Site(root)

        # start housekeeping thread after 5 seconds to allow database to be verified
        # housekeeping.init(factory1)

        # openssl genrsa -aes256 -passout pass:gsahdg -out server.pass.key 4096
        # ...
        # openssl rsa -passin pass:gsahdg -in server.pass.key -out server.key
        # writing RSA key
        # rm server.pass.key
        # openssl req -new -key server.key -out server.csr
        # ...
        # Country Name (2 letter code) [AU]:US
        # State or Province Name (full name) [Some-State]:California
        # ...
        # A challenge password []:
        # ...
        # openssl x509 -req -sha256 -days 365 -in server.csr -signkey server.key -out server.crt
        # The server.crt file is your site certificate along with the server.key private key.

        shared_objects.log.info("starting websocket server on port {}".format(shared_objects.config["server"]["port"]))
        # reactor.listenTCP(shared_objects.config["server"]["port"], site)
        reactor.listenSSL(shared_objects.config["server"]["port"], site, CtxFactory())
        reactor.run()
    except AttributeError as e:
        shared_objects.log.error(e)
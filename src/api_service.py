import json
import queue
import threading
import time
import shared_objects
import gc

from docbook import Docbook
from md import Markdown
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from api_handlers import run
from orgdb import OrgDb


class RequestResponseManager:
    # server_message_queue = queue.Queue()

    def __init__(self, name, reactor, send_message):
        self.reactor = reactor
        self.send = send_message
        self.request_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.request_thread = threading.Thread(target=self.request_worker_runnable, name=name, daemon=True)
        self.response_thread = threading.Thread(target=self.response_worker_runnable, name=name, daemon=True)
        self.connected = True
        self.keep_running = True
        self.request_thread.start()
        self.response_thread.start()
        self.client = None
        self.db = None
        self.md = Markdown.Markdown(config=shared_objects.config["markdown"],
                                    log=shared_objects.log)
        self.docbook = Docbook.Docbook(config=shared_objects.absolute_path(shared_objects.config["docbook"]),
                                       pdf_path=shared_objects.absolute_path(shared_objects.config["paths"]["pdf"]),
                                       log=shared_objects.log)

    def process_request(self, request):
        self.request_queue.put(request)

    def get_client(self):
        return self.client

    def connection_open(self, reactor, send_message):
        self.reactor = reactor
        self.send = send_message

    def connection_close(self):
        self.connected = False
        if self.db:
            pass
            # self.db.close()

    def response_worker_runnable(self):
        while self.keep_running:
            rq = self.response_queue.get(block=True)
            if self.connected:
                if "ts" not in rq:
                    rq["ts"] = time.perf_counter()
                rq.update({"elapsed": "{:.3f} secs".format(time.perf_counter() - rq["ts"])})
                self.reactor.callFromThread(self.send, json.dumps(rq).encode('utf8'))

                # if "recipient" in rq and rq["recipient"] == "server":
                #     # print("RESPONSE FOR SERVER", rq)
                #     RequestResponseManager.server_message_queue.put(rq)
                #     # self.reactor.callFromThread(self.send, json.dumps(rq).encode('utf8'))
                # else:
                #     self.reactor.callFromThread(self.send, json.dumps(rq).encode('utf8'))
                shared_objects.log.info("response: {}".format(json.dumps(rq)))
            self.response_queue.task_done()

    def request_worker_runnable(self):
        # initialise DB object
        # self.db = OrgDb.OrgDb(config=shared_objects.config, log=shared_objects.log)
        # loop continuously to read and run requests posted to the message queue
        while self.keep_running:
            request = self.request_queue.get(block=True)
            # handle set_org_db here
            if request["cmd"] == "set_org_db":
                if request["org"]["name"] != "":
                    self.db = OrgDb.OrgDb(name=request["org"]["name"],
                                          config=shared_objects.absolute_path(shared_objects.config["db"]),
                                          log=shared_objects.log)
                request.update({
                    "response": {
                        "message": "",
                        "status": 0
                    }
                })
                self.response_queue.put(request)
            # if self.client is None and "cmd" in request and request["cmd"] == "register_client":
            #     self.client = request["uuid"]
            # if "broadcast" in request or "broadcast_response" in request:
            #     self.reactor.callFromThread(self.send, json.dumps(request).encode('utf8'))
            else:
                run(request, db=self.db, md=self.md, docbook=self.docbook, msg_queue=self.response_queue)
            self.request_queue.task_done()


class ApiService(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()
        self.peer = None
        # self.rr_manager = RequestResponseManager()
        self.rr_manager = None

    def onMessage(self, payload, is_binary):
        if not is_binary:
            try:
                request = json.loads(payload.decode('utf8'))
                # request["peer"] = self.peer
                # initialise performance timing variable
                request["ts"] = time.perf_counter()
                shared_objects.log.info("request: {}".format(json.dumps(request)))
                self.rr_manager.request_queue.put(request)
                # handle get_server_info request here
                # if "cmd" in request and request["cmd"] == "get_server_info":
                #     self.rr_manager.message_queue.put(self.get_system_info(request))
                # elif "cmd" in request and request["cmd"] == "get_client_online_status":
                #     self.rr_manager.message_queue.put(request)
                # else:
                #     if "broadcast" in request or "broadcast_response" in request:
                #         self.factory.broadcast(request, request["recipient"])
                #     else:
                #         self.rr_manager.process_request(request)
            except json.decoder.JSONDecodeError:
                request = {"message": "Exception: Cannot parse request as JSON object", "status": 1}
                self.rr_manager.process_request(request)
        else:
            request = {"message": "Exception: Binary JSON request not allowed.", "status": 1}
            self.rr_manager.process_request(request)

    def onConnect(self, request):
        self.peer = request.peer

    def onOpen(self):
        self.rr_manager = RequestResponseManager(self.peer, self.factory.reactor, self.sendMessage)
        shared_objects.log.info("websocket connection opened.")
        self.factory.register(self, self.rr_manager)

    def onClose(self, was_clean, code, reason):
        self.rr_manager.connection_close()
        shared_objects.log.info("websocket connection closed.")
        gc.collect()

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

    def get_system_info(self, request):
        user_connections = 0
        sensor_connections = 0
        for c in self.factory.clients:
            if c["rr_manager"].client is None and "tcp4" in c["client"]:
                user_connections += 1
            else:
                sensor_connections += 1
        request.update({
            "data": {
                "info": {
                    "user_connections": user_connections,
                    "sensor_connections": sensor_connections
                },
                "message": "",
                "status": 0
            }
        })
        return request


class ApiServiceFactory(WebSocketServerFactory):
    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []

    def __get_client(self, client):
        found = False
        for c in self.clients:
            if c["client"] == client:
                return c
        return None

    def __remove_client(self, client):
        for i in range(len(self.clients)):
            c = self.clients[i]
            if c["client"] == client:
                del self.clients[i]
                return

    def register(self, client, rr_manager):
        if self.__get_client(client.peer) is None:
            shared_objects.log.info("registered websocket client {}".format(client.peer))
            self.clients.append({"client": client.peer, "rr_manager": rr_manager})

    def unregister(self, client):
        shared_objects.log.info("unregistered websocket client {}".format(client.peer))
        self.__remove_client(client.peer)

    def broadcast(self, request, recipient=None):
        at_least_one_message = False
        if recipient is None:
            for c in self.clients:
                self.reactor.callFromThread(c["rr_manager"].send, json.dumps(request).encode('utf8'))
                at_least_one_message = True
        else:
            for c in self.clients:
                if recipient.startswith("tcp4"):
                    if c["client"] == recipient:
                        self.reactor.callFromThread(c["rr_manager"].send, json.dumps(request).encode('utf8'))
                        at_least_one_message = True
                else:
                    if c["rr_manager"].client == recipient:
                        self.reactor.callFromThread(c["rr_manager"].send, json.dumps(request).encode('utf8'))
                        at_least_one_message = True

        return at_least_one_message

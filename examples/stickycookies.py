from libmproxy import controller, proxy

class StickyMaster(controller.Master):
    def __init__(self, server):
        controller.Master.__init__(self, server)
        self.stickyhosts = {}

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, msg):
        hid = (msg.host, msg.port)
        if msg.headers["cookie"]:
            self.stickyhosts[hid] = msg.headers["cookie"]
        elif hid in self.stickyhosts:
            msg.headers["cookie"] = self.stickyhosts[hid]
        msg._ack()

    def handle_response(self, msg):
        hid = (msg.request.host, msg.request.port)
        if msg.headers["set-cookie"]:
            self.stickyhosts[hid] = f.response.headers["set-cookie"]
        msg._ack()


ssl_config = proxy.SSLConfig(
    "~/.mitmproxy/cert.pem"
)
server = proxy.ProxyServer(ssl_config, 8080)
m = StickyMaster(server)
m.run()

from threading import Thread
from websockets.sync.server import WebSocketServer,ServerConnection,serve
from logging import getLogger
from json import dumps

logger_child_name = 'socket server'

logger = getLogger().getChild(logger_child_name)
logger.debug(f'loaded socket_server.py')

class SocketServer(Thread):
    port: int = 8765
    server: WebSocketServer = None
    clients: dict[int, ServerConnection] = {}
    imagevalue_imagenothing: bytes = None
    imagevalue_information: bytes = None
    imagevalue_summary: bytes = None
    imagevalue_notesradar: bytes = None
    imagevalue_screenshot: bytes = None
    imagevalue_scoreinformation: bytes = None
    imagevalue_scoregraph: bytes = None
    musictable = None
    scoreresult = None
    scoreresult_music = None

    def __init__(self, port: int = None):
        if port is not None:
            self.port = port
        
        Thread.__init__(self, daemon=True)
    
    def run(self):
        def handler(connection: ServerConnection):
            self.clients[connection.id] = connection


            try:
                for message in connection:
                    if message == 'get_informationimage':
                        target = self.imagevalue_information
                    if message == 'get_summaryimage':
                        target = self.imagevalue_summary
                    if message == 'get_notesradarimage':
                        target = self.imagevalue_notesradar
                    if message == 'get_screenshotimage':
                        target = self.imagevalue_screenshot
                    if message == 'get_scoreinformationimage':
                        target = self.imagevalue_scoreinformation
                    if message == 'get_scoregraphimage':
                        target = self.imagevalue_scoregraph
                    if message == 'get_musictable':
                        obj = { "method" : "get_musictable" }
                        if self.musictable is not None:
                            obj["result"] = self.musictable
                        target = dumps(obj)
                    if message == 'get_scoreresult':
                        obj = { "method" : "get_scoreresult", "music": self.scoreresult_music }
                        if self.scoreresult is not None:
                            obj["result"] = self.scoreresult
                        target = dumps(obj)

                    if target is not None:
                        connection.send(target)
                    else:
                        connection.send(self.imagevalue_imagenothing)
            finally:
                del self.clients[connection.id]
        
        try:
            self.server = serve(handler, '0.0.0.0', self.port)
            self.server.serve_forever()
        except Exception as ex:
            logger.exception(ex)
        
    def update_information(self, imagevalue):
        self.imagevalue_information = imagevalue
        self.broadcast('update_information')
    
    def update_summary(self, imagevalue):
        self.imagevalue_summary = imagevalue
        self.broadcast('update_summary')
    
    def update_notesradar(self, imagevalue):
        self.imagevalue_notesradar = imagevalue
        self.broadcast('update_notesradar')
    
    def update_screenshot(self, imagevalue):
        self.imagevalue_screenshot = imagevalue
        self.broadcast('update_screenshot')
    
    def update_scoreinformation(self, imagevalue):
        self.imagevalue_scoreinformation = imagevalue
        self.broadcast('update_scoreinformation')

    def update_scoregraph(self, imagevalue):
        self.imagevalue_scoregraph = imagevalue
        self.broadcast('update_scoregraph')

    def broadcast(self, message):
        deletetargets = []
        for id, client in self.clients.items():
            try:
                client.send(message)
            except:
                deletetargets.append(id)
        
        for id in deletetargets:
            del self.clients[id]


    def stop(self):
        if self.server is not None:
            try:
                self.server.shutdown()
            except Exception as ex:
                logger.exception(ex)

if __name__ == '__main__':
    server = SocketServer(8000)
    server.start()
    server.join()
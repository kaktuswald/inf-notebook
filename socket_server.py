from threading import Thread
from websockets import ServerConnection
from websockets.sync.server import Server,serve

class SocketServer(Thread):
    port: int = 8765
    server: Server = None
    clients: dict[int, ServerConnection] = {}

    def __init__(self, port: int = None):
        if port is not None:
            self.port = port
        
        Thread.__init__(self, daemon=True)
    
    def run(self):
        def handler(connection: ServerConnection):
            self.clients[connection.id] = connection

            print('websocket connection open', connection.id)

            try:
                while True:
                    pass
            except:
                del self.clients[connection.id]
                print('exeption')
            
            print('websocket connection close', connection.id)
        
        try:
            self.server = serve(handler, 'localhost', self.port)
            self.server.serve_forever()
        except:
            pass
        
    def update_information(self):
        self.broadcast('update_information')
    
    def update_summary(self):
        self.broadcast('update_summary')
    
    def update_notesradar(self):
        self.broadcast('update_notesradar')
    
    def update_screenshot(self):
        self.broadcast('update_screenshot')
    
    def update_scoreinformation(self):
        self.broadcast('update_scoreinformation')

    def update_scoregraph(self):
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

        print('broadcast', message, len(self.clients))

    def stop(self):
        self.server.shutdown()

if __name__ == '__main__':
    server = SocketServer(8000)
    server.start()
    server.join()
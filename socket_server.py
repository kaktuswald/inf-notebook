from threading import Thread
from websockets.sync.server import Server,ServerConnection,serve
from logging import getLogger
from json import loads,dumps

logger_child_name = 'socket server'

logger = getLogger().getChild(logger_child_name)
logger.debug(f'loaded socket_server.py')

from record import NotebookRecent

class Events():
    '''イベントの定義
    '''
    UPDATE_INFORMATIONIMAGE: str = 'update_informationimage'
    '''インフォメーション画像の更新'''
    UPDATE_SUMMARYIMAGE: str = 'update_summaryimage'
    '''統計画像の更新'''
    UPDATE_NOTESRADARIMAGE: str = 'update_notesradarimage'
    '''ノーツレーダー画像の更新'''
    UPDATE_SCREENSHOTIMAGE: str = 'update_screenshotimage'
    '''スクリーンショット画像の更新'''
    UPDATE_SCOREINFORMATIONIMAGE: str = 'update_scoreinformationimage'
    '''譜面記録画像の更新'''
    UPDATE_SCOREGRAPHIMAGE: str = 'update_scoregraphimage'
    '''グラフ画像の更新'''
    UPDATE_RECENTS: str = 'update_recents'
    '''最近のリザルトの更新'''
    UPDATE_SCORERESULT: str = 'update_scoreresult'
    '''譜面記録の更新'''

class Requests():
    '''リクエストの定義
    '''
    GET_INFORMATIONIMAGE: str = 'get_informationimage'
    '''インフォメーション画像の取得'''
    GET_SUMMARYIMAGE: str = 'get_summaryimage'
    '''統計画像の取得'''
    GET_NOTESRADARIMAGE: str = 'get_notesradarimage'
    '''ノーツレーダー画像の取得'''
    GET_SCREENSHOTIMAGE: str = 'get_screenshotimage'
    '''スクリーンショット画像の取得'''
    GET_SCOREINFORMATIONIMAGE: str = 'get_scoreinformationimage'
    '''譜面記録画像の取得'''
    GET_SCOREGRAPHIMAGE: str = 'get_scoregraphimage'
    '''グラフ画像の取得'''
    GET_MUSICTABLE: str = 'get_musictable'
    '''楽曲テーブルの取得'''
    GET_SCORERESULT: str = 'get_scoreresult'
    '''楽曲プレイ履歴の取得'''
    GET_RESENTS: str = 'get_recents'
    '''最近のリザルトの取得'''

class Statuses():
    '''レスポンス状態の定義
    '''
    SUCCESS: str = 'success'
    '''成功'''
    INVALID_REQUEST: str = 'invalid_request'
    '''無効リクエスト'''
    FAILED: str = 'failed'
    '''応答に失敗(使用しないことを前提の予約 原因ごとに定義するべき)'''

class DataTypes():
    '''データ種類
    '''
    TEXT_PLAIN: str = 'text/plain'
    '''プレーンテキスト'''
    APP_JSON: str = 'application/json'
    '''JSON型'''
    IMAGE_PNG: str = 'image/png'
    '''PNG形式画像'''
    IMAGE_JPG: str = 'image/jpg'
    '''JPG形式画像'''

class SocketServer(Thread):
    '''WebSocketサーバ

    メッセージフォーマット: json

    イベントフォーマット: {
        'e': イベント名(Events),
    }

    リクエストフォーマット: {
        'r': リクエスト名(Requests),
        'p(optional)': {
            't': データタイプ(DataTypes),
            'd': データ,
        },
    }
    
    レスポンスフォーマット: {
        'r': リクエスト名(Requests),
        's': 状態(Statuses),
        'p(optional)': {
            't': データタイプ(DataTypes),
            'd': データ,
        },
    }
    '''
    port: int = 8765
    server: Server | None = None
    clients: dict[int, ServerConnection] = {}

    encodedimage_imagenothing: str | None = None

    encodedimage_information: str | None = None
    encodedimage_summary: str | None = None
    encodedimage_notesradar: str | None = None
    encodedimage_screenshot: str | None = None
    encodedimage_scoreinformation: str | None = None
    encodedimage_scoregraph: str | None = None

    musictable: dict[str, any] | None = None
    scoreresult: dict[str, any] | None = None
    recents: NotebookRecent = None

    def __init__(self, port: int = None):
        if port is not None:
            self.port = port
        
        Thread.__init__(self, daemon=True)
    
    def run(self):
        def handler(connection: ServerConnection):
            self.clients[connection.id] = connection

            try:
                for message in connection:
                    message = loads(message)
                    if not 'r' in message.keys():
                        connection.send(None)
                        continue

                    request = message['r']

                    payload: dict[str: str] | None = None
                    if request == Requests.GET_INFORMATIONIMAGE:
                        payload = self.response_image(self.encodedimage_information)
                    if request == Requests.GET_SUMMARYIMAGE:
                        payload = self.response_image(self.encodedimage_summary)
                    if request == Requests.GET_NOTESRADARIMAGE:
                        payload = self.response_image(self.encodedimage_notesradar)
                    if request == Requests.GET_SCREENSHOTIMAGE:
                        payload = self.response_image(self.encodedimage_screenshot)
                    if request == Requests.GET_SCOREINFORMATIONIMAGE:
                        payload = self.response_image(self.encodedimage_scoreinformation)
                    if request == Requests.GET_SCOREGRAPHIMAGE:
                        payload = self.response_image(self.encodedimage_scoregraph)
                    if request == Requests.GET_MUSICTABLE:
                        payload = self.response_json(self.musictable)
                    if request == Requests.GET_SCORERESULT:
                        payload = self.response_json(self.scoreresult)
                    if request == Requests.GET_RESENTS:
                        payload = self.response_json(self.recents.json)
                                        
                    if payload is not None:
                        message = {
                            'r': request,
                            's': Statuses.SUCCESS,
                            'p': payload,
                        }
                    else:
                        message = {
                            'r': request,
                            's': Statuses.INVALID_REQUEST,
                        }

                    connection.send(dumps(message))
            finally:
                del self.clients[connection.id]
        
        try:
            self.server = serve(handler, '0.0.0.0', self.port)
            self.server.serve_forever()
        except Exception as ex:
            logger.exception(ex)
    
    def response_image(self, target: str | None):
        return {
            't': DataTypes.IMAGE_PNG,
            'd': target if target is not None else self.encodedimage_imagenothing,
        }
    
    def response_json(self, target: dict[str, any] | None):
        return {
            't': DataTypes.APP_JSON,
            'd': target if target is not None else {},
        }

    def reset_scoreinformation(self):
        self.encodedimage_scoreinformation = self.encodedimage_imagenothing
        self.broadcast(Events.UPDATE_SCOREINFORMATIONIMAGE)
    
    def reset_scoregraph(self):
        self.encodedimage_scoregraph = self.encodedimage_imagenothing
        self.broadcast(Events.UPDATE_SCOREGRAPHIMAGE)
    
    def update_information(self, encodedimage: str | None):
        self.encodedimage_information = encodedimage
        self.broadcast(Events.UPDATE_INFORMATIONIMAGE)
    
    def update_summary(self, encodedimage: str | None):
        self.encodedimage_summary = encodedimage
        self.broadcast(Events.UPDATE_SUMMARYIMAGE)
    
    def update_notesradar(self, encodedimage: str | None):
        self.encodedimage_notesradar = encodedimage
        self.broadcast(Events.UPDATE_NOTESRADARIMAGE)
    
    def update_screenshot(self, encodedimage: str | None):
        self.encodedimage_screenshot = encodedimage
        self.broadcast(Events.UPDATE_SCREENSHOTIMAGE)
    
    def update_scoreinformation(self, encodedimage: str | None):
        self.encodedimage_scoreinformation = encodedimage
        self.broadcast(Events.UPDATE_SCOREINFORMATIONIMAGE)

    def update_scoregraph(self, encodedimage: str | None):
        self.encodedimage_scoregraph = encodedimage
        self.broadcast(Events.UPDATE_SCOREGRAPHIMAGE)

    def update_recents(self):
        self.broadcast(Events.UPDATE_RECENTS)
    
    def update_scoreresult(self):
        self.broadcast(Events.UPDATE_SCORERESULT)

    def broadcast(self, event: str, payload: any = None):
        if payload is not None:
            message = dumps({
                'e': event,
                'p': payload,
            })
        else:
            message = dumps({
                'e': event,
            })

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
from webview import create_window,start
from webview.window import Window
from bottle import Bottle,HTTPResponse,FormsDict,FileUpload,static_file,run,request
from json import dumps
from socket import socket,AF_INET,SOCK_STREAM

from setting import Setting,default
from socket_server import SocketServer

class RecentResult():
    class NewFlags():
        cleartype: bool = False
        djlevel: bool = False
        score: bool = False
        misscount: bool = False
    
    timestamp: str
    musicname: str = None
    playmode: str = None
    difficulty: str = None
    news: NewFlags = None
    latest: bool = False
    saved: bool = False
    filtered: bool = False

    def __init__(self, timestamp: str):
        self.timestamp = timestamp
        self.news = self.NewFlags()
    
    def encode(self):
        return {
            'timestamp': self.timestamp,
            'musicname': self.musicname,
            'playmode': self.playmode,
            'difficulty': self.difficulty,
            'news_cleartype': self.news.cleartype,
            'news_djlevel': self.news.djlevel,
            'news_score': self.news.score,
            'news_misscount': self.news.misscount,
            'latest': self.latest,
            'saved': self.saved,
            'filtered': self.filtered,
        }

class Gui():
    setting: Setting = None
    api: object = None
    bottle: Bottle = None
    socketserver: SocketServer = None
    imagevalues: dict[str, bytes] = {}
    uploadedimages: dict[str, object] = {}
    mainwindow: Window = None
    modalwindow: Window = None

    @staticmethod
    def response_image(imagevalue: bytes):
        response = HTTPResponse(status=200, body=imagevalue)
        response.set_header('Content-Type', 'image/png')
        response.set_header('Access-Control-Allow-Origin', '*')

        return response

    @staticmethod
    def response_notfound():
        response = HTTPResponse(status=404, body="Not Found.")
        response.set_header('Content-Type', 'text/plain')
        response.set_header('Access-Control-Allow-Origin', '*')
        
        return response

    def __init__(self, version: str, setting: Setting, api: object):
        self.setting = setting
        self.api = api

        self.bottle: Bottle = Bottle()

        @self.bottle.route('/')
        def root():
            return static_file('index.html', root='web')

        @self.bottle.route('/<filename>')
        def top(filename: str = 'index.html'):
            return static_file(filename, root='web')

        @self.bottle.route('/lib/<filename>')
        def root(filename: str):
            return static_file(filename, root='web/lib')

        @self.bottle.route('/image/<filename>')
        def request_image(filename: str):
            '''画像ファイルリクエスト

            Args:
                filename(str): ファイル名
            '''
            if filename in self.imagevalues.keys():
                return self.response_image(self.imagevalues[filename])
            
            return self.response_notfound()

        @self.bottle.post('/upload/image/<filename>')
        def upload_image(filename: str):
            if not isinstance(request.files, FormsDict):
                return

            dict: FormsDict = request.files

            imagefile: FileUpload = dict.get('imagefile')
            if not isinstance(imagefile, FileUpload):
                return
            
            file = imagefile.file
            
            if not hasattr(file, 'read'):
                return
            
            self.imagevalues[filename] = imagefile.file.read()
            print('uploaded', filename)

        self.port_socket = self.checkport(setting.port['socket'] if isinstance(setting.port['socket'], int) else default['port']['socket'])
        self.socketserver = SocketServer(self.port_socket)
        self.socketserver.start()

        self.port_main = self.checkport(setting.port['main'] if isinstance(setting.port['main'], int) else default['port']['main'])

        print(self.port_main, self.port_socket)

        def start_server(bottle, port):
            run(bottle, host='0.0.0.0', port=port)
        
        from threading import Thread
        Thread(target=start_server, args=(self.bottle, self.port_main,), daemon=True).start()

        title = f'リザルト手帳 {version}'

        self.mainwindow: Window = create_window(
            title,
            f'http://localhost:{self.port_main}',
            js_api=self.api,
            width=1000,
            height=600,
            resizable=False,
            text_select=True,
            draggable=True,
        )

    def checkport(self, port):
        while True:
            with socket(AF_INET, SOCK_STREAM) as sock:
                try:
                    sock.bind(('127.0.0.1', port))
                    return port
                except Exception as ex:
                    pass
            port += 1

    def start(self, start_callback):
        self.start_callback = start_callback
        start(
            self.bind,
            icon='icon.ico',
            debug=self.setting.debug,
        )

    def bind(self):
        self.start_callback()
    
    def openwindow_modal(self, filename: str, title: str, api: object, width:int = 640, height:int = 480):
        '''モーダルウィンドウを開く
        
        Args:
            filename(str): 開くHTMLファイルのファイル名
            title(str): ウィンドウのタイトル
            api(object): APIインスタンス
            width(int): ウィンドウの幅
            height(int): ウィンドウの高さ
        '''
        self.modalwindow = create_window(
            title,
            f'http://localhost:{self.port_main}/{filename}',
            js_api=api,
            width=width,
            height=height,
            resizable=False,
            text_select=True,
            draggable=False,
            on_top=True,
        )

        def close():
            self.modalwindow.destroy()

        def closed():
            del self.modalwindow
            self.modalwindow = None
        
        self.modalwindow.events.closed += closed

        self.modalwindow.expose(close)

        while self.modalwindow is not None:
            pass

    def switch_detect_infinitas(self, flag: bool):
        self.send_message('switch_detect_infinitas', flag)

    def switch_capturable(self, flag: bool):
        self.send_message('switch_capturable', flag)

    def send_message(self, message, data=None):
        if data is None:
            self.mainwindow.evaluate_js(f'communication_message("{message}");')
        else:
            self.mainwindow.evaluate_js(f'communication_message("{message}", {dumps(data)});')

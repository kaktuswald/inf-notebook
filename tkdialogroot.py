from tkinter import Tk,Label,filedialog 
from typing import Callable
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from infnotebook import title,icon_filename

font = 'Meiryo'

class TkDialogRoot():
    def __enter__(self):
        self.root = Tk()
        
        try:
            self.root.withdraw()
        except Exception as ex:
            logger.exception(ex)
        
        try:
            self.root.attributes('-topmost', True)
        except Exception as ex:
            logger.exception(ex)
        
        return self
        
    def __exit__(self, exc_type, exc, tb):
        try:
            self.root.destroy()
        except Exception as ex:
            logger.exception(ex)
    
    def opendialog_selectfiles(self, **kwargs):
        filepaths = filedialog.askopenfilenames(**kwargs)
        
        return filepaths if filepaths else None
    
    def opendialog_selectfile(self, **kwargs):
        filepaths = filedialog.askopenfilename(**kwargs)
        
        return filepaths if filepaths else None
    
    def opendialog_selectdirectory(self, **kwargs):
        filepaths = filedialog.askdirectory(**kwargs)
        
        return filepaths if filepaths else None

class ProcessingMessage():
    def __init__(self, message:str):
        self.message = message
    
    def __enter__(self):
        self.root = Tk()
        self.root.iconbitmap(icon_filename)
        self.root.resizable(0, 0)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)

        width = 350
        height = 150
        left = self.root.winfo_screenwidth() // 2 - width // 2
        top = self.root.winfo_screenheight() // 2 - height // 2
        self.root.geometry(f'{width}x{height}+{left}+{top}')

        label_title = Label(self.root, text=title, font=(font, 20))
        label_title.pack(pady=20)

        self.label_message = Label(self.root, text=self.message, font=(font, 16))
        self.label_message.pack(expand=True)

        return self

    def __exit__(self, exc_type, exc, tb):
        if self.root:
            self.root.destroy()
    
    def open(self, task:Callable):
        def func():
            task()
            self.root.destroy()
            self.root = None
        
        self.root.after(100, func)
        self.root.mainloop()

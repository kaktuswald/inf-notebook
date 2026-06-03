from tkinter import Tk,filedialog 
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

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

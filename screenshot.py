from datetime import datetime
from PIL import Image,ImageGrab
from logging import getLogger
from os.path import exists,basename

logger_child_name = 'screenshot'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded screenshot.py')

from define import define
from recog import recog

class Screen:
    def __init__(self, original, monochrome, filename):
        self.original = original
        self.monochrome = monochrome
        self.filename = filename

class Screenshot:
    area = None

    def shot(self):
        if self.area is not None:
            self.image = ImageGrab.grab(all_screens=True, bbox=self.area)
        else:
            self.image = ImageGrab.grab(all_screens=True)

    def get(self):
        return self.image.convert('RGBA')

    def get_resultscreen(self):
        if not recog.get_is_screen_result(self.image):
            return None

        original = self.image.convert('RGBA')
        monochrome = original.convert('L')

        if not recog.get_is_result(monochrome):
            return None

        now = datetime.now()
        filename = f"{now.strftime('%Y%m%d-%H%M%S-%f')}.png"

        return Screen(original, monochrome, filename)

def open_screenimage(filepath):
    if not exists(filepath):
        return None
    
    image = Image.open(filepath)
    filename = basename(filepath)

    return Screen(image, image.convert('L'), filename)
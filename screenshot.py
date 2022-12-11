from datetime import datetime
from PIL import Image
import pyautogui as pgui
from PIL import ImageGrab
import os
from logging import getLogger

logger_child_name = 'screenshot'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded screenshot.py')

class Screen:
    def __init__(self, image, filename):
        self.original = image
        self.image = image.convert('L')
        self.filename = filename

class Screenshot:
    width = 1280
    height = 720
    region = None

    def find(self, target):
        image = ImageGrab.grab(all_screens=True)
        return pgui.locate(target, image, grayscale=True)

    def shot(self):
        image = ImageGrab.grab(all_screens=True)
        if self.region is not None:
            image = image.crop(self.region)
        image = image.convert('RGBA')

        now = datetime.now()
        filename = f"{now.strftime('%Y%m%d-%H%M%S-%f')}.png"

        return Screen(image, filename)
    
    def open(self, filepath):
        if not os.path.exists(filepath):
            return None
        
        image = Image.open(filepath)
        filename = os.path.basename(filepath)

        return Screen(image, filename)

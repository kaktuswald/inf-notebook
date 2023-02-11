from datetime import datetime
from PIL import Image
import pyautogui as pgui
from PIL import ImageGrab
import os
from logging import getLogger

logger_child_name = 'screenshot'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded screenshot.py')

from define import define
from resources import find_images
from recog import recog

class Screen:
    def __init__(self, image, filename):
        self.original = image
        self.image = image.convert('L')
        self.filename = filename

class Screenshot:
    width = 1280
    height = 720
    region = None
    screen_search_keyindex = 0

    def find(self):
        image = ImageGrab.grab(all_screens=True)
        key = [*define.screen_areas.keys()][self.screen_search_keyindex]
        box =  pgui.locate(find_images[key], image, grayscale=True)
        if box is None:
            self.screen_search_keyindex = (self.screen_search_keyindex + 1) % len(define.screen_areas.keys())
            return False

        left = box.left - define.screen_areas[key][0]
        top = box.top - define.screen_areas[key][1]
        self.region = (
            left,
            top,
            left + self.width,
            top + self.height
        )
        self.region_loading = (
            left + define.screen_areas['loading'][0],
            top + define.screen_areas['loading'][1],
            left + define.screen_areas['loading'][2],
            top + define.screen_areas['loading'][3]
        )
        self.region_turntables = {}
        for key in define.areas['turntable'].keys():
            self.region_turntables[key] = (
                left + define.areas['turntable'][key][0],
                top + define.areas['turntable'][key][1],
                left + define.areas['turntable'][key][2],
                top + define.areas['turntable'][key][3]
            )
        self.region_trigger = (
            left + define.areas['trigger'][0],
            top + define.areas['trigger'][1],
            left + define.areas['trigger'][2],
            top + define.areas['trigger'][3]
        )

        return True

    @property
    def is_loading(self):
        image = ImageGrab.grab(all_screens=True)
        image = image.crop(self.region_loading)
        image = image.convert('L')
        return recog.loading.find(image)

    @property
    def is_ended_waiting(self):
        image = ImageGrab.grab(all_screens=True)
        for key in define.areas['turntable'].keys():
            image = image.crop(self.region_turntables[key])
            image = image.convert('L')
            if recog.turntable.find(image):
                return True
        return False

    def shot(self):
        image = ImageGrab.grab(all_screens=True)
        if self.region is not None:
            image = image.crop(self.region)

        return image.convert('RGBA')

    def get_resultscreen(self):
        image = ImageGrab.grab(all_screens=True)
        cropped = image.crop(self.region_trigger)
        cropped = cropped.convert('L')
        if not recog.trigger.find(cropped):
            return None

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

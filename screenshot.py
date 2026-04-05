from datetime import datetime
from os.path import exists,basename
from logging import getLogger

from PIL import Image
import numpy as np
from numpy import ndarray,uint64
from dxcam import create as create_camera
from dxcam import DXCamera

logger_child_name = 'screenshot'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded screenshot.py')

from define import define
from resources import load_resource_serialized

class Screen:
    def __init__(self, np_value:ndarray, filename:str):
        self.np_value = np_value

        self.original = Image.fromarray(np_value)
        self.filename = filename

class Screenshot:
    screentable: dict = load_resource_serialized('get_screen')
    np_value: ndarray | None = None
    camera: DXCamera | None = None

    def __init__(self):
        self.checkscreens: list[tuple[str|tuple[slice]|uint64]] = []
        for screenname, areas in define.screens.items():
            slices = (
                slice(areas['top'], areas['top'] + areas['height']),
                slice(areas['left'], areas['left'] + areas['width']),
            )
            self.checkscreens.append((screenname, slices, self.screentable[screenname],))

    def create_camera(self, idx:int):
        self.camera = create_camera(output_idx=idx, processor_backend='numpy')
        self.camera.start()
    
    def clear_camera(self):
        if self.camera is not None:
            self.camera.release()
        self.camera = None
    
    def shot(self) -> bool:
        if self.camera is None:
            return False
        
        self.np_value = self.camera.grab()
        return self.np_value is not None

    def get_screen(self) -> str|None:
        if self.np_value is None:
            return None
        
        results = []
        for screen, slices, value in self.checkscreens:
            if np.sum(self.np_value[slices]) == value:
                results.append(screen)
        
        if len(results) != 1:
            return None

        return results[0]

    def is_black(self) -> bool|None:
        if self.np_value is None:
            return None
        
        return bool(np.all(self.np_value == 0))

    def get_image(self) -> Image.Image|None:
        if self.np_value is None:
            return None
        
        return Image.fromarray(self.np_value)
    
    def get_resultscreen(self) -> Screen:
        now = datetime.now()
        filename = f"{now.strftime('%Y%m%d-%H%M%S-%f')}.png"

        return Screen(self.np_value, filename)

def open_screenimage(filepath:str) -> Screen:
    if not exists(filepath):
        return None
    
    image = Image.open(filepath).convert('RGB')
    filename = basename(filepath)

    return Screen(np.array(image, dtype=np.uint8), filename)


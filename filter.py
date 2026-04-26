from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {__name__}')

from PIL import ImageFilter
from PIL.Image import Image

from define import Playsides,ResultTabs,define
from resources import resource

class StampDefine():
    SIZE: int = 800
    MARGIN_LEFTRIGHT: int = 10
    TOP: int = 264

    def __init__(self):
        self.positions = {
            '1P': (StampDefine.MARGIN_LEFTRIGHT, StampDefine.TOP),
            '2P': (define.width - StampDefine.MARGIN_LEFTRIGHT - StampDefine.SIZE, StampDefine.TOP),
        }

        stampimage = resource.image_stamp.resize((StampDefine.SIZE, StampDefine.SIZE))
        *_, alpha = stampimage.split()
        alpha = alpha.point(lambda a: int(a * 0.3))
        stampimage.putalpha(alpha)

        self.stampimage = stampimage

stampdefine = StampDefine()

def blur(image, area):
    cropped = image.crop(area)
    blured = cropped.filter(ImageFilter.GaussianBlur(10))
    image.paste(blured, (area[:2]))

    return image

def filter(image, playside, tab, loveletter, rivalname, compact, nonfilterrankposition):
    '''適切な位置にぼかしを入れる

    ライバル順位と、必要があれば挑戦状・グラフターゲットのライバル名にぼかしを入れる。

    Args:
        image (Image): 対象の画像(PIL)
        playside (str): 1P or 2P
        tab (str|None): 表示タブ
        loveletter (bool): ライバル挑戦状の有無
        rivalname (bool): グラフターゲットのライバル名の有無
        compact (bool): ぼかしの範囲を最小限にする
        nonfilterrankposition (int): ぼかしを入れない順位位置

    Returns:
        Image: ぼかしを入れた画像
    '''
    ret = image.copy()

    # プレイサイドが不明の場合はフィルタ加工できない しょうがない
    # タブが不明の場合はとりあえずフィルタ加工する しょうがない
    if tab in [None, ResultTabs.RIVAL] and playside != '':
        if not compact:
            ret = blur(ret, define.filter_areas['ranking'][playside])
        else:
            for pos in range(1, len(define.filter_areas['ranking_compact'][playside])+1):
                if pos != nonfilterrankposition:
                    ret = blur(ret, define.filter_areas['ranking_compact'][playside][pos-1])
        
        if rivalname:
            ret = blur(ret, define.filter_areas['graphtarget_name'][playside])

    if loveletter:
        if not compact:
            ret = blur(ret, define.filter_areas['loveletter'])
        else:
            ret = blur(ret, define.filter_areas['loveletter_compact'])
    
    return ret

def stamp(image: Image, playside: str):
    '''リザルト画像にスタンプを押す

    リザルト画像にライバル欄を隠すために画像を重ねる。
    元画像を予め透過画像に変換しておく必要がある。

    Args:
        image (Image): 対象の画像(PIL)
        playside (str): 1P or 2P
        stampimage: (Image): スタンプ画像(PIL)
    Returns:
        (Image): スタンプを押した画像
    '''
    if not playside in Playsides.values:
        return None

    ret = image.copy()

    ret.paste(
        stampdefine.stampimage,
        stampdefine.positions[playside],
        stampdefine.stampimage,
    )

    return ret

def filter_overlay(image: Image, playside: str, tab: str, loveletter: bool, rivalname: bool, settings: dict):
    '''リザルト画像に各種ライバル隠し用の画像を重ねる

    Args:
        image (Image): 対象の画像(PIL)
        playside (str): 1P or 2P
        tab (str|None): 表示タブ
        loveletter (bool): ライバル挑戦状の有無
        rivalname (bool): グラフターゲットのライバル名の有無
        settings: オーバーレイ設定
    
    Returns:
        Image: 結果の画像
    '''
    ret = image.convert('RGBA')
    
    if loveletter and 'loveletter' in settings.keys():
        position = (
            define.overlay['loveletter']['position'][0] + settings['loveletter']['offset'][0],
            define.overlay['loveletter']['position'][1] + settings['loveletter']['offset'][1],
        )
        ret.paste(
            settings['loveletter']['image'],
            position,
            settings['loveletter']['image'],
        )

    # プレイサイドが不明の場合はフィルタ加工できない しょうがない
    # タブが不明の場合はとりあえずフィルタ加工する しょうがない
    if playside == '' or not tab in [ResultTabs.RIVAL, None]:
        return ret.convert('RGB')
    
    if 'rival' in settings.keys():
        position = (
            define.overlay['rival']['positions'][playside][0] + settings['rival']['offset'][0],
            define.overlay['rival']['positions'][playside][1] + settings['rival']['offset'][1],
        )
        ret.paste(
            settings['rival']['image'],
            position,
            settings['rival']['image'],
        )
    
    if rivalname and 'rivalname' in settings.keys():
        position = (
            define.overlay['rivalname']['positions'][playside][0] + settings['rivalname']['offset'][0],
            define.overlay['rivalname']['positions'][playside][1] + settings['rivalname']['offset'][1],
        )
        ret.paste(
            settings['rivalname']['image'],
            position,
            settings['rivalname']['image'],
        )
    
    return ret.convert('RGB')

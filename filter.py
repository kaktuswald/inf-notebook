from PIL import ImageFilter

from define import define

def blur(image, area):
    cropped = image.crop(area)
    blured = cropped.filter(ImageFilter.GaussianBlur(10))
    image.paste(blured, (area[:2]))

    return image

def filter(image, play_side, loveletter, rivalname, compact):
    '''適切な位置にぼかしを入れる

    ライバル順位と、必要があれば挑戦状・グラフターゲットのライバル名にぼかしを入れる。

    Args:
        image (Image): 対象の画像(PIL)
        play_side (str): 1P or 2P
        loveletter (bool): ライバル挑戦状の有無
        rivalname (bool): グラフターゲットのライバル名の有無
        compact (bool): ぼかしの範囲を最小限にする

    Returns:
        Image: ぼかしを入れた画像
    '''
    ret = image.copy()

    if play_side != '':
        if not compact:
            ret = blur(ret, define.filter_areas['ranking'][play_side])
        else:
            for area in define.filter_areas['ranking_compact'][play_side]:
                ret = blur(ret, area)
        
        if rivalname:
            ret = blur(ret, define.filter_areas['graphtarget_name'][play_side])

    if loveletter:
        if not compact:
            ret = blur(ret, define.filter_areas['loveletter'])
        else:
            ret = blur(ret, define.filter_areas['loveletter_compact'])
    
    return ret

def filter_overlay(image: Image, play_side: str, loveletter: bool, rivalname: bool, settings: dict):
    '''リザルト画像に各種ライバル隠し用の画像を重ねる

    Args:
        image (Image): 対象の画像(PIL)
        play_side (str): 1P or 2P
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

    if play_side == '':
        return ret
    
    if 'rival' in settings.keys():
        position = (
            define.overlay['rival']['positions'][play_side][0] + settings['rival']['offset'][0],
            define.overlay['rival']['positions'][play_side][1] + settings['rival']['offset'][1],
        )
        ret.paste(
            settings['rival']['image'],
            position,
            settings['rival']['image'],
        )
    
    if rivalname and 'rivalname' in settings.keys():
        position = (
            define.overlay['rivalname']['positions'][play_side][0] + settings['rivalname']['offset'][0],
            define.overlay['rivalname']['positions'][play_side][1] + settings['rivalname']['offset'][1],
        )
        ret.paste(
            settings['rivalname']['image'],
            position,
            settings['rivalname']['image'],
        )
    
    return ret

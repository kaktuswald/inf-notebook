from PIL import ImageFilter

from define import define

def blur(image, area):
    cropped = image.crop(area)
    blured = cropped.filter(ImageFilter.GaussianBlur(10))
    image.paste(blured, (area[:2]))

    return image

def filter(result, image):
    """適切な位置にぼかしを入れる

    ライバル順位と、必要があれば挑戦状・グラフターゲットのライバル名にぼかしを入れる。

    Args:
        result (Result): 対象のリザルト(result.py)
        image (Image): 対象の画像(PIL)

    Returns:
        Image: ぼかしを入れた画像
    """
    ret = image.copy()

    if result.play_side != '':
        ret = blur(ret, define.filter_areas['ranking'][result.play_side])
        if result.details.graphtarget == 'rival':
            ret = blur(ret, define.filter_areas['graphtarget_name'][result.play_side])

    if result.rival:
        ret = blur(ret, define.filter_areas['loveletter'])
    
    return ret

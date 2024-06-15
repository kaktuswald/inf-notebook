from os import mkdir
from os.path import join,exists,isfile
from PIL import Image,ImageFont,ImageDraw
from PIL.ImageFont import FreeTypeFont
from datetime import datetime
import re

from define import define
from resources import resource,images_resourcecheck_filepath,images_imagenothing_filepath,images_loading_filepath
from export import export_dirname
from windows import openfolder

dirname_results = 'results'
dirname_filtereds = 'filtered'
dirname_graphs = 'graphs'
dirname_scoreinformations = 'scoreinformations'

export_filename_summary = 'summary.png'
export_filename_musicinformation = 'musicinformation.png'

adjust_length = 94

background = (0, 0, 0, 0)
textcolor = (255, 255, 255, 255)
strokecolor = (0, 0, 0, 255)
colors_difficulty = {
    'BEGINNER': (0, 255, 0, 255),
    'NORMAL': (0, 0, 255, 255),
    'HYPER': (208, 208, 0, 255),
    'ANOTHER': (255, 0, 0, 255),
    'LEGGENDARIA': (208, 0, 208, 255)
}

image = Image.new("RGBA", (1280, 720), background)
draw = ImageDraw.Draw(image)

font_title = ImageFont.truetype('Resources/Fonts/gomarice_mukasi_mukasi.ttf', 80)
font_musicname = ImageFont.truetype('Resources/Fonts/hanazomefont.ttf', 80)
font = ImageFont.truetype('Resources/Fonts/gomarice_mukasi_mukasi.ttf', 48)
font_small = ImageFont.truetype('Resources/Fonts/gomarice_mukasi_mukasi.ttf', 36)
font_moresmall = ImageFont.truetype('Resources/Fonts/gomarice_mukasi_mukasi.ttf', 22)

musicinformation_keys = ['score', 'miss_count']

titles = {
    False: 'Number achieved.',
    True: 'Number recorded.'
}

summarytypes = {'cleartypes': 'クリアタイプ', 'djlevels': 'DJレベル'}
summarytypes_xpositions = {'cleartypes': (250, 650), 'djlevels': (740, 950)}
playmode_xposition = 50
level_xposition = 200
total_xposition = 1150
nodata_xposition = 1230

text_resourcecheck = '最新データチェック中'
text_imagenothing = '画像なし'
text_loading_title = 'インフィニタス ローディング'
text_loading_message = '30秒ごとにローディングの状況をチェックします'

def generate_filename(music, timestamp, scoretype=None, musicname_right=False, imgtype='jpg'):
    """保存ファイル名を作る

    Args:
        music (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.

    Returns:
        str: ファイル名
    """
    if scoretype is not None and scoretype['playmode'] is not None and scoretype['difficulty'] is not None:
        st = f"[{scoretype['playmode']}{scoretype['difficulty'][0]}]"
    else:
        st = ''

    if music is None:
        return f'{timestamp}{st}.{imgtype}'

    music_convert=re.sub(r'[\\|/|:|*|?|.|"|<|>|/|]', '', music)
    adjustmented = music_convert if len(music_convert) < adjust_length else f'{music_convert[:adjust_length]}..'
    if not musicname_right:
        return f'{adjustmented}{st}_{timestamp}.{imgtype}'
    else:
        return f'{timestamp}_{adjustmented}{st}.{imgtype}'

def save_resultimage(image, music, timestamp, destination_dirpath, scoretype, musicname_right=False):
    """リザルト画像をファイル保存する

    Args:
        image (Image): 対象の画像(PIL.Image)
        music (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        scoretype (dict): プレイモードと譜面難易度
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.

    Returns:
        str: 成功した場合はファイル名を返す
    """
    return save_image(image, music, timestamp, destination_dirpath, dirname_results, scoretype, musicname_right)

def save_resultimage_filtered(image, music, timestamp, destination_dirpath, scoretype, musicname_right=False):
    """ライバル欄にぼかしを入れたリザルト画像をファイル保存する

    Args:
        image (Image): 対象の画像(PIL.Image)
        music (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        scoretype (dict): プレイモードと譜面難易度
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.

    Returns:
        str: 成功した場合はファイル名を返す
    """
    return save_image(image, music, timestamp, destination_dirpath, dirname_filtereds, scoretype, musicname_right)

def save_scoreinformationimage(image, music, destination_dirpath, scoretype, musicname_right=False):
    """譜面記録情報をファイルに保存する

    Args:
        image (Image): 対象の画像
        music (str): 曲名
        scoretype (dict): プレイモードと譜面難易度
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.
    """
    now = datetime.now()
    timestamp = f"{now.strftime('%Y%m%d-%H%M%S')}"

    return save_image(image.convert('RGB'), music, timestamp, destination_dirpath, dirname_scoreinformations, scoretype, musicname_right)

def save_graphimage(image, music, destination_dirpath, scoretype, musicname_right=False):
    """グラフ画像をファイルに保存する

    Args:
        image (Image): 対象の画像
        music (str): 曲名
        scoretype (dict): プレイモードと譜面難易度
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.
    """
    now = datetime.now()
    timestamp = f"{now.strftime('%Y%m%d-%H%M%S')}"

    return save_image(image.convert('RGBA'), music, timestamp, destination_dirpath, dirname_graphs, scoretype, musicname_right, imgtype='png')

def save_image(image, music, timestamp, destination_dirpath, target_dirname, scoretype, musicname_right=False, imgtype='jpg'):
    """画像をファイル保存する

    Args:
        image (Image): 対象の画像(PIL.Image)
        music (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        target_dirname (str): 保存先の子ディレクトリ名
        scoretype (dict): プレイモードと譜面難易度
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.

    Returns:
        str: 成功した場合はファイル名を返す
    """
    if not exists(destination_dirpath):
        mkdir(destination_dirpath)

    dirpath = join(destination_dirpath, target_dirname)
    if not exists(dirpath):
        mkdir(dirpath)

    filename = generate_filename(music, timestamp, scoretype, musicname_right, imgtype)
    filepath = join(dirpath, filename)
    if exists(filepath):
        return None
    
    image.save(filepath)

    return filename

def get_resultimage(music, timestamp, destination_dirpath, scoretype):
    """リザルト画像をファイルから取得する

    最も古い形式はタイムスタンプのみのファイル名。
    曲名がファイル名の左側にあるときも右側にあるときもある。
    全パターンでファイルの有無を確認する。

    Args:
        music (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        scoretype (dict): プレイモードと譜面難易度

    Returns:
        bytes: PySimpleGUIに渡すデータ
    """
    return load_image(music, timestamp, destination_dirpath, dirname_results, scoretype)

def get_resultimage_filtered(music, timestamp, destination_dirpath, scoretype):
    """ぼかしの入ったリザルト画像をファイルから取得する

    Args:
        music (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        scoretype (dict): プレイモードと譜面難易度

    Returns:
        bytes: PySimpleGUIに渡すデータ
    """
    return load_image(music, timestamp, destination_dirpath, dirname_filtereds, scoretype)

def load_image(music, timestamp, destination_dirpath, target_dirname, scoretype):
    """ぼかしの入ったリザルト画像をファイルから取得する

    Args:
        music (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        target_dirname (str): 保存先の子ディレクトリ名
        scoretype (dict): プレイモードと譜面難易度

    Returns:
        bytes: PySimpleGUIに渡すデータ
    """
    dirpath = join(destination_dirpath, target_dirname)

    for st in [scoretype, None]:
        for musicname_right in [True, False]:
            filename = generate_filename(music, timestamp, musicname_right=musicname_right, scoretype=st)
            filepath = join(dirpath, filename)
            if isfile(filepath):
                return Image.open(filepath)
        
        filename = generate_filename(None, timestamp, scoretype=st)
        filepath = join(dirpath, filename)
        if isfile(filepath):
            return Image.open(filepath)
    
    return None

def generateimage_summary(counts, setting, countmethod_only):
    """
    統計データ画像を作る

    Args:
        counts (dict): カウントデータ
        setting (dict): 出力対象の設定
        countmethod_only (bool): カウント方式
            Falseの場合は達成している曲数をすべて計上する
            Trueの場合は一致する曲数のみ計上する
    """
    if resource.musictable is None:
        return
    if counts is None:
        return
    
    draw.rectangle((0, 0, 1280, 720), fill=background)
    drawtext((20, 20), titles[countmethod_only], font_title, textcolor)

    drawtext((summarytypes_xpositions['cleartypes'][1], 150), 'CLEAR TYPE', font, textcolor, 'ra')
    drawtext((summarytypes_xpositions['djlevels'][1], 150), 'DJ LEVEL', font, textcolor, 'ra')
    drawtext((total_xposition, 150), 'TOTAL', font, textcolor, 'ra')
    drawtext((nodata_xposition, 150), 'NO', font_moresmall, textcolor, 'ra')
    drawtext((nodata_xposition, 150+25), 'DATA', font_moresmall, textcolor, 'ra')

    result = {}
    for playmode in setting.keys():
        result[playmode] = {}
        for level in setting[playmode].keys():
            result[playmode][level] = {'TOTAL': counts[playmode][level]['total']}
            values = counts[playmode][level]
            for summarykey, targetkey in [('cleartypes', 'clear_types'), ('djlevels', 'dj_levels')]:
                result[playmode][level][summarykey] = {}
                for key in setting[playmode][level][summarykey]:
                    value = values[key]
                    if not countmethod_only:
                        index = define.value_list[targetkey].index(key)
                        result[playmode][level][summarykey][key] = sum([values[k] for k in define.value_list[targetkey][index:]])
                    else:
                        result[playmode][level][summarykey][key] = counts[playmode][level][key]

    line = 0
    for playmode in result.keys():
        for level in result[playmode].keys():
            levelcount = max([len(v) for k, v in result[playmode][level].items() if k != 'TOTAL'])
            items = {}
            for summarytype in summarytypes.keys():
                items[summarytype] = [*result[playmode][level][summarytype].items()] if summarytype in result[playmode][level].keys() else []
            total = len(resource.musictable['levels'][playmode][level])
            total_str = str(total)
            nodatacount = total - counts[playmode][level]['datacount']
            nodatacount_str = f'({nodatacount})' if nodatacount > 0 else ''

            for index in range(levelcount):
                drawtext((playmode_xposition, line*50+200), playmode, font, textcolor)
                drawtext((level_xposition, line*50+200), level, font, textcolor, 'ra')

                for summarytype in summarytypes.keys():
                    if index >= len(items[summarytype]) or not summarytype in result[playmode][level].keys():
                        continue

                    key, value = items[summarytype][index]

                    drawtext((summarytypes_xpositions[summarytype][0], line*50+200), key, font, textcolor)
                    drawtext((summarytypes_xpositions[summarytype][1], line*50+200), str(value), font, textcolor, 'ra')

                drawtext((total_xposition, line*50+200), total_str, font, textcolor, 'ra')
                drawtext((nodata_xposition, line*50+220), nodatacount_str, font_moresmall, textcolor, 'ra')

                line += 1

    save_exportimage(image, export_filename_summary)

    return image

def generateimage_musicinformation(playmode, difficulty, musicname, record):
    draw.rectangle((0, 0, 1280, 720), fill=background)

    drawtext_width_adjustment((20, 10), musicname, 1240, font_musicname, textcolor)
    drawtext((50, 100), f'{playmode} {difficulty}', font, colors_difficulty[difficulty])

    if 'timestamps' in record.keys():
        count = str(len(record['timestamps']))
        drawtext((20, 170), 'Played count.', font, textcolor)
        drawtext((680, 140), count, font_title, textcolor)

    if 'latest' in record.keys():
        drawtext((20, 260), 'Last time played.', font, textcolor)
        drawtext((500, 230), record['latest']['timestamp'], font_title, textcolor)

    if 'best' in record.keys():
        drawtext((20, 330), 'Options when update a new record.', font, textcolor)
        for keyindex in range(len(musicinformation_keys)):
            key = musicinformation_keys[keyindex]
            drawtext((50, keyindex*90+390), str.upper(key.replace('_', ' ')), font_title, textcolor)

            if not key in record['best'].keys() or record['best'][key] is None:
                break

            value = str(record['best'][key]['value'])
            drawtext((750, keyindex*90+390), value, font_title, textcolor, 'ra')

            has_options = 'options' in record['best'][key].keys() and record['best'][key]['options'] is not None
            if has_options and 'arrange' in record['best'][key]['options'].keys():
                arrange = record['best'][key]['options']['arrange']
                drawtext((800, keyindex*90+390), arrange if arrange is not None else '-----', font_title, textcolor)
            else:
                drawtext((800, keyindex*90+390), '?????', font_title, textcolor)

    keys1 = {'fixed': 'FIXED', 'S-RANDOM': 'S-RANDOM', 'DBM': 'DBM'}
    if 'achievement' in record.keys():
        drawtext((20, 570), 'Achievement status for each options.', font, textcolor)
        index1 = 0
        for key1 in keys1.keys():
            index2 = 0
            if playmode == 'SP' and key1 == 'DBM':
                continue
            drawtext(((index1+0.5)*380+50, 630), keys1[key1], font_small, textcolor, 'ma')
            for key2 in ['clear_type', 'dj_level']:
                value = record['achievement'][key1][key2]
                if value is None:
                    continue
                drawtext((index1*380+index2*240+100, 670), value, font_small, textcolor)
                index2 += 1
            index1 += 1
        
    save_exportimage(image, export_filename_musicinformation)

    return image

def generateimage_musictableinformation():
    draw.rectangle((0, 0, 1280, 720), fill=background)

    xpositions = {'SP': 950, 'DP': 1200}
    musiccount = len(resource.musictable['musics'])

    drawtext((380, 100), '全曲数', font_title, textcolor)
    drawtext((900, 100), f'{musiccount}', font_title, textcolor, 'ra')

    drawtext((80, 350), '全譜面数', font_title, textcolor)
    drawtext((80, 450), 'ビギナー譜面数', font_title, textcolor)
    drawtext((80, 550), 'レジェンダリア譜面数', font_title, textcolor)

    for playmode in define.value_list['play_modes']:
        drawtext((xpositions[playmode], 250), playmode, font_title, textcolor, 'ra')

        scorecount = sum([len(music[playmode]) for music in resource.musictable['musics'].values()])
        drawtext((xpositions[playmode], 350), f'{scorecount}', font_title, textcolor, 'ra')

        if playmode == 'SP':
            beginnercount = len(resource.musictable['beginners'])
            drawtext((xpositions[playmode], 450), f'{beginnercount}', font_title, textcolor, 'ra')

        leggendariacount = len(resource.musictable['leggendarias'][playmode])
        drawtext((xpositions[playmode], 550), f'{leggendariacount}', font_title, textcolor, 'ra')

    return image

def generateimage_simple(message, filepath):
    font = ImageFont.truetype('Resources/Fonts/gomarice_mukasi_mukasi.ttf', 160)

    draw.rectangle((0, 0, 1280, 720), fill=background)
    drawtext((640, 360), message, font, textcolor, 'mm')

    image.save(filepath)

def generateimage_multiline(title, message, filepath):
    font_title = ImageFont.truetype('Resources/Fonts/gomarice_mukasi_mukasi.ttf', 120)
    font_message = ImageFont.truetype('Resources/Fonts/gomarice_mukasi_mukasi.ttf', 60)

    draw.rectangle((0, 0, 1280, 720), fill=background)
    drawtext((640, 260), title, font_title, textcolor, 'mm')
    drawtext((640, 460), message, font_message, textcolor, 'mm')

    image.save(filepath)

def drawtext(position: tuple[int, int], text: str, font: FreeTypeFont, color: str, anchor: str=None):
    draw.multiline_text(
        position,
        text,
        fill=color,
        stroke_width=font.size // 10,
        stroke_fill=strokecolor,
        font=font,
        anchor=anchor
    )

def drawtext_width_adjustment(position: tuple[int, int], text: str, maxwidth: int, font: FreeTypeFont, color: str):
    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        stroke_width=font.size // 10,
        font=font
    )

    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    textimage = Image.new("RGBA", (width, height), background)
    textdraw = ImageDraw.Draw(textimage)
    textdraw.multiline_text(
        (-bbox[0], -bbox[1]),
        text,
        fill=color,
        stroke_width=font.size // 10,
        stroke_fill=strokecolor,
        font=font
    )
    if width < maxwidth:
        image.paste(textimage, position)
    else:
        resized = textimage.resize((maxwidth, height))
        image.paste(resized, (position[0]+bbox[0], position[1]+bbox[1]))

def save_exportimage(image, filename):
    """エクスポートフォルダに画像ファイルを保存する

    Args:
        image (Image): 対象の画像
        filename (str): ファイル名
    """
    image.save(join(export_dirname, filename))

def openfolder_results(destination_dirpath):
    dirpath = join(destination_dirpath, dirname_results)
    return openfolder(dirpath)

def openfolder_filtereds(destination_dirpath):
    dirpath = join(destination_dirpath, dirname_filtereds)
    return openfolder(dirpath)

def openfolder_graphs(destination_dirpath):
    dirpath = join(destination_dirpath, dirname_graphs)
    return openfolder(dirpath)

def openfolder_scoreinformations(destination_dirpath):
    dirpath = join(destination_dirpath, dirname_scoreinformations)
    return openfolder(dirpath)

def openfolder_export():
    return openfolder(export_dirname)

if __name__ == '__main__':
    generateimage_simple(text_resourcecheck, images_resourcecheck_filepath)
    generateimage_simple(text_imagenothing, images_imagenothing_filepath)
    generateimage_multiline(text_loading_title, text_loading_message, images_loading_filepath)

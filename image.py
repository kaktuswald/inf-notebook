from os import mkdir
from os.path import join,exists,isfile
from PIL import Image,ImageFont,ImageDraw
from datetime import datetime
import re

from define import define
from resources import resource,images_resourcecheck_filepath,images_imagenothing_filepath,images_loading_filepath
from export import export_dirname

dirname_results = 'results'
dirname_filtereds = 'filtered'
dirname_graphs = 'graphs'
dirname_scoreinformations = 'scoreinformations'

export_filename_summary = 'summary.png'
export_filename_musicinformation = 'musicinformation.png'

adjust_length = 94

background = (0, 0, 0, 128)
textcolor = (255, 255, 255, 255)
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

def generate_filename(music, timestamp, scoretype=None, musicname_right=False):
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
        return f'{timestamp}{st}.jpg'

    music_convert=re.sub(r'[\\|/|:|*|?|.|"|<|>|/|]', '', music)
    adjustmented = music_convert if len(music_convert) < adjust_length else f'{music_convert[:adjust_length]}..'
    if not musicname_right:
        return f'{adjustmented}{st}_{timestamp}.jpg'
    else:
        return f'{timestamp}_{adjustmented}{st}.jpg'

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

    return save_image(image.convert('RGB'), music, timestamp, destination_dirpath, dirname_graphs, scoretype, musicname_right)

def save_image(image, music, timestamp, destination_dirpath, target_dirname, scoretype, musicname_right=False):
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

    filename = generate_filename(music, timestamp, scoretype, musicname_right)
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
    draw.multiline_text((20, 20), 'Number of goals achieved.', fill=textcolor, font=font_title)

    bbox = draw.multiline_textbbox((0, 0), 'CLEAR TYPE', font=font)
    draw.multiline_text((summarytypes_xpositions['cleartypes'][1] - bbox[2], 150), 'CLEAR TYPE', fill=textcolor, font=font)

    bbox = draw.multiline_textbbox((0, 0), 'DJ LEVEL', font=font)
    draw.multiline_text((summarytypes_xpositions['djlevels'][1] - bbox[2], 150), 'DJ LEVEL', fill=textcolor, font=font)

    bbox = draw.multiline_textbbox((0, 0), 'TOTAL', font=font)
    draw.multiline_text((total_xposition - bbox[2], 150), 'TOTAL', fill=textcolor, font=font)

    bbox = draw.multiline_textbbox((0, 0), 'NO', font=font_moresmall)
    draw.multiline_text((nodata_xposition - bbox[2], 150), 'NO', fill=textcolor, font=font_moresmall)
    bbox = draw.multiline_textbbox((0, 0), 'DATA', font=font_moresmall)
    draw.multiline_text((nodata_xposition - bbox[2], 150+25), 'DATA', fill=textcolor, font=font_moresmall)

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
                draw.multiline_text((playmode_xposition, line*50+200), playmode, fill=textcolor, font=font)
                
                bbox = draw.multiline_textbbox((0, 0), level, font=font)
                draw.multiline_text((level_xposition-bbox[2], line*50+200), level, fill=textcolor, font=font)

                for summarytype in summarytypes.keys():
                    if index >= len(items[summarytype]) or not summarytype in result[playmode][level].keys():
                        continue

                    key, value = items[summarytype][index]

                    draw.multiline_text((summarytypes_xpositions[summarytype][0], line*50+200), key, fill=textcolor, font=font)
                    bbox = draw.multiline_textbbox((0, 0), str(value), font=font)
                    draw.multiline_text((summarytypes_xpositions[summarytype][1]-bbox[2], line*50+200), str(value), fill=textcolor, font=font)

                bbox = draw.multiline_textbbox((0, 0), total_str, font=font)
                draw.multiline_text((total_xposition-bbox[2], line*50+200), total_str, fill=textcolor, font=font)

                bbox = draw.multiline_textbbox((0, 0), nodatacount_str, font=font_moresmall)
                draw.multiline_text((nodata_xposition-bbox[2], line*50+220), nodatacount_str, fill=textcolor, font=font_moresmall)

                line += 1

    save_exportimage(image, export_filename_summary)

    return image

def generateimage_musicinformation(playmode, difficulty, musicname, record):
    draw.rectangle((0, 0, 1280, 720), fill=background)

    bbox = draw.multiline_textbbox((0, 0), musicname, font=font_musicname)
    if bbox[2] >= 1240:
        musicnameimage = Image.new("RGBA", (bbox[2], 100), background)
        musicnamedraw = ImageDraw.Draw(musicnameimage)
        musicnamedraw.multiline_text((0, 0), musicname, font=font_musicname)
        resized = musicnameimage.resize((1240, 100))
        image.paste(resized, (20, 10))
    else:
        draw.multiline_text((20, 10), musicname, fill=textcolor, font=font_musicname)
    draw.multiline_text((50, 100), f'{playmode} {difficulty}', fill=colors_difficulty[difficulty], font=font)

    if 'timestamps' in record.keys():
        count = str(len(record['timestamps']))
        draw.multiline_text((20, 170), 'Played count.', fill=textcolor, font=font)
        bbox = draw.multiline_textbbox((0, 0), count, font=font_title)
        draw.multiline_text((680-bbox[2], 140), count, fill=textcolor, font=font_title)

    if 'latest' in record.keys():
        draw.multiline_text((20, 260), 'Last time played.', fill=textcolor, font=font)
        draw.multiline_text((500, 230), record['latest']['timestamp'], fill=textcolor, font=font_title)

    if 'best' in record.keys():
        draw.multiline_text((20, 330), 'Options when update a new record.', fill=textcolor, font=font)
        for keyindex in range(len(musicinformation_keys)):
            key = musicinformation_keys[keyindex]
            draw.multiline_text((50, keyindex*90+390), str.upper(key.replace('_', ' ')), fill=textcolor, font=font_title)

            if not key in record['best'].keys() or record['best'][key] is None:
                break

            value = str(record['best'][key]['value'])
            bbox = draw.multiline_textbbox((0, 0), value, font=font_title)
            draw.multiline_text((750-bbox[2], keyindex*90+390), value, fill=textcolor, font=font_title)

            has_options = 'options' in record['best'][key].keys() and record['best'][key]['options'] is not None
            if has_options and 'arrange' in record['best'][key]['options'].keys():
                arrange = record['best'][key]['options']['arrange']
                draw.multiline_text((800, keyindex*90+390), arrange if arrange is not None else '-----', fill=textcolor, font=font_title)
            else:
                draw.multiline_text((800, keyindex*90+390), '?????', fill=textcolor, font=font_title)

    keys1 = {'fixed': 'FIXED', 'S-RANDOM': 'S-RANDOM', 'DBM': 'DBM'}
    if 'achievement' in record.keys():
        draw.multiline_text((20, 570), 'Achievement status for each options.', fill=textcolor, font=font)
        index1 = 0
        for key1 in keys1.keys():
            index2 = 0
            if playmode == 'SP' and key1 == 'DBM':
                continue
            bbox = draw.multiline_textbbox((0, 0), keys1[key1], font=font_small)
            draw.multiline_text(((index1+0.5)*380-bbox[2]/2+50, 630), keys1[key1], fill=textcolor, font=font_small)
            for key2 in ['clear_type', 'dj_level']:
                value = record['achievement'][key1][key2]
                if value is None:
                    continue
                draw.multiline_text((index1*380+index2*240+100, 670), value, fill=textcolor, font=font_small)
                index2 += 1
            index1 += 1
        
    save_exportimage(image, export_filename_musicinformation)

    return image

def generateimage_simple(message, filepath):
    font = ImageFont.truetype('Resources/Fonts/gomarice_mukasi_mukasi.ttf', 160)

    draw.rectangle((0, 0, 1280, 720), fill=background)

    bbox = draw.multiline_textbbox((0, 0), message, font=font)
    draw.multiline_text((640-bbox[2]/2, 360-bbox[3]/2), message, fill=textcolor, font=font)

    image.save(filepath)

def generateimage_multiline(title, message, filepath):
    font_title = ImageFont.truetype('Resources/Fonts/gomarice_mukasi_mukasi.ttf', 120)
    font_message = ImageFont.truetype('Resources/Fonts/gomarice_mukasi_mukasi.ttf', 60)

    draw.rectangle((0, 0, 1280, 720), fill=background)

    bbox = draw.multiline_textbbox((0, 0), title, font=font_title)
    draw.multiline_text((640-bbox[2]/2, 260-bbox[3]/2), title, fill=textcolor, font=font_title)

    bbox = draw.multiline_textbbox((0, 0), message, font=font_message)
    draw.multiline_text((640-bbox[2]/2, 460-bbox[3]/2), message, fill=textcolor, font=font_message)

    image.save(filepath)

def save_exportimage(image, filename):
    """エクスポートフォルダに画像ファイルを保存する

    Args:
        image (Image): 対象の画像
        filename (str): ファイル名
    """
    image.save(join(export_dirname, filename))

if __name__ == '__main__':
    generateimage_simple(text_resourcecheck, images_resourcecheck_filepath)
    generateimage_simple(text_imagenothing, images_imagenothing_filepath)
    generateimage_multiline(text_loading_title, text_loading_message, images_loading_filepath)

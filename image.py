from os import mkdir
from os.path import join,exists,isfile
from PIL import Image
from datetime import datetime
from pathlib import Path
import re

from export import export_dirname
from windows import openfolder
from general import get_imagevalue

dirname_results = 'results'
dirname_filtereds = 'filtered'
dirname_scorecharts = 'graphs'
dirname_scoreinformations = 'scoreinformations'

export_filename_summary = 'summary.png'
export_filename_musicinformation = 'musicinformation.png'

adjust_length = 94

class ResultImages():
    destination_path: Path = None
    resultimages: dict[str, bytes]
    filteredimages: dict[str, bytes]

    def get_resultimage(self, musicname: str, difficulty: str, playmode: str, timestamp: str):
        scoretype = {'playmode': playmode, 'difficulty': difficulty}
        if self.destination_path is not None and not timestamp in self.resultimages.keys():
            image = get_resultimage(musicname, timestamp, self.destination_path, scoretype)
            self.resultimages[timestamp] = get_imagevalue(image)
            del image
        if timestamp in self.resultimages.keys() and self.resultimages[timestamp] is not None:
            return self.resultimages[timestamp]
        if self.destination_path is not None and not timestamp in self.filteredimages.keys():
            image = get_resultimage_filtered(musicname, timestamp, self.destination_path, scoretype)
            self.filteredimages[timestamp] = get_imagevalue(image)
            del image

def generate_filename(music, timestamp, scoretype=None, musicname_right=False, imgtype='jpg'):
    '''保存ファイル名を作る

    Args:
        music (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.

    Returns:
        str: ファイル名
    '''
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

def generate_filename2(
        playmode: str,
        musicname: str,
        difficulty: str,
        timestamp: str,
        musicname_right: bool = False,
        imgtype: str = 'jpg',
    ):
    '''保存ファイル名を作る

    Args:
        playmode (str): プレイモード(SP or DP)
        musicname (str): 曲名
        difficulty (str): 譜面難易度
        timestamp (str): リザルトを記録したときのタイムスタンプ
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.

    Returns:
        str: ファイル名
    '''
    if playmode is not None and difficulty is not None:
        st = f"[{playmode}{difficulty[0]}]"
    else:
        st = ''

    if musicname is None:
        return f'{timestamp}{st}.{imgtype}'

    music_convert = re.sub(r'[\\|/|:|*|?|.|"|<|>|/|]', '', musicname)
    adjustmented = music_convert if len(music_convert) < adjust_length else f'{music_convert[:adjust_length]}..'

    if not musicname_right:
        return f'{adjustmented}{st}_{timestamp}.{imgtype}'
    else:
        return f'{timestamp}_{adjustmented}{st}.{imgtype}'

def save_resultimage(image, music, timestamp, destination_dirpath, scoretype, musicname_right=False):
    '''リザルト画像をファイル保存する

    Args:
        image (Image): 対象の画像(PIL.Image)
        music (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        scoretype (dict): プレイモードと譜面難易度
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.

    Returns:
        str: 成功した場合はファイル名を返す
    '''
    return save_image(image, music, timestamp, destination_dirpath, dirname_results, scoretype, musicname_right)

def save_resultimage_filtered(image, music, timestamp, destination_dirpath, scoretype, musicname_right=False):
    '''ライバル欄にぼかしを入れたリザルト画像をファイル保存する

    Args:
        image (Image): 対象の画像(PIL.Image)
        music (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        scoretype (dict): プレイモードと譜面難易度
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.

    Returns:
        str: 成功した場合はファイル名を返す
    '''
    return save_image(image, music, timestamp, destination_dirpath, dirname_filtereds, scoretype, musicname_right)

def get_scoreinformationimagepath(
        playmode: str,
        musicname: str,
        difficulty: str,
        destination_dirpath: str,
        musicname_right: bool = False,
    ):
    '''譜面情報の保存先パスを取得する
    Args:
        playmode (str): プレイモード(SP or DP)
        musicname (str): 曲名
        difficulty (str): 譜面難易度
        destination_dirpath (str): 画像保存先のパス
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.
    '''
    now = datetime.now()
    timestamp = f"{now.strftime('%Y%m%d-%H%M%S')}"

    return get_filepath(
        playmode,
        musicname,
        difficulty,
        timestamp,
        destination_dirpath,
        dirname_scoreinformations,
        musicname_right,
        imgtype='png',
    )

def get_scoregraphimagepath(
        playmode: str,
        musicname: str,
        difficulty: str,
        destination_dirpath: str,
        musicname_right: bool = False,
    ):
    '''譜面グラフの保存先パスを取得する
    Args:
        playmode (str): プレイモード(SP or DP)
        musicname (str): 曲名
        difficulty (str): 譜面難易度
        destination_dirpath (str): 画像保存先のパス
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.
    '''
    now = datetime.now()
    timestamp = f"{now.strftime('%Y%m%d-%H%M%S')}"

    return get_filepath(
        playmode,
        musicname,
        difficulty,
        timestamp,
        destination_dirpath,
        dirname_scorecharts,
        musicname_right,
        imgtype='png',
    )

def save_image(image, music, timestamp, destination_dirpath, target_dirname, scoretype, musicname_right=False, imgtype='jpg'):
    '''画像をファイル保存する

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
    '''
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

def get_filepath(
        playmode: str,
        musicname: str,
        difficulty: str,
        timestamp: str,
        destination_dirpath: str,
        target_dirname: str,
        musicname_right: bool = False,
        imgtype: str = 'jpg',
    ):
    '''画像保存先のファイルパスを取得する

    Args:
        playmode (str): プレイモード(SP or DP)
        musicname (str): 曲名
        difficulty (str): 譜面難易度
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        target_dirname (str): 保存先の子ディレクトリ名
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.
    Returns:
        str: 成功した場合はファイルパスを返す
    '''
    if not exists(destination_dirpath):
        mkdir(destination_dirpath)

    dirpath = join(destination_dirpath, target_dirname)
    if not exists(dirpath):
        mkdir(dirpath)

    filename = generate_filename2(playmode, musicname, difficulty, timestamp, musicname_right, imgtype)
    filepath = join(dirpath, filename)
    
    return filepath

def get_resultimage(music, timestamp, destination_dirpath, scoretype):
    '''リザルト画像をファイルから取得する

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
    '''
    return load_image(music, timestamp, destination_dirpath, dirname_results, scoretype)

def get_resultimage_filtered(music, timestamp, destination_dirpath, scoretype):
    '''ぼかしの入ったリザルト画像をファイルから取得する

    Args:
        music (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        scoretype (dict): プレイモードと譜面難易度

    Returns:
        bytes: PySimpleGUIに渡すデータ
    '''
    return load_image(music, timestamp, destination_dirpath, dirname_filtereds, scoretype)

def load_image(music, timestamp, destination_dirpath, target_dirname, scoretype):
    '''リザルト画像をファイルから取得する

    Args:
        music (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        target_dirname (str): 保存先の子ディレクトリ名
        scoretype (dict): プレイモードと譜面難易度

    Returns:
        bytes: PySimpleGUIに渡すデータ
    '''
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

def openfolder_results(destination_dirpath):
    dirpath = join(destination_dirpath, dirname_results)
    return openfolder(dirpath)

def openfolder_filtereds(destination_dirpath):
    dirpath = join(destination_dirpath, dirname_filtereds)
    return openfolder(dirpath)

def openfolder_scorecharts(destination_dirpath):
    dirpath = join(destination_dirpath, dirname_scorecharts)
    return openfolder(dirpath)

def openfolder_scoreinformations(destination_dirpath):
    dirpath = join(destination_dirpath, dirname_scoreinformations)
    return openfolder(dirpath)

def openfolder_export():
    return openfolder(export_dirname)

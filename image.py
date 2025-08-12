from os import mkdir
from os.path import join,exists,isfile
from PIL import Image
from datetime import datetime
import re

from define import Playtypes
from export import export_dirname
from windows import openfolder

dirname_results = 'results'
dirname_filtereds = 'filtered'
dirname_scorecharts = 'graphs'
dirname_scoreinformations = 'scoreinformations'

export_filename_summary = 'summary.png'
export_filename_musicinformation = 'musicinformation.png'

adjust_length = 94

def generate_scoretype(playtype: str | None, difficulty: str | None):
    '''プレイの種類と譜面難易度を複合した3文字を作る

    Args:
        playtype (str): プレイの種類
        difficulty (str): 譜面難易度

    Returns:
        str: プレイの種類と譜面難易度を複合した3文字
    '''
    if playtype is not None and difficulty is not None:
        if playtype != Playtypes.DPBATTLE:
            return f'{playtype}{difficulty[0]}'
        else:
            return f'DB{difficulty[0]}'
    else:
        return None

def generate_filename(
        scoretype: str | None,
        musicname: str | None,
        timestamp: str,
        musicname_right: bool = False,
        filetype: str = 'jpg',
    ):
    '''保存ファイル名を作る

    Args:
        scoretype (str): プレイの種類と譜面難易度
        musicname (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.
        filetype (str, optional): ファイルの拡張子

    Returns:
        str: ファイル名
    '''
    scoretype_str = f'[{scoretype}]' if scoretype is not None else ''

    if musicname is None:
        return f'{timestamp}{scoretype_str}.{filetype}'

    music_convert = re.sub(r'[\\|/|:|*|?|.|"|<|>|/|]', '', musicname)
    adjustmented = music_convert if len(music_convert) < adjust_length else f'{music_convert[:adjust_length]}..'

    if not musicname_right:
        return f'{adjustmented}{scoretype_str}_{timestamp}.{filetype}'
    else:
        return f'{timestamp}_{adjustmented}{scoretype_str}.{filetype}'

def save_resultimage(image, playtype, musicname, difficulty, timestamp, destination_dirpath, musicname_right=False):
    '''リザルト画像をファイル保存する

    Args:
        image (Image): 対象の画像(PIL.Image)
        playtype (str): プレイの種類
        musicname (str): 曲名
        difficulty (str): 譜面難易度
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        scoretype (dict): プレイの種類と譜面難易度
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.

    Returns:
        str: 成功した場合はファイル名を返す
    '''
    return save_image(image, playtype, musicname, difficulty, timestamp, destination_dirpath, dirname_results, musicname_right)

def save_resultimage_filtered(image, playtype, musicname, difficulty, timestamp, destination_dirpath, musicname_right=False):
    '''ライバル欄にぼかしを入れたリザルト画像をファイル保存する

    Args:
        image (Image): 対象の画像(PIL.Image)
        playtype (str): プレイの種類
        musicname (str): 曲名
        difficulty (str): 譜面難易度
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        scoretype (dict): プレイの種類と譜面難易度
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.

    Returns:
        str: 成功した場合はファイル名を返す
    '''
    return save_image(image, playtype, musicname, difficulty, timestamp, destination_dirpath, dirname_filtereds, musicname_right)

def get_scoreinformationimagepath(
        scoretype: str,
        musicname: str,
        destination_dirpath: str,
        musicname_right: bool = False,
    ):
    '''譜面情報の保存先パスを取得する
    Args:
        scoretype (str): プレイの種類と譜面難易度
        musicname (str): 曲名
        destination_dirpath (str): 画像保存先のパス
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.
    '''
    now = datetime.now()
    timestamp = f"{now.strftime('%Y%m%d-%H%M%S')}"

    return get_filepath(
        scoretype,
        musicname,
        timestamp,
        destination_dirpath,
        dirname_scoreinformations,
        musicname_right,
        imgtype='png',
    )

def get_scoregraphimagepath(
        scoretype: str,
        musicname: str,
        destination_dirpath: str,
        musicname_right: bool = False,
    ):
    '''譜面グラフの保存先パスを取得する
    Args:
        scoretype (str): プレイの種類と譜面難易度
        musicname (str): 曲名
        destination_dirpath (str): 画像保存先のパス
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.
    '''
    now = datetime.now()
    timestamp = f"{now.strftime('%Y%m%d-%H%M%S')}"

    return get_filepath(
        scoretype,
        musicname,
        timestamp,
        destination_dirpath,
        dirname_scorecharts,
        musicname_right,
        imgtype='png',
    )

def save_image(image, playtype, musicname, difficulty, timestamp, destination_dirpath, target_dirname, musicname_right=False, imgtype='jpg'):
    '''画像をファイル保存する

    Args:
        image (Image): 対象の画像(PIL.Image)
        playtype (str): プレイの種類
        musicname (str): 曲名
        difficulty (str): 譜面難易度
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        target_dirname (str): 保存先の子ディレクトリ名
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.
        
    Returns:
        str: 成功した場合はファイル名を返す
    '''
    if not exists(destination_dirpath):
        mkdir(destination_dirpath)

    dirpath = join(destination_dirpath, target_dirname)
    if not exists(dirpath):
        mkdir(dirpath)

    scoretype = generate_scoretype(playtype, difficulty)
    filename = generate_filename(scoretype, musicname, timestamp, musicname_right, imgtype)
    filepath = join(dirpath, filename)
    if exists(filepath):
        return None
    
    image.save(filepath)

    return filename

def get_filepath(
        scoretype: str,
        musicname: str,
        timestamp: str,
        destination_dirpath: str,
        target_dirname: str,
        musicname_right: bool = False,
        imgtype: str = 'jpg',
    ):
    '''画像保存先のファイルパスを取得する

    Args:
        scoretype (str): プレイの種類と譜面難易度
        musicname (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        target_dirname (str): 保存先の子ディレクトリ名
        musicname_right (bool, optional): 曲名をファイル名の後尾にする. Defaults to False.
        imgtype (str, optional): 画像の種類(拡張子)

    Returns:
        str: 成功した場合はファイルパスを返す
    '''
    if not exists(destination_dirpath):
        mkdir(destination_dirpath)

    dirpath = join(destination_dirpath, target_dirname)
    if not exists(dirpath):
        mkdir(dirpath)

    filename = generate_filename(scoretype, musicname, timestamp, musicname_right, imgtype)
    filepath = join(dirpath, filename)
    
    return filepath

def get_resultimage(scoretype, musicname, timestamp, destination_dirpath):
    '''リザルト画像をファイルから取得する

    最も古い形式はタイムスタンプのみのファイル名。
    曲名がファイル名の左側にあるときも右側にあるときもある。
    全パターンでファイルの有無を確認する。

    Args:
        scoretype (str): プレイの種類(SP or DP or DP BATTLE)と譜面難易度
        musicname (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス

    Returns:
        bytes: フロントエンドに渡すデータ
    '''
    return load_image(scoretype, musicname, timestamp, destination_dirpath, dirname_results)

def get_resultimage_filtered(scoretype, musicname, timestamp, destination_dirpath):
    '''ぼかしの入ったリザルト画像をファイルから取得する

    Args:
        scoretype (str): プレイの種類(SP or DP or DP BATTLE)と譜面難易度
        musicname (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス

    Returns:
        bytes: フロントエンドに渡すデータ
    '''
    return load_image(scoretype, musicname, timestamp, destination_dirpath, dirname_filtereds)

def load_image(scoretype, musicname, timestamp, destination_dirpath, target_dirname):
    '''リザルト画像をファイルから取得する

    Args:
        scoretype (str): プレイの種類(SP or DP or DP BATTLE)と譜面難易度
        musicname (str): 曲名
        timestamp (str): リザルトを記録したときのタイムスタンプ
        destination_dirpath (str): 画像保存先のパス
        target_dirname (str): 保存先の子ディレクトリ名

    Returns:
        bytes: フロントエンドに渡すデータ
    '''
    dirpath = join(destination_dirpath, target_dirname)

    for st in [scoretype, None]:
        for musicname_right in [True, False]:
            filename = generate_filename(st, musicname, timestamp, musicname_right, 'jpg')
            filepath = join(dirpath, filename)
            if isfile(filepath):
                return Image.open(filepath)
        
        filename = generate_filename(st, None, timestamp, filetype='jpg')
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

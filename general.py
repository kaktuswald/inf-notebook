from io import BytesIO
from PIL.Image import Image

imagesize = (1280, 720)

def get_imagevalue(image: Image) -> bytes:
    if image is None:
        return None
    
    if image.height == 1080:
        image = image.resize(imagesize)

    bytes = BytesIO()
    image.save(bytes, format='PNG')
    ret = bytes.getvalue()
    bytes.close()

    return ret

def save_imagevalue(data: bytes, filepath: str):
    '''画像データを画像ファイルに保存する
    
    Args:
        data(bytes): 対象のデータ
        filepath(str): 保存先のファイルパス
    '''
    with open(filepath, 'wb') as f:
        f.write(data)

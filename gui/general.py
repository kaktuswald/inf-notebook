import io

def get_imagevalue(image):
    bytes = io.BytesIO()
    image.save(bytes, format='PNG')
    return bytes.getvalue()

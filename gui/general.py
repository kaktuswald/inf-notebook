import io
import PySimpleGUI as sg
from PIL import Image

from .static import icon_path,background_color

icon_image = Image.open(icon_path)
resized_icon = icon_image.resize((32, 32))
icon_bytes = io.BytesIO()
resized_icon.save(icon_bytes, format='PNG')

def get_imagevalue(image: Image.Image):
    if image is None:
        return None
    
    if image.height == 1080:
        image = image.resize((1280, 720))
    bytes = io.BytesIO()
    image.save(bytes, format='PNG')
    return bytes.getvalue()

def message(title: str, message: str | list, location: tuple[int, int]):
    sg.popup(
        '\n'.join([
            message,
        ]),
        title=title,
        icon=icon_path,
        background_color=background_color,
        relative_location=location
    )

def question(title: str, message: str | list, location: tuple[int, int]):
    if type(message) is list:
        message = '\n'.join(message)

    result = sg.popup_yes_no(
        message,
        title=title,
        icon=icon_path,
        background_color=background_color,
        relative_location=location
    )

    return result == 'Yes'

def progress(title, message, counter, location):
    if type(message) is list:
        message = '\n'.join(message)

    layout = [
        [sg.Text(message, background_color=background_color)],
        [sg.ProgressBar(counter[1], key='-PROG-')],
    ]
    window = sg.Window(
        title,
        layout,
        icon=icon_path,
        return_keyboard_events=True,
        resizable=False,
        finalize=True,
        enable_close_attempted_event=True,
        background_color=background_color,
        keep_on_top=True,
        relative_location=location
    )

    while True:
        event, values = window.read(timeout=100)
        window['-PROG-'].update(counter[0])
        if counter[1] is not None and len(set(counter)) == 1:
            break

    window.close()
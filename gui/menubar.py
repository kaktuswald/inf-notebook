class MenuBar():
    class Text():
        def __init__(self, text: str, key: str=None, disabled: bool=False):
            self.text: str = text
            self.key: str = key
            self.disabled: bool = disabled

    class Line():
        pass

    @staticmethod
    def Compile(value: Line | Text | list):
        if isinstance(value, MenuBar.Line):
            return '---'
        
        if isinstance(value, MenuBar.Text):
            return f'{'!' if value.disabled else ''}{value.text}{f'(&{value.key})' if value.key is not None else ''}'

        if type(value) is list:
            return [MenuBar.Compile(v) for v in value]

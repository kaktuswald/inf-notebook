from os.path import join

from define import define
from resources import resource

playmodes = define.value_list['play_modes']
difficulties = define.value_list['difficulties']
attributes = define.value_list['notesradar_attributes']

class NotesRadarValue():
    """一曲の値
    """

    def __init__(self, musicname: str, difficulty: str, value: float):
        self.musicname: str = musicname
        """曲名"""

        self.difficulty: str = difficulty
        """譜面難易度"""

        self.value: float = value
        """レーダー値"""

class NotesRadarAttribute():
    """ノーツレーダーの属性
    """

    def __init__(self):
        self.average: float = 0
        """平均値"""

        self.ranking: list[NotesRadarValue] = []
        """上位曲データ"""

class NotesRadarItem():
    """プレイモードごとのアイテム
    """

    def __init__(self):
        self.total: float = 0
        """合計値"""

        self.attributes: dict[str, NotesRadarAttribute] = {}
        """属性ごとのデータ"""

        for attribute in attributes:
            self.attributes[attribute] = NotesRadarAttribute()
    
class NotesRadar():
    """ノーツレーダー
    """

    def __init__(self):
        self.items: dict[str, NotesRadarItem] = {}
        """プレイモードごとのアイテム"""

        for playmode in playmodes:
            self.items[playmode] = NotesRadarItem()
    
    def generate(self, summary: dict[str, dict[str, dict[str, dict[str, str | int]]]]):
        for musicname, item1 in resource.notesradar.items():
            if not musicname in summary.keys():
                continue
            for playmode, item2 in item1.items():
                if not playmode in summary[musicname].keys():
                    continue

                values: dict[str, NotesRadarValue] = self.calculate_values(
                    musicname,
                    item2,
                    summary[musicname][playmode]
                )
                
                targetitem = self.items[playmode]

                for attribute in values.keys():
                    targetattribute = targetitem.attributes[attribute]
                    if len(targetattribute.ranking) == 0:
                        targetattribute.ranking.append(values[attribute])
                    else:
                        inserted = False
                        for i in reversed(range(len(targetattribute.ranking))):
                            if targetattribute.ranking[i].value > values[attribute].value:
                                targetattribute.ranking.insert(i + 1, values[attribute])
                                inserted = True
                                break
                        if not inserted:
                            targetattribute.ranking.insert(0, values[attribute])
                        del targetattribute.ranking[10:]

        self.calculate_total()

    def insert(self, playmode: str, musicname: str, summary: dict[str, dict[str, dict[str, dict[str, str | int]]]]):
        if not musicname in resource.notesradar.keys():
            return False
        if not musicname in summary.keys():
            return False
        if not playmode in resource.notesradar[musicname].keys():
            return False
        if not playmode in summary[musicname].keys():
            return False
        
        values: dict[str, NotesRadarValue] = self.calculate_values(
            musicname,
            resource.notesradar[musicname][playmode],
            summary[musicname][playmode]
        )

        targetitem = self.items[playmode]

        for attribute in values.keys():
            targetattribute = targetitem.attributes[attribute]
            if len(targetattribute.ranking) == 0:
                targetattribute.ranking.append(values[attribute])
            else:
                if musicname in [v.musicname for v in targetattribute.ranking]:
                    for i in range(len(targetattribute.ranking)):
                        if musicname == targetattribute.ranking[i].musicname:
                            targetattribute.ranking[i] = values[attribute]
                            break
                else:
                    inserted = False
                    for i in reversed(range(len(targetattribute.ranking))):
                        if targetattribute.ranking[i].value > values[attribute].value:
                            targetattribute.ranking.insert(i + 1, values[attribute])
                            inserted = True
                            break
                    if not inserted:
                        targetattribute.ranking.insert(0, values[attribute])
                    del targetattribute.ranking[10:]

        self.calculate_total()

        return True

    def calculate_values(self, musicname: str, notesradaritem: dict, summaryitem: dict[str, dict[str, dict[str, str | int]]]):
        values: dict[str, NotesRadarValue] = {}
        for difficulty in difficulties:
            if not difficulty in notesradaritem.keys():
                continue
            if not difficulty in summaryitem.keys():
                continue
            if not 'score' in summaryitem[difficulty].keys():
                continue
            score = summaryitem[difficulty]['score']
            if score is None or score == 0:
                continue
            notes, radars = notesradaritem[difficulty]
            for attribute in attributes:
                if radars[attribute] == 0:
                    continue
                rate = score * 100 // (notes * 2) / 100
                v = rate * 100 * radars[attribute] // 1 / 100
                if not attribute in values.keys() or values[attribute].value < v:
                    values[attribute] = NotesRadarValue(musicname, difficulty, v)

        return values
        
    def calculate_total(self):
        for item in self.items.values():
            for attribute in item.attributes.values():
                if len(attribute.ranking) > 0:
                    attribute.average = sum([t.value for t in attribute.ranking]) * 100 // len(attribute.ranking) / 100
                else:
                    attribute.average = 0
            item.total = sum([t.average for t in item.attributes.values()]) * 100 // 1 / 100
    
if __name__ == '__main__':
    from record import NotebookSummary
    from graph import create_radarchart
    from export import output_notesradarcsv,output_notesradarimage

    resource.load_resource_notesradar()

    summary = NotebookSummary().json['musics']

    radar = NotesRadar()

    radar.generate(summary)

    output_notesradarcsv(radar)

    image = create_radarchart(radar)
    output_notesradarimage(image)

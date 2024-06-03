from define import define
from resources import resource

ranking_count = 50

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
    
    def __lt__(self, other: float):
        return self.value < other

    def __gt__(self, other: float):
        return self.value > other

    def __eq__(self, item):
        return self.musicname == item.musicname

class NotesRadarAttribute():
    """ノーツレーダーの属性
    """

    def __init__(self):
        self.average: float = 0
        """平均値"""

        self.ranking: list[NotesRadarValue] = []
        """上位曲データ"""

        self.targets: list[NotesRadarValue] = []
        """平均対象のデータ"""
    
    def calculate_average(self):
        self.ranking.sort(reverse=True)

        self.targets.clear()
        for t in self.ranking:
            if not t in self.targets:
                self.targets.append(t)
                if len(self.targets) == 10:
                    break

        if len(self.ranking) > ranking_count:
            del self.ranking[ranking_count:]

        if len(self.targets) > 0:
            self.average = sum([t.value * 100 for t in self.targets]) // 10 / 100

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
    
    def calculate_total(self):
        self.total = sum([t.average for t in self.attributes.values()]) * 100 // 1 / 100
    
class NotesRadar():
    """ノーツレーダー
    """

    def __init__(self):
        self.items: dict[str, NotesRadarItem] = {}
        """プレイモードごとのアイテム"""

        for playmode in playmodes:
            self.items[playmode] = NotesRadarItem()
    
    def generate(self, summary: dict[str, dict[str, dict[str, dict[str, str | int]]]]):
        for playmode, item1 in resource.notesradar.items():
            targetitem = self.items[playmode]
            attributes = targetitem.attributes

            for attribute, item2 in item1['attributes'].items():
                targetattribute = attributes[attribute]
                ranking = targetattribute.ranking

                for item3 in item2:
                    musicname = item3['musicname']
                    difficulty = item3['difficulty']

                    if not musicname in summary.keys():
                        continue
                    if not difficulty in summary[musicname][playmode].keys():
                        continue
                    if not 'score' in summary[musicname][playmode][difficulty].keys():
                        continue
                    if summary[musicname][playmode][difficulty]['score'] is None:
                        continue
                    
                    target = resource.notesradar[playmode]['musics'][musicname][difficulty]
                    notes = target['notes']
                    max = target['radars'][attribute]

                    if len(ranking) == ranking_count and min(ranking).value > max:
                        break

                    score = summary[musicname][playmode][difficulty]['score']
                    
                    rate = score * 10000 / (notes * 2) // 1
                    calculated = rate * max / 100 // 1 / 100

                    if len(ranking) == ranking_count and min(ranking).value > calculated:
                        continue

                    ranking.append(NotesRadarValue(musicname, difficulty, calculated))
                    ranking.sort(reverse=True)
                    del ranking[ranking_count:]
                
                targetattribute.calculate_average()
            
            targetitem.calculate_total()

    def insert(self, playmode: str, musicname: str, difficulty: str, score: int, summary: dict[str, dict[str, dict[str, dict[str, str | int]]]]):
        if not musicname in resource.notesradar[playmode]['musics'].keys():
            return False
        if not difficulty in resource.notesradar[playmode]['musics'][musicname].keys():
            return False

        targetitem = self.items[playmode]

        score = summary[musicname][playmode][difficulty]['score']
        notes = resource.notesradar[playmode]['musics'][musicname][difficulty]['notes']

        updated = False
        for attribute, targetattribute in targetitem.attributes.items():
            max = resource.notesradar[playmode]['musics'][musicname][difficulty]['radars'][attribute]

            rate = score * 100 // (notes * 2) / 100
            calculated = rate * 100 * max // 1 / 100

            ranking = targetattribute.ranking

            if len(ranking) > 0 and ranking[-1].value > calculated:
                continue

            attribute_updated = False
            
            for value in ranking:
                if value.musicname == musicname and value.difficulty == difficulty:
                    value.value = calculated
                    attribute_updated = True
                    break
            
            if not attribute_updated:
                ranking.append(NotesRadarValue(musicname, difficulty, calculated))
                attribute_updated = True
            
            if attribute_updated:
                ranking.sort(reverse=True)
                if len(ranking) > ranking_count:
                    del ranking[ranking_count:]
                targetattribute.calculate_average()
                updated = True

        if updated:
            targetitem.calculate_total()

        return updated
    
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

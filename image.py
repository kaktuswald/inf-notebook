from os.path import join,exists
from PIL import Image,ImageFont,ImageDraw
from csv import reader

from define import define

image = Image.new("RGB", (1280, 720), (255, 255, 255))
draw = ImageDraw.Draw(image)

font_title = ImageFont.truetype('Resources/Fonts/gomarice_mukasi_mukasi.ttf', 80)
font = ImageFont.truetype('Resources/Fonts/gomarice_mukasi_mukasi.ttf', 48)

def generateimage_summary():
    draw.rectangle((0, 0, 1280, 720), fill=(255, 255, 255))
    draw.multiline_text((20, 20), '統計', fill=(0, 0, 0), font=font_title)
    bbox = draw.multiline_textbbox((0, 0), 'TOTAL', font=font)
    draw.multiline_text((1250 - bbox[2], 100), 'TOTAL', fill=(0, 0, 0), font=font)

    summarytypes_xpositions = ((280, 530), (590, 1030))

    levels_count = 5
    playmodes = define.value_list['play_modes']
    summarytypes = ['DJレベル', 'クリアタイプ']
    difficulties = define.value_list['levels'][-levels_count:]
    totals = {}
    for stindex in range(len(summarytypes)):
        summarytype = summarytypes[stindex]
        bbox = draw.multiline_textbbox((0, 0), summarytype, font=font)
        draw.multiline_text((summarytypes_xpositions[stindex][1]-bbox[2], 100), summarytype, fill=(0, 0, 0), font=font)

    for pmindex in range(len(playmodes)):
        playmode = playmodes[pmindex]
        draw.multiline_text((80, pmindex*300+250), playmode, fill=(0, 0, 0), font=font)
        for dindex in range(len(difficulties)):
            level = difficulties[dindex]
            draw.multiline_text((180, pmindex*300+dindex*50+150), level, fill=(0, 0, 0), font=font)

    for pmindex in range(len(playmodes)):
        playmode = playmodes[pmindex]
        totals = [[] for i in range(levels_count)]

        for stindex in range(len(summarytypes)):
            summarytype = summarytypes[stindex]
            filename = f'{playmode}-レベル-{summarytype}.csv'
            filepath = join('export', filename)
            if not exists(filepath):
                continue

            with open(filepath) as f:
                rows = [*reader(f)]
                keys = [*reversed(rows[0][2:-2])]
                for lindex in range(levels_count):
                    rindex = len(rows) - levels_count + lindex
                    counts = [int(v) for v in reversed(rows[rindex][2:-2])]
                    maxcount = max(counts)
                    index = counts.index(maxcount)

                    draw.multiline_text((summarytypes_xpositions[stindex][0], pmindex*300+lindex*50+150), keys[index], fill=(0, 0, 0), font=font)

                    strmaxcount = str(maxcount)
                    bbox = draw.multiline_textbbox((0, 0), strmaxcount, font=font)
                    draw.multiline_text((summarytypes_xpositions[stindex][1]-bbox[2], pmindex*300+lindex*50+150), strmaxcount, fill=(0, 0, 0), font=font)

                    totals[lindex].append(rows[rindex][-1])
        
        for lindex in range(len(totals)):
            setted = set(totals[lindex])
            if len(setted) == 1:
                totalcount = [*setted][0]
                bbox = draw.multiline_textbbox((0, 0), totalcount, font=font)
                draw.multiline_text((1250-bbox[2], pmindex*300+lindex*50+150), totalcount, fill=(0, 0, 0), font=font)

    return image

colors = {
    'BEGINNER': (0, 255, 0),
    'NORMAL': (0, 0, 255),
    'HYPER': (208, 208, 0),
    'ANOTHER': (255, 0, 0),
    'LEGGENDARIA': (208, 0, 208)
}
def generateimage_musicinformation(playmode, difficulty, musicname, record):
    draw.rectangle((0, 0, 1280, 720), fill=(255, 255, 255))
    draw.multiline_text((20, 20), musicname, fill=(0, 0, 0), font=font_title)
    draw.multiline_text((50, 120), f'{playmode} {difficulty}', fill=colors[difficulty], font=font)

    draw.multiline_text((20, 200), 'Options when update a new record.', fill=(0, 0, 0), font=font)
    if 'best' in record.keys():
        for keyindex in range(4):
            key = ['clear_type', 'dj_level', 'score', 'miss_count'][keyindex]
            if key in record['best'].keys() and record['best'][key] is not None:
                draw.multiline_text((50, keyindex*100+260), str.upper(key.replace('_', ' ')), fill=(0, 0, 0), font=font_title)
                if record['best'][key]['options'] is None:
                    option = '??????'
                else:
                    option = record['best'][key]['options']['arrange'] if 'arrange' in record['best'][key]['options'].keys() and record['best'][key]['options']['arrange'] is not None  else '------'
                draw.multiline_text((600, keyindex*100+260), option, fill=(0, 0, 0), font=font_title)

    return image

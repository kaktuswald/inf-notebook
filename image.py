from os import mkdir
from os.path import join,exists
from PIL import Image,ImageFont,ImageDraw
from csv import reader

from define import define
from resources import resource

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

output_directory = 'export'
output_filename_summary = 'summary.png'
output_filename_musicinformation = 'musicinformation.png'

musicinformation_keys = ['score', 'miss_count']

summarytypes = {'cleartypes': 'クリアタイプ', 'djlevels': 'DJレベル'}
summarytypes_xpositions = {'cleartypes': (250, 700), 'djlevels': (750, 1050)}
playmode_xposition = 50
level_xposition = 200
total_exposition = 1250

if not exists(output_directory):
    mkdir(output_directory)

def generateimage_summary(setting):
    draw.rectangle((0, 0, 1280, 720), fill=background)
    draw.multiline_text((20, 20), 'Number of goals achieved.', fill=textcolor, font=font_title)

    bbox = draw.multiline_textbbox((0, 0), 'CLEAR TYPE', font=font)
    draw.multiline_text((summarytypes_xpositions['cleartypes'][1] - bbox[2], 150), 'CLEAR TYPE', fill=textcolor, font=font)

    bbox = draw.multiline_textbbox((0, 0), 'DJ LEVEL', font=font)
    draw.multiline_text((summarytypes_xpositions['djlevels'][1] - bbox[2], 150), 'DJ LEVEL', fill=textcolor, font=font)

    bbox = draw.multiline_textbbox((0, 0), 'TOTAL', font=font)
    draw.multiline_text((total_exposition - bbox[2], 150), 'TOTAL', fill=textcolor, font=font)

    summaryvalues = {}
    for playmode in define.value_list['play_modes']:
        summaryvalues[playmode] = {}
        for summarytype_a, summarytype_b in summarytypes.items():
            filename = f'{playmode}-レベル-{summarytype_b}.csv'
            filepath = join('export', filename)
            if not exists(filepath):
                continue

            with open(filepath) as f:
                values = [*reader(f)]
            summaryvalues[playmode][summarytype_a] = {}
            columnkeys = values[0][1:-2]
            for line in values[1:]:
                level = line[0]
                summaryvalues[playmode][summarytype_a][level] = {}
                count = 0
                for columnindex in range(len(columnkeys)):
                    count += int(line[-(columnindex+3)])
                    summaryvalues[playmode][summarytype_a][level][columnkeys[-(columnindex+1)]] = str(count)

    table = {}
    for playmode in setting.keys():
        for level in setting[playmode].keys():
            for summarytype in setting[playmode][level].keys():
                targetkeys = setting[playmode][level][summarytype]
                if summarytype in summaryvalues[playmode].keys() and len(targetkeys) >= 1:
                    if not playmode in table.keys():
                        table[playmode] = {}
                    if not level in table[playmode].keys():
                        table[playmode][level] = {'TOTAL': len(resource.musictable['levels'][playmode][level])}
                    if not summarytype in table[playmode][level].keys():
                        table[playmode][level][summarytype] = {}
                    for targetkey in targetkeys:
                        table[playmode][level][summarytype][targetkey] = summaryvalues[playmode][summarytype][level][targetkey]

    line = 0
    for playmode in table.keys():
        for level in table[playmode].keys():
            levelcount = max([len(v) for k, v in table[playmode][level].items() if k != 'TOTAL'])
            items = {}
            for summarytype in summarytypes.keys():
                items[summarytype] = [*table[playmode][level][summarytype].items()] if summarytype in table[playmode][level].keys() else []
            total = str(len(resource.musictable['levels'][playmode][level]))

            for index in range(levelcount):
                draw.multiline_text((playmode_xposition, line*50+200), playmode, fill=textcolor, font=font)
                
                bbox = draw.multiline_textbbox((0, 0), level, font=font)
                draw.multiline_text((level_xposition-bbox[2], line*50+200), level, fill=textcolor, font=font)

                for summarytype in summarytypes.keys():
                    if index >= len(items[summarytype]) or not summarytype in table[playmode][level].keys():
                        continue

                    key, value = items[summarytype][index]

                    draw.multiline_text((summarytypes_xpositions[summarytype][0], line*50+200), key, fill=textcolor, font=font)
                    bbox = draw.multiline_textbbox((0, 0), value, font=font)
                    draw.multiline_text((summarytypes_xpositions[summarytype][1]-bbox[2], line*50+200), value, fill=textcolor, font=font)

                bbox = draw.multiline_textbbox((0, 0), total, font=font)
                draw.multiline_text((total_exposition-bbox[2], line*50+200), total, fill=textcolor, font=font)

                line += 1

    image.save(join(output_directory, output_filename_summary))
    return image

def generateimage_musicinformation(playmode, difficulty, musicname, record):
    draw.rectangle((0, 0, 1280, 720), fill=background)

    bbox = draw.multiline_textbbox((0, 0), musicname, font=font_musicname)
    if bbox[2] >= 1240:
        musicnameimage = Image.new("RGBA", (bbox[2], 100), background)
        musicnamedraw = ImageDraw.Draw(musicnameimage)
        musicnamedraw.multiline_text((0, 0), musicname, font=font_musicname)
        resized = musicnameimage.resize((1240, 100))
        image.paste(resized, (20, 20))
    else:
        draw.multiline_text((20, 20), musicname, fill=textcolor, font=font_musicname)
    draw.multiline_text((50, 120), f'{playmode} {difficulty}', fill=colors_difficulty[difficulty], font=font)

    if 'timestamps' in record.keys():
        count = str(len(record['timestamps']))
        draw.multiline_text((20, 200), 'Played count.', fill=textcolor, font=font)
        bbox = draw.multiline_textbbox((0, 0), count, font=font_title)
        draw.multiline_text((680-bbox[2], 170), count, fill=textcolor, font=font_title)

    if 'latest' in record.keys():
        draw.multiline_text((20, 300), 'Last time played.', fill=textcolor, font=font)
        draw.multiline_text((500, 270), record['latest']['timestamp'], fill=textcolor, font=font_title)

    if 'best' in record.keys():
        draw.multiline_text((20, 400), 'Options when update a new record.', fill=textcolor, font=font)
        for keyindex in range(len(musicinformation_keys)):
            key = musicinformation_keys[keyindex]
            draw.multiline_text((50, keyindex*100+460), str.upper(key.replace('_', ' ')), fill=textcolor, font=font_title)

            if not key in record['best'].keys() or record['best'][key] is None:
                break

            value = str(record['best'][key]['value'])
            bbox = draw.multiline_textbbox((0, 0), value, font=font_title)
            draw.multiline_text((750-bbox[2], keyindex*100+460), value, fill=textcolor, font=font_title)

            has_options = 'options' in record['best'][key].keys() and record['best'][key]['options'] is not None
            if has_options and 'arrange' in record['best'][key]['options'].keys():
                arrange = record['best'][key]['options']['arrange']
                draw.multiline_text((800, keyindex*100+460), arrange if arrange is not None else '-----', fill=textcolor, font=font_title)
            else:
                draw.multiline_text((800, keyindex*100+460), '?????', fill=textcolor, font=font_title)

    image.save(join(output_directory, output_filename_musicinformation))
    return image

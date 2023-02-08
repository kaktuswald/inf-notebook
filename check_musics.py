from os.path import exists
from sys import exit
import json

arcadeallmusics_filename = 'arcade_all_musics.txt'
infinitasonlymusics_filename = 'infinitas_only_musics.txt'

from resources import recog_musics_filepath

if not exists(recog_musics_filepath):
    exit()

with open(recog_musics_filepath) as f:
    recog_music = json.load(f)

with open(arcadeallmusics_filename, 'r', encoding='utf-8') as f:
    arcade_all_musics = f.read().split('\n')

with open(infinitasonlymusics_filename, 'r', encoding='utf-8') as f:
    infinitas_only_musics = f.read().split('\n')

print(f'arcade all music count: : {len(arcade_all_musics)}')
print(f'infinitas only music count: : {len(infinitas_only_musics)}')

duplicates = list(set(arcade_all_musics) & set(infinitas_only_musics))
if len(duplicates) > 0:
    print(f"duplicates: {','.join(duplicates)}")

def check(target):
    if type(target) is dict:
        for value in target.values():
            check(value)
    else:
        if not target in arcade_all_musics and not target in infinitas_only_musics:
            print(f"not found: {target}({target.encode('unicode-escape').decode()})")

check(recog_music)

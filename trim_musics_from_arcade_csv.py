from os.path import exists
from sys import exit
import json

scoredata_filename = 'score_data.csv'
arcadeallmusics_filename = 'arcade_all_musics.txt'

from resources import recog_musics_filepath

if not exists(recog_musics_filepath):
    exit()

with open(recog_musics_filepath) as f:
    recog_music = json.load(f)

with open(scoredata_filename, 'r', encoding='utf-8') as f:
    scoredata = f.read().split('\n')

all_musics = [line.split(',')[1] for line in scoredata[1:-1]]

with open(arcadeallmusics_filename, 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_musics))

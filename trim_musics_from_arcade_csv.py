scoredata_filename = 'score_data.csv'
arcadeallmusics_filename = 'musics_arcade_all.txt'

with open(scoredata_filename, 'r', encoding='utf-8') as f:
    scoredata = f.read().split('\n')

all_musics = [line.split(',')[1] for line in scoredata[1:-1]]

with open(arcadeallmusics_filename, 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_musics))

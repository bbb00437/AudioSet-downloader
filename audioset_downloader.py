import ffmpy
import librosa
import os
import pafy
import time
from multiprocessing.dummy import Pool

TARGET_CSV = 'balanced_train_segments.csv'
TARGET_DIR = r'D:\Dataset\AudioSet\balanced_train_segments'
YT_LINK = 'https://www.youtube.com/watch?v='

FILTER_LABELS = [
    # 'Baby cry, infant cry',
    # 'Baby laughter',
]


class Segment:
    def __init__(self, yt_id, start_seconds, end_seconds, positive_labels):
        self.positive_labels = positive_labels
        self.end_seconds = end_seconds
        self.start_seconds = start_seconds
        self.yt_id = yt_id

    @property
    def url(self):
        return YT_LINK + self.yt_id

    @property
    def filename(self):
        return '{}_{}_{}.wav'.format(self.yt_id, int(self.start_seconds), int(self.end_seconds))


label_dct = {}
filtered_label_set = set()
with open('class_labels_indices.csv', 'r') as f:
    for ln in f.readlines()[1:]:
        index, mid, display_name = ln.rstrip().split(',', maxsplit=2)
        display_name = display_name.replace('\"', '')
        label_dct[mid] = display_name
        if len(FILTER_LABELS) == 0 or display_name in FILTER_LABELS:
            filtered_label_set.add(mid)

segments = []
cnt = 0

with open(TARGET_CSV, 'r') as f:
    for ln in f.readlines()[3:]:
        _yt_id, _start, _end, _labels = ln.rstrip().split(', ')
        _labels = _labels.replace('\"', '').split(',')
        if set(_labels).isdisjoint(filtered_label_set):
            continue
        segments.append(Segment(_yt_id, float(_start), float(_end), _labels))

if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)


def download(segment):
    global cnt
    cnt += 1
    save_path = None
    temp_path = None
    try:
        save_path = os.path.join(TARGET_DIR, segment.filename)
        if os.path.exists(save_path):
            print('({}/{}) {} already exists.'.format(cnt, len(segments), save_path))
            return
        print('({}/{}) Downloading \"{}\", time(sec)={}~{}, labels={}'
              .format(cnt, len(segments), segment.url, int(segment.start_seconds), int(segment.end_seconds),
                      list(map(lambda s: label_dct[s], segment.positive_labels))))

        video = pafy.new(segment.url)
        best_audio = video.getbestaudio()
        temp_path = save_path.replace('.wav', '.' + best_audio.extension)
        cmd = 'ffmpeg -i \"{}\" -ss {} -to {} -vn -c:a copy {}' \
            .format(best_audio.url, int(round(segment.start_seconds)), int(round(segment.end_seconds)), temp_path)
        os.system(cmd)

        if temp_path != save_path:
            ffmpy.FFmpeg(inputs={temp_path: None}, outputs={save_path: None}).run()
            os.remove(temp_path)

        data, sr = librosa.load(save_path, sr=22050)
        librosa.output.write_wav(save_path, data, sr)
        time.sleep(1)
    except Exception as e:
        print('*****************************')
        print('**** Something happened. ****')
        print('*****************************')
        print(e)
        for _path in [save_path, temp_path]:
            if _path and os.path.exists(_path):
                os.remove(_path)


with Pool(4) as workers:
    workers.map(download, segments)

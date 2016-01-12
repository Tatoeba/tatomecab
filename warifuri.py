#!/usr/bin/python

import xml.etree.ElementTree as ET
import sys, string, re

class Warifuri():
    def __init__(self):
        kata = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲン"
        hira = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをん"
        self.kata_to_hira_map = str.maketrans(kata, hira)
        self.hira_to_kata_map = str.maketrans(hira, kata)
        self.readings = {}

    def kata_to_hira(self, string):
        return string.translate(self.kata_to_hira_map)

    def hira_to_kata(self, string):
        return string.translate(self.hira_to_kata_map)

    def filter_kanjidict_reading(self, reading):
        reading = reading.split('.')[0]
        reading = reading.replace('-', '')
        reading = self.kata_to_hira(reading)
        return reading

    def load_readings(self, kanji, readings):
        readings = [self.filter_kanjidict_reading(r) for r in readings]
        sokuon = [ 'つ', 'ち', 'く', 'き']
        for reading in filter(lambda r: r[-1] in sokuon, readings):
            readings.append(reading[0:-1] + 'っ')
        readings = readings + [self.hira_to_kata(r) for r in readings]
        self.readings[ ord(kanji) ] = readings

    def load_kanjidic_readings(self, filename):
        all_readings = {}
        root = ET.parse(filename).getroot()
        for character in root.findall('character'):
            char = character.find('literal').text
            readings = []
            for r in character.iter('reading'):
                if r.get('r_type') in ['ja_on', 'ja_kun']:
                    readings.append(r.text)
            if char:
                self.load_readings(char, readings)

    def parallel_trim(self, kanjis, furi):
        pref = 0
        while pref < len(kanjis) and pref < len(furi) and kanjis[pref] == furi[pref]:
            pref = pref + 1
        suff = 0
        while suff > pref-len(kanjis) and kanjis[suff-1] == furi[suff-1]:
            suff = suff - 1

        klist = []
        flist = []
        if (pref < suff + len(kanjis)):
            if (suff == 0):
                suff = None
            klist.append(kanjis[pref:suff])
            flist.append(furi[pref:suff])
        if (suff):
            klist.append(kanjis[suff:])
            flist.append(furi[suff:])
        if (pref):
            klist.insert(0, kanjis[:pref])
            flist.insert(0, furi[:pref])
        return (klist, flist)

    def split_furi(self, kanjis, furi):
        chars = []
        # Python re compatible form of ([^\p{Han}]+|.)
        # Generated using http://www.unicode.org/Public/UCD/latest/ucd/Scripts.txt
        regex = r'([^\u2E80-\u2E99\u2E9B-\u2EF3\u2F00-\u2FD5\u3005\u3007\u3021-\u3029\u3038-\u303A\u303B\u3400-\u4DB5\u4E00-\u9FD5\uF900-\uFA6D\uFA70-\uFAD9\u20000-\u2A6D6\u2A700-\u2B734\u2B740-\u2B81D\u2B820-\u2CEA1\u2F800-\u2FA1D]+|.)'
        segments = re.findall(regex, kanjis)
        for segment in segments:
            try:
                readings = self.readings[ord(segment)]
            except (KeyError, TypeError):
                readings = [ segment, self.hira_to_kata(segment) ]
            readings = [re.escape(r) for r in readings]
            chars.append('(' + '|'.join(readings) + ')')
        regex = '^' + ''.join(chars) + '$'
        split = re.findall(regex, furi)
        groups = [ ]
        if (split):
            if (type(split[0]) is str):
                groups = [ split[0] ]
            else:
                groups = list(split[0])
        if (len(groups) == len(segments)):
            return (segments, groups)
        else:
            return self.parallel_trim(kanjis, furi)

if __name__ == '__main__':
    warifuri = Warifuri()
    warifuri.load_kanjidic_readings(sys.argv[1])
    print(warifuri.split_furi(sys.argv[2], sys.argv[3]))

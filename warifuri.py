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

    def load_kanjidic_readings(self, filename):
        all_readings = {}
        root = ET.parse(filename).getroot()
        for character in root.findall('character'):
            char = character.find('literal').text
            readings = []
            for r in character.iter('reading'):
                if r.get('r_type') in ['ja_on', 'ja_kun']:
                    reading = r.text.split('.')[0]
                    readings.append(self.kata_to_hira(reading))
            if char:
                self.readings[ord(char)] = readings

    def split_furi(self, kanjis, furi):
        chars = []
        n_kanjis = 0
        for kanji in kanjis:
            try:
                readings = self.readings[ord(kanji)]
                readings = readings + [self.hira_to_kata(c) for c in readings]
            except KeyError:
                readings = [ kanji ]
            chars.append('(' + '|'.join(readings) + ')')
            n_kanjis = n_kanjis + 1
        regex = '^' + ''.join(chars) + '$'
        split = re.findall(regex, furi)
        if (split and len(split[0]) == n_kanjis):
            return [ tuple(kanjis), split[0] ]
        else:
            return [ (kanjis,), (furi,) ]

if __name__ == '__main__':
    warifuri = Warifuri()
    warifuri.load_kanjidic_readings(sys.argv[1])
    print(warifuri.split_furi(sys.argv[2], sys.argv[3]))

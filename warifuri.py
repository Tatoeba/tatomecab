#!/usr/bin/python

import xml.etree.ElementTree as ET
import sys, string, re, csv

class Warifuri():
    def __init__(self):
        kata = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲン"
        hira = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをん"
        self.kata_to_hira_map = str.maketrans(kata, hira)
        self.hira_to_kata_map = str.maketrans(hira, kata)
        rendaku = {
            'か':'が','き':'ぎ','く':'ぐ','け':'げ','こ':'ご',
            'さ':'ざ','し':'じ','す':'ず','せ':'ぜ','そ':'ぞ',
            'た':'だ','ち':'ぢ','つ':'づ','て':'で','と':'ど',
            'は':'ばぱ','ひ':'びぴ','ふ':'ぶぷ','へ':'べぺ','ほ':'ぼぽ',
        }
        self.rendaku_map = str.maketrans(rendaku)
        self.rendaku = list(rendaku)
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
        for reading in filter(lambda r: r[-1] in sokuon and len(r) > 1, readings):
            readings.append(reading[0:-1] + 'っ')
        for reading in filter(lambda r: r[0] in self.rendaku, readings):
            rendaku = reading[0].translate(self.rendaku_map)
            for char in list(rendaku):
                readings.append(char + reading[1:])
        readings = readings + [self.hira_to_kata(r) for r in readings]
        self.readings[ ord(kanji) ] = readings

    def load_kanjidic_readings(self, filename):
        all_readings = {}
        root = ET.parse(filename).getroot()
        for character in root.findall('character'):
            char = character.find('literal').text
            readings = [ nanori.text for nanori in character.iter('nanori') ]
            for r in character.iter('reading'):
                if r.get('r_type') in ['ja_on', 'ja_kun']:
                    readings.append(r.text)
            if char:
                self.load_readings(char, readings)

    def split_furi(self, kanjis, furi):
        chars = [[]]
        # Python re compatible form of (?P<rest>[^\p{Han}]+)|(?P<kanji>.)
        # Generated using http://www.unicode.org/Public/UCD/latest/ucd/Scripts.txt
        regex = r'(?P<rest>[^\u2E80-\u2E99\u2E9B-\u2EF3\u2F00-\u2FD5\u3005\u3007\u3021-\u3029\u3038-\u303A\u303B\u3400-\u4DB5\u4E00-\u9FD5\uF900-\uFA6D\uFA70-\uFAD9\U00020000-\U0002A6D6\U0002A700-\U0002B734\U0002B740-\U0002B81D\U0002B820-\U0002CEA1\U0002F800-\U0002FA1D]+)|(?P<kanji>.)'
        segments = []
        for match in re.finditer(regex, kanjis):
            segments.append(match.group(0))
            token = match.groupdict()
            if token['kanji']:
                try:
                    readings = self.readings[ord(token['kanji'])]
                except KeyError:
                    readings = [ token['kanji'] ]
                chars[-1].append(readings)
            else:
                segment = token['rest']
                readings = [ segment, self.hira_to_kata(segment) ]
                readings = [ re.escape(r) for r in readings ]
                chars.append(readings)
                chars.append([])

        regex = []
        for i, char in enumerate(chars):
            char = chars[i]
            if len(char):
                if type(char[0]) is str:
                    block = '(' + '|'.join(char) + ')'
                else:
                    block = ''.join([ '(' + '|'.join(c) + ')' for c in char ])
                    block = '(?:' + block + '|(.+))'
                regex.append(block)
        match = re.match(''.join(regex) + '$', furi)
        if match:
            groups = list(match.groups())
        else:
            groups = []

        s = 0
        for i, item in enumerate(groups):
            if item is None:
                if i > 0 and groups[i-1] is None and s+1 < len(segments):
                    segments[s:s+2] = [ segments[s] + segments[s+1] ]
            else:
                s = s + 1
        groups = [ item for item in groups if item is not None ]

        if (len(groups) == len(segments)):
            return (segments, groups)
        else:
            return ([kanjis], [furi])

if __name__ == '__main__':
    warifuri = Warifuri()
    if len(sys.argv) != 2:
        print('Usage: {} kanjidic2.xml < dict.csv > dict.furi.splitted.csv'.format(sys.argv[0]))
        sys.exit(1)
    warifuri.load_kanjidic_readings(sys.argv[1])
    kanji_pos = 0
    reading_pos = 11
    mecabdict = csv.writer(sys.stdout, lineterminator='\n')
    for row in csv.reader(iter(sys.stdin.readline, '')):
        kanji = row[kanji_pos]
        reading = row[reading_pos].replace('.', '')
        kanji, reading = warifuri.split_furi(kanji, reading)
        splitted_reading = ''
        for i in range(len(kanji)-1):
            reading[i] = reading[i] + '.' * len(kanji[i])
        row[reading_pos] = ''.join(reading)
        mecabdict.writerow(row)

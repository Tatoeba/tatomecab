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
        self.okurigana_map = {
            'う':'い', 'く':'き', 'ぐ':'ぎ', 'す':'し',
            'つ':'ち', 'ぶ':'び', 'む':'み', 'る':'り',
        }
        self.okurigana_first_char = [
            'え', 'け', 'き', 'せ', 'て', 'ち', 'び',
            'め', 'み', 'れ', 'り',
        ]
        self.readings = {}
        self.jukukijuns = {}

    def kata_to_hira(self, string):
        return string.translate(self.kata_to_hira_map)

    def hira_to_kata(self, string):
        return string.translate(self.hira_to_kata_map)

    def filter_kanjidict_reading(self, reading):
        reading = reading.split('.')[0]
        reading = reading.replace('-', '')
        reading = self.kata_to_hira(reading)
        return reading

    def get_okurigana_inflections(self, readings):
        inflections = []
        for reading in readings:
            parts = reading.split('.', 1)
            if len(parts) == 2:
                base, okurigana = parts
                try:
                    inflections.append(base + self.okurigana_map[okurigana])
                except KeyError:
                    if (len(okurigana) > 1
                        and okurigana[0] in self.okurigana_first_char):
                        inflections.append(base + okurigana[0])
        return inflections

    def load_kanji_readings(self, kanji, readings):
        readings = readings + self.get_okurigana_inflections(readings)
        readings = [self.filter_kanjidict_reading(r) for r in readings]
        sokuon = [ 'つ', 'ち', 'く', 'き']
        for reading in filter(lambda r: r[-1] in sokuon and len(r) > 1, readings):
            readings.append(reading[0:-1] + 'っ')
        for reading in filter(lambda r: r[0] in self.rendaku, readings):
            rendaku = reading[0].translate(self.rendaku_map)
            for char in list(rendaku):
                readings.append(char + reading[1:])
        return readings

    def load_readings(self, kanjis, readings):
        if len(kanjis) == 1:
            readings = self.load_kanji_readings(kanjis, readings)
        readings = list(set(readings))
        readings = readings + [self.hira_to_kata(r) for r in readings]
        if len(kanjis) == 1:
            self.readings[ ord(kanjis) ] = readings
        else:
            self.jukukijuns[ kanjis ] = readings

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

    def load_csv_readings(self, filename):
        with open(filename, newline='') as csvfile:
            readings_reader = csv.reader(csvfile)
            try:
                for row in readings_reader:
                    kanjis, readings = row[0], row[1:]
                    self.load_readings(kanjis, readings)
            except csv.Error as e:
                sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))

    def to_regex(self, paths):
        regex = []
        for path in paths:
            if type(path) is tuple:
                block = ''.join(self.to_regex(path))
            elif type(path[0]) is bool:
                readings = path[2]
                block = '(' + '|'.join(readings) + ')'
            else:
                parts = self.to_regex(path)
                block = '(?:' + '|'.join(parts) + ')'
            regex.append(block)
        return regex

    def anything_path(self, kanjis):
        anything = [[ False, '', [''] ]] * (len(kanjis)-1)
        anything.append([ False, '', ['.+'] ])
        return [ tuple(kanjis), tuple(anything) ]

    def add_optimistic_paths(self, paths):
        new_paths = []
        kanjis = []
        for path in paths:
            is_kanji = path[0]
            if is_kanji:
                kanjis.append(path)
            else:
                if len(kanjis):
                    new_paths.append(self.anything_path(kanjis))
                    kanjis = []
                new_paths.append(path)
        if len(kanjis):
            new_paths.append(self.anything_path(kanjis))
        return new_paths

    def add_jukujikun_paths(self, paths):
        if type(paths) is tuple:
            paths = list(paths)
            kanjis = ''.join([ p[1] for p in paths ])
            for jukujikun, readings in self.jukukijuns.items():
                pos = 0
                while True:
                    try:
                        pos = kanjis.index(jukujikun, pos)
                    except ValueError:
                        break
                    j_path = [[ False, '', [''] ]] * (len(jukujikun)-1)
                    j_path.append([ True, jukujikun, readings ])
                    replacement = [[ tuple(j_path), tuple(paths[pos:pos+len(jukujikun)]) ]]
                    paths[pos:pos+len(jukujikun)] = replacement
                    kanjis = kanjis[:pos] + ' ' + kanjis[pos+len(jukujikun):]
                    pos = pos + 1
            return tuple(paths)
        elif type(paths) is list and type(paths[0]) is not bool:
            for i, path in enumerate(paths):
                paths[i] = self.add_jukujikun_paths(path)
        return paths

    def split_furi(self, kanjis, furi):
        paths = []
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
                paths.append([ True, token['kanji'], readings ])
            else:
                segment = token['rest']
                readings = [ segment, self.hira_to_kata(segment) ]
                readings = [ re.escape(r) for r in readings ]
                paths.append([ False, segment, readings ])
        paths = self.add_optimistic_paths(paths)
        paths = self.add_jukujikun_paths(paths)
        regex = self.to_regex(paths)
        match = re.match(''.join(regex) + '$', furi)
        if match:
            groups = list(match.groups())
        else:
            groups = []

        s = 0
        groups = [ item for item in groups if item is not None ]
        for i, item in enumerate(groups):
            if i > 0 and groups[i-1] == '' and s < len(segments):
                segments[s-1:s+1] = [ segments[s-1] + segments[s] ]
            else:
                s = s + 1
        groups = [ item for item in groups if item != '' ]

        if (len(groups) == len(segments)):
            return (segments, groups)
        else:
            return ([kanjis], [furi])

if __name__ == '__main__':
    warifuri = Warifuri()
    if len(sys.argv) < 2:
        print('Usage: {} kanjidic2.xml [other_readings.csv] < dict.csv > dict.furi.splitted.csv'.format(sys.argv[0]))
        sys.exit(1)
    warifuri.load_kanjidic_readings(sys.argv[1])
    try:
        warifuri.load_csv_readings(sys.argv[2])
    except IndexError:
        pass
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

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
            'た':'だ','ち':'ぢじ','つ':'づず','て':'で','と':'ど',
            'は':'ばぱ','ひ':'びぴ','ふ':'ぶぷ','へ':'べぺ','ほ':'ぼぽ',
        }
        self.rendaku_map = str.maketrans(rendaku)
        self.rendaku = list(rendaku)
        self.okurigana_map = {
            'う':'いう', 'く':'きく', 'ぐ':'ぎぐ', 'す':'しす',
            'つ':'ちつ', 'ぶ':'びぶ', 'む':'みむ', 'る':'りる',
            'ぬ':'にぬ', 'い':'い'
        }
        self.okurigana_first_char = [
            'い', 'え', 'け', 'げ', 'き', 'せ', 'て', 'ち', 'び',
            'め', 'み', 'れ', 'り',
        ]
        self.readings = {}
        self.jukujikuns = {}
        self.jukujikuns_list = []

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
                    okuriganas = self.okurigana_map[okurigana]
                    for char in list(okuriganas):
                        inflections.append(base + char)
                except KeyError:
                    if (len(okurigana) > 1
                        and okurigana[0] in self.okurigana_first_char):
                        inflections.append(base + okurigana[0])
        return inflections

    def get_rendaku_variants(self, readings):
        rendakus = []
        for reading in filter(lambda r: len(r) and r[0] in self.rendaku, readings):
            rendaku = reading[0].translate(self.rendaku_map)
            for char in list(rendaku):
                rendakus.append(char + reading[1:])
        return rendakus

    def load_kanji_readings(self, kanji, readings):
        readings = readings + self.get_okurigana_inflections(readings)
        readings = [self.filter_kanjidict_reading(r) for r in readings]
        sokuon = [ 'つ', 'ち', 'く', 'き']
        for reading in filter(lambda r: r[-1] in sokuon and len(r) > 1, readings):
            readings.append(reading[0:-1] + 'っ')
        readings = readings + self.get_rendaku_variants(readings)
        return readings

    def add_jukujikun_readings(self, kanjis, readings):
        new_readings = []
        for reading in readings:
            # Strip kana
            reading_stripped = []
            i = 0
            for r in reading.split('|'):
                if kanjis[i] == r:
                    kanjis = kanjis[:i] + kanjis[i+1:]
                else:
                    i = i + 1
                    reading_stripped.append(r)

            new_reading = []
            for r in reading_stripped:
                variants = [r]
                variants = variants + self.get_rendaku_variants(variants)
                variants = variants + [self.hira_to_kata(v) for v in variants]
                new_reading.append(variants)
            if len(new_reading) != len(kanjis):
                filler = (len(kanjis)-len(new_reading)) * ['']
                new_reading = new_reading + filler
            new_readings.append(new_reading)
        self.add_jukujikun(kanjis, new_readings)

    def add_jukujikun(self, kanjis, readings):
        try:
            previous = self.jukujikuns[kanjis]
        except KeyError:
            previous = []
            pos = 0
            for jukujikun in self.jukujikuns_list:
                if len(jukujikun) < len(kanjis):
                    break
                pos = pos + 1
            self.jukujikuns_list.insert(pos, kanjis)
        self.jukujikuns[kanjis] = previous + readings

    def add_readings(self, kanjis, readings):
        if len(kanjis) == 1:
            readings = self.load_kanji_readings(kanjis, readings)
            readings = list(set(readings))
            readings = readings + [self.hira_to_kata(r) for r in readings]
        else:
            self.add_jukujikun_readings(kanjis, readings)
        if len(kanjis) == 1:
            code = ord(kanjis)
            try:
                previous = self.readings[code]
            except KeyError:
                previous = []
            self.readings[code] = previous + readings

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
                self.add_readings(char, readings)

    def load_csv_readings(self, filename):
        with open(filename, newline='') as csvfile:
            readings_reader = csv.reader(csvfile, delimiter='\t')
            try:
                for row in readings_reader:
                    if len(row) == 0 or row[0][0] == '#':
                        continue
                    try:
                        kanjis, readings = row[0], [row[1]]
                    except IndexError:
                        sys.exit('file {}, line {}: malformed line'.format(filename, readings_reader.line_num))
                    self.add_readings(kanjis, readings)
            except csv.Error as e:
                sys.exit('file {}, line {}: {}'.format(filename, readings_reader.line_num, e))

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
        anything = [[ False, '', ['.+'] ]]
        anything = anything + [[ False, '', [''] ]] * (len(kanjis)-1)
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
            for jukujikun in self.jukujikuns_list:
                readings = self.jukujikuns[jukujikun]
                pos = 0
                while True:
                    try:
                        pos = kanjis.index(jukujikun, pos)
                    except ValueError:
                        break
                    j_paths = []
                    for reading in readings:
                        j_path = [ [False, '', r] for r in reading ]
                        j_paths.append(tuple(j_path))
                    replacement = [ j_paths + [tuple(paths[pos:pos+len(jukujikun)])] ]
                    paths[pos:pos+len(jukujikun)] = [replacement]
                    kanjis = kanjis[:pos] + ' ' + kanjis[pos+len(jukujikun):]
                    pos = pos + 1
            return tuple(paths)
        elif type(paths) is list and type(paths[0]) is not bool:
            for i, path in enumerate(paths):
                paths[i] = self.add_jukujikun_paths(path)
        return paths

    def split_furi(self, kanjis, furi):
        paths = []
        # Python re compatible form of (?P<rest>[\p{Hiragana}\p{Katakana}ー]+)|(?P<kanji>.)
        # Generated using http://www.unicode.org/Public/UCD/latest/ucd/Scripts.txt
        regex = r'(?P<rest>[\u3041-\u3096\u309D-\u309E\u309F\u30A1-\u30FA\u30FD-\u30FE\u30FF\u31F0-\u31FF\u30FC]+)|(?P<kanji>.)'
        segments = []
        for match in re.finditer(regex, kanjis):
            segments.append(match.group(0))
            token = match.groupdict()
            if token['kanji']:
                try:
                    readings = self.readings[ord(token['kanji'])]
                except KeyError:
                    readings = [ re.escape(token['kanji']) ]
                paths.append([ True, token['kanji'], readings ])
            else:
                segment = token['rest']
                readings = [ segment, self.hira_to_kata(segment) ]
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
            if i > 0 and groups[i] == '' and s < len(segments):
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
    if len(sys.argv) > 2:
        warifuri.load_csv_readings(sys.argv[2])
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

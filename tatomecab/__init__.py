# coding: utf-8

import MeCab

class TatoMeCab():
    tagger = MeCab.Tagger('')
    kill_readings = u"1234567890１２３４５６７８９０"

    def __init__(self):
        kata = u"ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶ"
        hira = u"ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖ"
        self.kata_to_hira_map = dict((ord(kata[i]), hira[i]) for i in range(len(kata)))
        punct = u"ー・"
        self.chars_without_furi = dict((ord(char), None) for char in kata + hira + punct)

    def kata_to_hira(self, kata_str):
        return kata_str.translate(self.kata_to_hira_map)

    def needs_furigana(self, string):
        for char in string:
            if not ord(char) in self.chars_without_furi:
                return False
        return True

    def split_feature(self, line):
        cols = []
        quote = False
        col = u""
        for char in line:
            if char == '"':
                quote = not quote
            elif char == ',' and not quote:
                cols.append(col)
                col = u""
            else:
                col = col + char
        cols.append(col)
        return cols

    def get_reading(self, line):
        cols = self.split_feature(line)
        try:
            return cols[7]
        except IndexError:
            return u''

    def strip_unneeded_readings(self, tokens):
        return [(kanjis, None) if kanjis == reading or self.needs_furigana(kanjis) or kanjis == '"' else (kanjis, reading) for kanjis, reading in tokens]

    def parse_furi(self, kanjis, furigana):
        parsed = []
        furi = furigana.split('.')
        if len(furi) == 1:
            if kanjis in self.kill_readings:
                furigana = ''
            parsed.append((kanjis, furigana))
        else:
            for i in range(len(kanjis)):
                kanji = kanjis[i]
                try:
                    reading = furi[i]
                except IndexError:
                    reading = ''
                if len(reading) == 0:
                    prev = parsed.pop()
                    token = (prev[0] + kanji, prev[1])
                else:
                    token = (kanji, reading)
                parsed.append(token)
        return self.strip_unneeded_readings(parsed)

    def parse(self, text):
        node = self.tagger.parseToNode(text)
        tokens = []
        while node:
            if node.stat != MeCab.MECAB_BOS_NODE and \
               node.stat != MeCab.MECAB_EOS_NODE:
                space_len = node.rlength - node.length
                if space_len > 0:
                    spaces = ' ' * space_len
                    tokens.append([(spaces, None)])
                try:
                    kanjis = node.surface.decode('utf-8')
                except AttributeError: # Python 2 backward compatibility
                    kanjis = node.surface
                try:
                    reading = self.get_reading(node.feature.decode('utf-8'))
                except AttributeError: # Python 2 backward compatibility
                    reading = self.get_reading(node.feature)
                reading = self.kata_to_hira(reading)
                tokens.append(self.parse_furi(kanjis, reading))
            node = node.next
        return tokens

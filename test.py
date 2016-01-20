#!/usr/bin/python

import warifuri
import unittest

class WarifuriTest(unittest.TestCase):
    def setUp(self):
        self.warifuri = warifuri.Warifuri()
        all_readings = {
            '間': ['カン', 'ケン', 'あいだ', 'ま', 'あい'],
            '接': ['セツ', 'ショウ', 'つ.ぐ'],
            '男': ['ダン', 'ナン', 'おとこ', 'お'],
            '子': ['シ', 'ス', 'ツ', 'こ', '-こ', 'ね'],
            '勉': ['ベン', 'つと.める'],
            '絶': ['ゼツ', 'た.える', 'た.やす', 'た.つ'],
            '対': ['タイ', 'ツイ', 'あいて', 'こた.える', 'そろ.い',
                   'つれあ.い', 'なら.ぶ', 'むか.う'],
            '八': ['ハチ', 'や', 'や.つ', 'やっ.つ', 'よう'],
            '歳': ['サイ', 'セイ', 'とし', 'とせ', 'よわい'],
            '学': ['まな.ぶ', 'ガク'],
            '校': ['コウ', 'キョウ'],
            '石': ['セキ', 'シャク', 'コク', 'いし'],
            '鹸': ['ケン', 'カン', 'セン', 'あ.く'],
            '仕': ['シ', 'ジ', 'つか.える'],
            '舞': ['ブ', '-ま.う', 'まい'],
            '双': ['ソウ', 'ふた', 'たぐい', 'ならぶ', 'ふたつ'],
            '一': ['イチ', 'イツ', 'ひと-', 'ひと.つ'],
            '発': ['ハツ', 'ホツ', 'た.つ', 'あば.く', 'おこ.る', 'つか.わす', 'はな.つ'],
            '差': ['サ', 'さ.す', 'さ.し'],
            '入': ['ニュウ', 'ジュ', 'い.る', '-い.る', '-い.り',
                   'い.れる', '-い.れ', 'はい.る'],
            '人': [ 'ジン', 'ニン', 'ひと', '-り', '-と'],
            '暮': [ 'ボ', 'く.れる', 'く.らす' ],
            '一人': [ 'ひとり' ],
        }
        for kanjis, readings in all_readings.items():
            self.warifuri.load_readings(kanjis, readings)

    def assert_split_furi(self, kanjis, readings):
        result = self.warifuri.split_furi(''.join(kanjis), ''.join(readings))
        self.assertEqual((kanjis, readings), result)

    def assert_cant_split_furi(self, kanjis, readings):
        readings = ''.join(readings)
        kanjis = ''.join(kanjis)
        result = self.warifuri.split_furi(kanjis, readings)
        self.assertEqual(([kanjis], [readings]), result)

    def test_unknown_reading(self):
        self.assert_cant_split_furi(['間','接'], ['あれ','あれれ'])

    def test_simple(self):
        self.assert_split_furi(['間','接'], ['かん','せつ'])

    def test_katakana(self):
        self.assert_split_furi(['間','接'], ['カン','セツ'])
        self.assert_split_furi(['仕','舞','い'], ['シ','マ','イ'])

    def test_kana_mix(self):
        self.assert_split_furi(['男','の','子'], ['おとこ','の','こ'])
        self.assert_split_furi(['ノー', '勉',], ['ノー', 'べん',])

    def test_opportunistic_split(self):
        self.assert_split_furi(['男','の','子'], ['Xのの','の','こ'])
        self.assert_split_furi(['男','の','子'], ['おとこ','の','ののX'])
        self.assert_split_furi(['男','の','子'], ['X','の','Y'])
        self.assert_split_furi(['男子','の','子'], ['Xのの','の','こ'])
        self.assert_split_furi(['男','の','男子'], ['おとこ','の','ののX'])
        self.assert_split_furi(['男','子','の','子'], ['だん','し','の','X'])
        self.assert_split_furi(['男','の','男','子'], ['X','の','だん','し'])
        self.assert_split_furi(['お','好','み','焼'], ['お','X','み','X'])

    def test_unknown_kanji(self):
        self.assert_cant_split_furi(['子','供'], ['こ','ども'])

    def test_metachar(self):
        self.assert_split_furi(['(',], ['(',])
        self.assert_split_furi(['?',], ['?',])

    def test_unknown_suffix(self):
        self.assert_split_furi(['撫','でる'], ['ぶぶー','でる'])

    def test_unknown_prefix(self):
        self.assert_split_furi(['つけ','方'], ['つけ','ぶぶー'])

    def test_unknown_suffix_and_prefix(self):
        self.assert_split_furi(['お','試','し'], ['お','ぶぶー','し'])

    def test_no_kanji(self):
        self.assert_cant_split_furi(['ノーパン'], ['ノーパン'])
        self.assert_cant_split_furi(['かた','パン'], ['カタ','パン'])

    def test_empty_reading(self):
        self.assert_split_furi(['空'], [''])

    def test_sokuonka(self):
        self.assert_split_furi(['絶','対'], ['ぜっ','たい']) # つ
        self.assert_split_furi(['八','歳'], ['はっ','さい']) # ち
        self.assert_split_furi(['学','校'], ['がっ','こう']) # く
        self.assert_split_furi(['石','鹸'], ['せっ','けん']) # き

    def test_rendaku(self):
        self.assert_split_furi(['双','子'], ['ふた','ご'])
        self.assert_split_furi(['一','発'], ['いっ','ぱつ'])

    def test_omitted_okurigana(self):
        self.assert_split_furi(['差','入'], ['さし', 'いれ'])

    def test_match_until_the_end_of_the_reading(self):
        self.assert_split_furi(['舞'], ['まい'])

    def test_hito_not_broken_down(self):
        self.assert_split_furi(['一人'], ['ひとり'])
        self.assert_split_furi(['二人'], ['ふたり'])

    def test_jukujikun(self):
        self.assert_split_furi(['一人', '暮', 'らし'], ['ひとり', 'ぐ', 'らし'])

if __name__ == '__main__':
    unittest.main()

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
        }
        for kanji, readings in all_readings.items():
            self.warifuri.load_readings(kanji, readings)

    def assert_split_furi(self, kanjis, readings):
        result = self.warifuri.split_furi(''.join(kanjis), ''.join(readings))
        self.assertEqual([kanjis, readings], result)

    def assert_cant_split_furi(self, kanjis, readings):
        readings = ''.join(readings)
        kanjis = ''.join(kanjis)
        result = self.warifuri.split_furi(kanjis, readings)
        self.assertEqual([(kanjis,), (readings,)], result)

    def test_cant_split(self):
        expected = [ ('間接',), ('あれあれれ',) ]
        self.assert_cant_split_furi(('間','接'), ('あれ','あれれ'))

    def test_simple(self):
        self.assert_split_furi(('間','接'), ('かん','せつ'))

    def test_katakana(self):
        self.assert_split_furi(('間','接'), ('カン','セツ'))
        self.assert_split_furi(('仕','舞','い'), ('シ','マ','イ'))

    def test_kana_mix(self):
        self.assert_split_furi(('男','の','子'), ('おとこ','の','こ'))
        self.assert_split_furi(('ノー', '勉',), ('ノー', 'べん',))

    def test_unknown_kanji(self):
        self.assert_cant_split_furi(('子','供'), ('こ','ども'))

    def test_metachar(self):
        self.assert_split_furi(('(',), ('(',))

    def test_sokuonka(self):
        self.assert_split_furi(('絶','対'), ('ぜっ','たい')) # つ
        self.assert_split_furi(('八','歳'), ('はっ','さい')) # ち
        self.assert_split_furi(('学','校'), ('がっ','こう')) # く
        self.assert_split_furi(('石','鹸'), ('せっ','けん')) # き

if __name__ == '__main__':
    unittest.main()

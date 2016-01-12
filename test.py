#!/usr/bin/python

import warifuri
import unittest

class WarifuriTest(unittest.TestCase):
    def setUp(self):
        self.warifuri = warifuri.Warifuri()
        all_readings = {
            '間': ['かん'],   '接': ['せつ'],
            '男': ['おとこ'], '子': ['こ'],
            '勉': ['べん'],
            '絶': ['ぜつ'],   '対': ['たい'],
            '八': ['はち'],   '歳': ['さい'],
            '学': ['がく'],   '校': ['こう'],
            '石': ['せき'],   '鹸': ['けん'],
            '仕': ['し'],     '舞': ['ま.う'],
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

    def test_simple_kata(self):
        self.assert_split_furi(('間','接'), ('カン','セツ'))

    def test_kana_mix(self):
        self.assert_split_furi(('男','の','子'), ('おとこ','の','こ'))
        self.assert_split_furi(('ノー', '勉',), ('ノー', 'べん',))

    def test_unknown_kanji(self):
        self.assert_cant_split_furi(('子','供'), ('こ','ども'))

    def test_sokuonka(self):
        self.assert_split_furi(('絶','対'), ('ぜっ','たい')) # つ
        self.assert_split_furi(('八','歳'), ('はっ','さい')) # ち
        self.assert_split_furi(('学','校'), ('がっ','こう')) # く
        self.assert_split_furi(('石','鹸'), ('せっ','けん')) # き

if __name__ == '__main__':
    unittest.main()

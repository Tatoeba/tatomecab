#!/usr/bin/python

import warifuri
import unittest

class WarifuriTest(unittest.TestCase):
    def setUp(self):
        self.warifuri = warifuri.Warifuri()
        self.warifuri.readings = {
            ord('間'): ['かん'],   ord('接'): ['せつ'],
            ord('男'): ['おとこ'], ord('子'): ['こ'],
        }

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

    def test_unknown_kanji(self):
        self.assert_cant_split_furi(('子','供'), ('こ','ども'))

if __name__ == '__main__':
    unittest.main()

# Tatomecab
A wrapper around mecab for the [Tatoeba](https://tatoeba.org/) project.

Tatomecab is of a set of tools to provide Japanese sentences with furiganas.

#### tatomecab.py

A library that wraps Mecab and add some more features
(like parsing markers set by warifuri). It can also be
used as a command line to do quick testing like mecab:
```sh
$ echo 振り仮名をつけろう | ./tatomecab.py
振	ふ
り	None
仮	が
名	な
を	None
つけろ	None
う	None
```

#### webserver.py

Exposes the tatomecab library as a webservice.

```sh
$ curl http://127.0.0.1:8842/furigana?str=振り仮名をつけろう
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
<parse>
<token>
  <reading furigana="ふ"><![CDATA[振]]></reading>
  <![CDATA[り]]>
  <reading furigana="が"><![CDATA[仮]]></reading>
  <reading furigana="な"><![CDATA[名]]></reading>
</token>
<token><![CDATA[を]]></token>
<token><![CDATA[つけろ]]></token>
<token><![CDATA[う]]></token>
</parse>
</root>
```

## Warifuri
Warifuri is a script that edits mecab dictionary to insert markers in the
reading field so that furigana(s) are mapped to the character(s) they belong
to, enabling proper [mono ruby and group ruby](https://ja.wikipedia.org/wiki/%E3%83%AB%E3%83%93#.E3.82.B0.E3.83.AB.E3.83.BC.E3.83.97.E3.83.AB.E3.83.93.E3.81.A8.E3.83.A2.E3.83.8E.E3.83.AB.E3.83.93).

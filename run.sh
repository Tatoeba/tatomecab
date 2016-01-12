#!/bin/sh

set -e

maybe_download() {
   local file=$1 url=$2
   if [ ! -e "$file" ]; then
       wget -O "$file" "$url"
   fi
}

maybe_download kanjidic2.xml.gz http://www.csse.monash.edu/~jwb/kanjidic2/kanjidic2.xml.gz
if [ ! -e kanjidic2.xml ]; then
    gunzip -k kanjidic2.xml.gz
fi

DICT_BASE_NAME=mecab-naist-jdic-0.6.3b-20111013
maybe_download "$DICT_BASE_NAME.tar.gz" "http://osdn.jp/frs/redir.php?m=rwthaachen&f=%2Fnaist-jdic%2F53500%2Fmecab-naist-jdic-0.6.3b-20111013.tar.gz"
if [ ! -d "$DICT_BASE_NAME" ]; then
    tar xf "$DICT_BASE_NAME.tar.gz"
fi

for csv in $DICT_BASE_NAME/*.csv; do
    echo "Processing $csv..."
    PYTHONIOENCODING=EUC-JP ./warifuri.py ./kanjidic2.xml < "$csv" > "$csv".new \
        && mv "$csv".new "$csv"
done

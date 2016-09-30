"""Render alignments"""

import sys
from align import *

if __name__ == "__main__":
    """Usage: render.py data.zh data.en data.gold data.guess"""
    data_paths = sys.argv[1:5]
    data_files = [open(f) for f in data_paths]

    for i, (zh, en, gold, guess) in enumerate(zip(*data_files)):
        zh_words = zh.lower().strip().split(' ')
        en_words = en.lower().strip().split(' ')
        gold_align = Aligned(zh_words, en_words, gold.strip())
        guess_align = Aligned(zh_words, en_words, guess.strip())
        print("Alignment %d:" % i)
        print(gold_align.render(guess_align.sure))

"""Compute AER and phrase F1 of a predicted set of alignments."""

import os
import sys

from phrase_eval import PhraseF1, extract

class AER:
    "Alignment error rate metric sufficient statistics."
    def __init__(self):
        self.guess = 0
        self.sure = 0
        self.guess_sure = 0
        self.guess_possible = 0
    def precision(self):
        return self.guess_possible / self.guess
    def recall(self):
        return self.guess_sure / self.sure
    def combined(self):
        return 1-(self.guess_sure+self.guess_possible)/(self.guess+self.sure)
    def add(self, guess, sure, possible):
        "Add statistics for sets of links guess, sure, and possible."
        self.guess += len(guess)
        self.sure += len(sure)
        self.guess_sure += len(guess.intersection(sure))
        self.guess_possible += len(guess.intersection(sure.union(possible)))

def read(path):
    """Yield sure and possible alignments."""
    for line in open(path):
        sure, possible = set(), set()
        for link in line.strip().split(' '):
            parts = link.split('-')
            j, i = map(int, parts[0:2])
            if len(parts) == 3 and parts[2]=='P':
                possible.add((j, i))
            else:
                assert len(parts) == 2, link
                sure.add((j, i))
        yield sure, possible

def print_table(gold, guess_paths, metric):
    """Print a print_table of evaluations for each file in guess_paths."""
    names = [os.path.split(p)[1][:-6] for p in guess_paths]
    pad = lambda s: ('%-' + str(max(len(p) for p in names)) + 's') % s
    print('%s\t%s\t%s\t%s' % (pad('File'), 'Prec', 'Rec', metric.__name__))
    row = lambda n,p,r,a: ('%s'+'\t%0.1f'*3) % (pad(n), 100*p, 100*r, 100*a)
    for p, name in zip(guess_paths, names):
        m = metric()
        for ((guess, _), (sure, possible)) in zip(read(p), gold):
            m.add(guess, sure, possible)
        print(row(name, m.precision(), m.recall(), m.combined()))

if __name__ == "__main__":
    # Flag -p prints extracted phrase pairs for an alignment file.
    if sys.argv[1] == '-p':
        for links in read(sys.argv[2]):
            print(sorted(extract(*links)))
        sys.exit(0)
    gold_path, guess_paths = sys.argv[1], sys.argv[2:]
    gold = list(read(gold_path))
    print_table(gold, guess_paths, AER)
    print()
    print_table(gold, guess_paths, PhraseF1)




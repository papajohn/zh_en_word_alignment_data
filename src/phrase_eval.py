"""Phrase extraction evaluation of alignments."""

import sys
from collections import namedtuple

def project(sure, possible):
    """Return the aligned spans (jstart, jend) for each i."""
    spans = []
    links = sure.union(possible)
    max_i = max(k[1] for k in links)
    for i in range(max_i+1):
        js = [k[0] for k in sure if k[1] == i]
        if not js:
            js = [k[0] for k in possible if k[1] == i]
        if js:
            spans.append((min(js), max(js)+1))
        else:
            spans.append(None) # Empty span
    return spans

def union(span, other):
    """Union of two spans."""
    if span is None or other is None: return None
    return min(span[0], other[0]), max(span[1], other[1])

def consistent(ispan, ispans, jspan, jspans, size):
    """Return all spans containing jspan that project into ispan."""
    bispans = set()
    jmin, jmax = jspan
    for jstart in range(max(jmax-size, 0), jmin+1):
        projected_ispan = ispans[jstart]
        for jmiddle in range(jstart+1, jmax):
            projected_ispan = union(projected_ispan, ispans[jmiddle])
        for jend in range(jmax, min(jstart+size, len(ispans))+1):
            projected_ispan = union(projected_ispan, ispans[jend-1])
            if projected_ispan is None: continue
            # Check that ispan contains projected_ispan
            if union(ispan, projected_ispan) == ispan:
                bispans.add((ispan, (jstart, jend)))
    return bispans

def swap(links):
    return {(i, j) for (j, i) in links}

def extract(sure, possible, size=5):
    """Extract all bispans consistent with links."""
    jspans = project(sure, possible)
    ispans = project(swap(sure), swap(possible))
    bispans = set()
    for istart, jspan in enumerate(jspans):
        for iend in range(istart+1, min(istart+size, len(jspans))+1):
            ispan = (istart, iend)
            jspan = union(jspan, jspans[iend-1])
            if jspan is not None:
                bispans.update(consistent(ispan, ispans, jspan, jspans, size))
    return bispans

class PhraseF1:
    """The F1 score of extracted phrase pairs."""
    def __init__(self):
        self.correct = 0
        self.guesses = 0
        self.golds = 0
    def precision(self):
        return self.correct / self.guesses
    def recall(self):
        return self.correct / self.golds
    def combined(self):
        p, r = self.precision(), self.recall()
        return 2 * p * r / (p + r)
    def add(self, guess, sure, possible):
        guesses = extract(guess, set())
        golds = extract(sure, possible)
        self.correct += len(guesses.intersection(golds))
        self.guesses += len(guesses)
        self.golds += len(golds)



"""Align an evaluation set and render the output as a text grid."""

import sys
import hmm

class Aligned:
    """A hand-aligned parallel sentence pair."""

    def __init__(self, zh, en, align):
        """zh and en are lists of words (strings). align is moses-formatted."""
        self.zh = zh
        self.en = en

        # Sets of (zh_index, en_index) pairs
        self.sure = set()
        self.possible = set()
        self.parse(align, self.sure, self.possible)

    def parse(self, align, sure, possible):
        """Populate sets sure and possible with alignment links from
        moses-formatted align string."""
        for pair in align.split():
            parts = pair.split('-')
            link = tuple(map(int, parts[0:2]))
            assert link[0] < len(self.zh), "%d: %s" % (link[0], str(self.zh))
            assert link[1] < len(self.en), "%d: %s" % (link[1], str(self.en))
            if len(parts) == 3:
                assert parts[2] == "P", align
                possible.add(link)
            else:
                sure.add(link)

    def combine(self, forward, backward):
        """Combine forward and backward alignments by intersection."""
        guess_forward, guess_backward, _ = set(), set(), set()
        self.parse(forward, guess_forward, _)
        self.parse(backward, guess_backward, _)
        return guess_forward.intersection(guess_backward)

    def render(self, guess):
        """Render this alignment as a grid."""
        # Alignment links and horizontal labels
        link_lines = []
        for j, zh in enumerate(self.zh):
            links = []
            for i in range(len(self.en)):
                links.append(self.render_link(i, j, guess))
            link_lines.append("".join(links) + "| " + zh)
        link_lines.append("---" * len(self.en) + "'")

        # Vertical labels
        longest_en = max(len(en) for en in self.en)
        labels = [[' '] * len(self.en) for _ in range(longest_en)]
        for i, en in enumerate(self.en):
            for k, s in enumerate(en):
                labels[k][i] = s
        label_lines = [" %s " % "  ".join(line) for line in labels]
        label_lines.append("   " * len(self.en))

        return "\n".join(link_lines + label_lines)

    def render_link(self, i, j, guess):
        link = (j, i)
        s = [" "] * 3
        if link in self.sure:
            s[0], s[2] = "[", "]"
        elif link in self.possible:
            s[0], s[2] = "(", ")"
        if link in guess:
            s[1] = "#"
        return "".join(s)

if __name__ == "__main__":
    """Usage: align.py data.zh data.en data.align zh_en.json en_zh.json"""
    data_paths = sys.argv[1:4]
    model_paths = sys.argv[4:6]

    data_files = [open(f) for f in data_paths]
    zh_en_model, en_zh_model = [hmm.HMM(f) for f in model_paths]

    for i, (zh, en, align) in enumerate(zip(*data_files)):
        zh_words = zh.lower().split()
        en_words = en.lower().split()
        a = Aligned(zh_words, en_words, align.strip())
        forward = en_zh_model.align(en_words, zh_words).moses_str(False)
        backward = zh_en_model.align(zh_words, en_words).moses_str(True)
        guess = a.combine(forward, backward)
        print("Alignment %d:" % i)
        print(a.render(guess))

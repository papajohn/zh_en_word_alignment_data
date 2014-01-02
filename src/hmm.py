#!/usr/bin/env python3

"""Read and apply a variant of the HMM-based alignment model (Vogel, 96)."""

import json
import math

negative_inf = float("-Inf")

def ln(x):
    """Natural log without value errors."""
    try:
        return math.log(x)
    except ValueError:
        return negative_inf

def memoize(f):
    """Memoization decorator. Requires no varargs and immutable arguments."""
    cache = {}
    def cached(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    return cached


class Alignment:
    """A max-value word alignment, stored recursively as pairs of indices.

    score represents the best score (log probability) of aligning e_i to f_j
    and maximally aligning the rest.

    i and j are indices into the generated (English) and observed (French)
    sentences, respectively.  When j is None, e_i is null-aligned.

    rest is an Alignment or None.
    """

    def __init__(self, score, i, j=None, rest=None):
        self.score = score
        self.i = i
        self.j = j
        self.rest = rest

    def update(self, alignment):
        """If score_of(alignment) > self.score, copy alignment."""
        if alignment.score > self.score:
            self.score = alignment.score
            self.i = alignment.i
            self.j = alignment.j
            self.rest = alignment.rest

    def moses_str(self, swap=False):
        """Alignment in Moses format: j-i for aligned pairs."""
        s = ""
        if self.rest is not None:
            s += self.rest.moses_str(swap)
        if self.j is not None:
            link = (self.i, self.j) if swap else (self.j, self.i)
            s += " %d-%d" % link
        return s.strip()


class HMM:
    """An HMM-based alignment model."""

    def __init__(self, params_path='zh_en_hmm.json'):
        """params is a nested dict of model parameters.

        emission:

            align_emissions    - P(e|f) for words e and f, stored as a dict from
                                 f words to dicts from e words to P(e|f) values.

            null_emissions     - P(e|NULL) for word e, stored as a dict from e
                                 words to P(e|NULL) values.

        transition:

            align_given_align  - P(d) for signed distance d between the previous
                                 align word and the current align word,
                                 stored as a list.

                                 The probability of transitioning from position j
                                 to position k is (k-j)+max_jump.  Assumes that
                                 max_jump > maximum length of a sentence.

            max_jump           - Maximum unsigned change in align positions.

            null_given_align   - Probability of null-aligning a word, given that
                                 the previous word was align.

            null_given_null    - Probability of null-aligning a word, given that
                                 the previous word was null-align.

        """
        with open(params_path) as params_file:
          params = json.load(params_file)

        emission = params["emission"]
        self.align_emissions = emission["align_emissions"]
        self.null_emissions = emission["null_emissions"]

        transition = params["transition"]
        self.align_given_align = transition["align_given_align"]
        self.max_jump = int(transition["max_jump"])
        self.null_given_align = transition["null_given_align"]
        self.null_given_null = transition["null_given_null"]


    def align(self, e, f):
        """Return an Alignment of words e and f scored by log probability."""
        # TODO Original model transitions to len(f) after aligning e_{len(e)-1}.

        @memoize
        def max_score_align(i, j):
            """The max score of aligning up to i with e_i aligned to f_j."""
            if i == 0:
                jump = j - -1
                return max_score_align_with_jump(i, j, jump, None)
            best = max_score_align_given_null(i, j)
            for previous in range(len(f)):
                best.update(max_score_align_given_align(i, j, previous))
            return best

        def max_score_align_with_jump(i, j, jump, rest):
            """Given a jump width, combine the transition and emission models
            for an aligned word and return a corresponding Alignment.
            """
            em = ln(self.align_emissions[f[j]].get(e[i], 0))
            jump = ln(self.align_given_align[jump + self.max_jump])
            aligned = ln(1-self.null_given_align)
            trans = jump + aligned
            score = em + trans + (0 if rest is None else rest.score)
            return Alignment(score, i, j, rest)

        def max_score_align_given_align(i, j, previous):
            jump = j - previous
            rest = max_score_align(i-1, previous)
            return max_score_align_with_jump(i, j, jump, rest)

        def max_score_align_given_null(i, j):
            # TODO Original model used fixed-parameter Model 2 style transitions
            #      for an aligned word after null, which differs from other
            #      implementations (e.g., GIZA++, Berkeley Aligner) that store
            #      the position of the previously aligned word.
            jump = j - -1
            rest = max_score_null(i-1)
            return max_score_align_with_jump(i, j, jump, rest)

        @memoize
        def max_score_null(i):
            """The max score of aligning up to i with e_i aligned to null."""
            null_emission = 0  # Experiments didn't include null emissions.
            given_align = ln(self.null_given_align) + null_emission
            given_null = ln(self.null_given_null) + null_emission
            if i == 0:
                return Alignment(given_align, i)
            rest_null = max_score_null(i-1)
            best = Alignment(given_null + rest_null.score, i, None, rest_null)
            for previous in range(len(f)):
                rest_align = max_score_align(i-1, previous)
                score = given_align + rest_align.score
                best.update(Alignment(score, i, None, rest_align))
            return best

        final_i = len(e)-1
        best = max_score_null(final_i)
        for j in range(len(f)):
            best.update(max_score_align(final_i, j))
        return best

if __name__ == "__main__":
    """Align a single example sentence."""

    en = "Indonesia Reiterated its Opposition to Foreign Military Presence"
    en_words = en.lower().split()
    zh = "印 尼 重申 反对 外国 军队 进驻"
    zh_words = zh.lower().split()

    en_zh_hmm = HMM("en_zh_hmm.json")
    print(en_zh_hmm.align(en_words, zh_words).moses_str(False))

    zh_en_hmm = HMM("zh_en_hmm.json")
    print(zh_en_hmm.align(zh_words, en_words).moses_str(True))


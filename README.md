zh_en_word_alignment_data
=========================

This repository contains data and parameters to replicate experiments in the
following paper.

Model-Based Aligner Combination Using Dual Decomposition
John DeNero and Klaus Macherey
ACL 2011
http://denero.org/content/pubs/acl11_denero_dual.pdf

This repository has several components, listed below.  It *does not* contain an
implementation of the bidirectional model described in the paper. It does
contain a simple reference implementation of the HMM-based alignment model
baseline (Vogel, '96).

(1) *zh_en_data* contains the tokenized, labeled evaluation data. It is a small
    hand-aligned subset of the NIST 2002 MT evaluation set.

(2) *hmm_models* contains the parameters of HMM-based alignment models trained
    to generate English given Chinese and Chinese given English. These are
    trained on the LDC FBIS corpus. The data format and interpretation is
    described in src/hmm.py files.

(3) *src* contains hmm.py, which reads and applies an HMM-based alignment model.
    It also contains align.py, which reads a dataset and applies two models to
    each sentence, rendering a text grid of the intersection of their output.

(4) *output* contains text grid renderings of the alignments evaluated in Table
    2 of the paper.

(5) *align.sh* runs src/align.py on zh_en_data using hmm_models.

*Note*: This implementation in src/hmm.py is not the original one used to
conduct experiments, nor is it efficient for performing word alignment of full
corpora. It exists only to clarify the interpretation of parameters files.

*Warning*: This implementation is not an exact replication of the original
aligner. Known differences are marked as TODO's in the code.  Small unknown
differences exist as well.  In the initial release of this dataset,
approximately 1% of words have different Viterbi alignments from those used in
the original implementation in one alignment model or the other. Hopefully,
those differences will be identified and removed in future updates.


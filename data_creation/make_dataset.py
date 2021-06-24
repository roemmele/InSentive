import os
import sys
sys.path.append("../")

import argparse
import random
import math
import re
import numpy
import itertools
import spacy

spacy_model = spacy.load('en_core_web_sm', disable=['ner'])
numpy.random.seed(0)


def syntax_drop_spacy_sentence(head_token, level=0, trim_multiplier=50):
    if level > 0:
        filter_prob = (1 / (1 + (((1 / numpy.sqrt(len(head_token.sent)) * trim_multiplier)
                                  * numpy.exp(-(level))))))
    else:
        filter_prob = 0.0
    rand_num = numpy.random.rand()
    if rand_num < filter_prob:
        return []  # Filter the dependent phrase associated with this token
    left_dependents = list(head_token.lefts)
    right_dependents = list(head_token.rights)
    left_phrase = [syntax_drop_spacy_sentence(head_token=dependent,
                                              level=level + 1) for dependent in left_dependents]
    right_phrase = [syntax_drop_spacy_sentence(head_token=dependent,
                                               level=level + 1) for dependent in right_dependents]
    return (list(itertools.chain(*left_phrase))
            + [head_token]
            + list(itertools.chain(*right_phrase)))


def random_drop_spacy_sentence(spacy_sent,
                               min_drop_rate=0.6,
                               min_open_class_prop=0.5):

    result_sent = []
    # Vary token-level drop rate across sentences from 0 up to max_drop_rate
    drop_rate = numpy.random.rand() * (1 - min_drop_rate)
    n_result_tokens = max(1, int(len(spacy_sent) * drop_rate))

    token_is_open_class_fn = (lambda spacy_token:
                              spacy_token.pos_ in set(['ADJ', 'INTJ', 'NOUN',
                                                       'NUM', 'PROPN', 'VERB']))

    n_min_open_class_tokens = max(1, int(n_result_tokens * min_open_class_prop))
    result_token_idxs = set(numpy.random.permutation(len(spacy_sent))[:n_result_tokens])
    open_class_token_idxs = [token_idx for token_idx, token in enumerate(spacy_sent)
                             if token_is_open_class_fn(token)]
    random.shuffle(open_class_token_idxs)
    min_open_class_token_idxs = set(open_class_token_idxs[:n_min_open_class_tokens])

    for token_idx, token in enumerate(spacy_sent):
        if token_idx in result_token_idxs or token_idx in min_open_class_token_idxs:
            result_sent.append(token)

    if not (result_sent or (result_sent[0].text != ' ' if len(result_sent) == 1 else True)):
        print("warning: blank sentence after dropping, setting sentence to random token")
        rand_idx = numpy.random.permutation(len(spacy_sent))
        result_sent.append(spacy_sent[rand_idx])

    return result_sent


def make_dataset(args):

    if args.data_dir is not None:
        def _read_file(filename):
            with open(filename) as f:
                return f.read().strip()

        texts = (line.strip() for filename in os.listdir(args.data_dir)
                 for line in _read_file(os.path.join(args.data_dir, filename)).split("\n"))
    else:
        assert args.data_file is not None
        texts = (line.strip() for line in open(args.data_file))

    if not os.path.exists(args.output_data_dir):
        os.mkdir(args.output_data_dir)

    with open(os.path.join(args.output_data_dir, "sents.src"), 'w') as src_f,\
            open(os.path.join(args.output_data_dir, "sents.tgt"), 'w') as tgt_f:
        src_sents, tgt_sents = [], []

        n_pairs = 0

        for text_idx, spacy_text in enumerate(spacy_model.pipe(
                texts, batch_size=args.batch_size, n_process=args.n_threads)):
            try:
                for spacy_sent in spacy_text.sents:
                    if len(spacy_sent) < args.min_tgt_length:  # Length requirement
                        continue
                    if args.filter_quotes:  # No quotes requirement
                        token_set = set([token.text for token in spacy_sent])
                        if ("\"" in token_set or "'" in token_set
                                or "`" in token_set or "``" in token_set or "''" in token_set):
                            continue
                    for src_idx in range(args.n_src_per_tgt):
                        if len(args.drop_methods) == 2:  # Randomly select between syntax and random dropping if both specified
                            drop_method = args.drop_methods[round(random.random())]
                        else:
                            drop_method = args.drop_methods[0]
                        if drop_method == 'syntax':
                            root_token = [token for token in spacy_sent if token.head == token][0]
                            spacy_sent_with_drop = syntax_drop_spacy_sentence(head_token=root_token,
                                                                              trim_multiplier=args.trim_multiplier)
                        elif drop_method == 'random':
                            spacy_sent_with_drop = random_drop_spacy_sentence(spacy_sent,
                                                                              min_drop_rate=args.min_drop_rate,
                                                                              min_open_class_prop=args.min_open_class_prop)
                        src_sent = ""
                        for token in spacy_sent_with_drop:
                            if token.i > 0:
                                if spacy_text[token.i - 1].text.endswith("\n"):
                                    src_sent = src_sent.strip() + " " + token.text_with_ws
                                else:
                                    src_sent += (spacy_text[token.i - 1].whitespace_
                                                 + token.text_with_ws)
                            else:
                                src_sent += token.text_with_ws
                        src_sent = re.sub("\s+", " ", src_sent).strip()
                        if args.lowercase_src:
                            src_sent = src_sent.lower()
                        tgt_sent = re.sub("\s+", " ", spacy_sent.text).strip()
                        src_sents.append(src_sent)
                        tgt_sents.append(tgt_sent)
                        n_pairs += 1

                if (text_idx + 1) % 10 == 0:
                    print("processed {} texts...".format(text_idx + 1))
                    src_f.write("\n".join(src_sents))
                    tgt_f.write("\n".join(tgt_sents))
                    src_sents, tgt_sents = [], []

            except (ValueError, MemoryError):  # Possible memory error with large text
                print("Error processing text {}, skipping...".format(text_idx + 1))
                continue

        src_f.write("\n".join(src_sents))
        tgt_f.write("\n".join(tgt_sents))
        print("Saved", n_pairs, "source-target pairs to", args.output_data_dir)


def main():
    parser = argparse.ArgumentParser(description="Create sentence elaboration dataset from raw text files.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--output_data_dir", "-output_data_dir", help="Specify directory path where generated dataset (source and target segments) will be saved.",
                        type=str, required=True)

    parser.add_argument("--data_dir", "-data_dir", help="Provide the path to the directory that contains the dataset. It is assumed that the directory is flat, with one or more text files (one text per file).",
                        type=str, required=False, default=None)

    parser.add_argument("--data_file", "-data_file", help="Provide the path to the file that contains the data used to derive source-target pairs (assumed to be one text per line).",
                        type=str, required=False, default=None)

    parser.add_argument("--drop_methods", "-drop_methods", nargs='+', help="Specify method(s) for dropping tokens from original sentence in order to derive source sentence.",
                        type=str, required=False, choices=['syntax', 'random'], default=['random'])
    parser.add_argument("--n_src_per_tgt", "-n_src_per_tgt", help="Specify the number of ablations to produce for each sentence in the dataset,\
                                                                which will equal the total number of source-target pairs for a given sentence.",
                        type=int, required=False, default=1)
    parser.add_argument("--min_tgt_length", "-min_tgt_length", help="Specify minimum length of target sentences as criteria for inclusion in dataset.",
                        type=int, required=False, default=1)
    parser.add_argument("--min_drop_rate", "-min_drop_rate", help="If drop methods include 'random', specify minimum proportion of tokens that will be removed from each target sentence in order to derive the source sentence.",
                        type=float, required=False, default=0.6)
    parser.add_argument("--min_open_class_prop", "-min_open_class_prop", help="If drop methods include 'random', specify minimum proportion of open-class (content) tokens (i.e. nouns, verbs, adjectives) that should be preserved in the source sentences\
                        (i.e. resulting source sentence will contain at least this proportion of open-class words relative to overall tokens).",
                        type=float, required=False, default=0.5)
    parser.add_argument("--trim_multiplier", "-trim_multiplier", help="If drop methods include 'syntax', specify how aggessively to filter (trim) dependent tokens. Higher numbers result in more dropped tokens.",
                        type=int, required=False, default=50)
    parser.add_argument("--lowercase_src", "-lowercase_src", help="Convert all tokens in derived source sentences to lowercase.",
                        action='store_true', required=False)
    parser.add_argument("--filter_quotes", "-filter_quotes", help="Filter source-target pairs where the target contains a quotation mark.",
                        action='store_true', required=False)
    parser.add_argument("--batch_size", "-batch_size", help="Specify batch size for spacy processing.",
                        type=int, required=False, default=100)
    parser.add_argument("--n_threads", "-n_threads", help="Specify number of threads for spacy processing.",
                        type=int, required=False, default=3)
    args = parser.parse_args()
    print(vars(args))

    make_dataset(args)

if __name__ == '__main__':
    main()

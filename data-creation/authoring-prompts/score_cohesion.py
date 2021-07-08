import os
import sys
sys.path.append("../")

import argparse
import spacy
import json
from transformers import pipeline

from utils.dataset import Dataset


def score(args):

    if args.input_file:
        dataset = Dataset()
        dataset.set_texts_from_file(filepath=args.input_file,
                                    partition=None)
    else:
        dataset = Dataset.get_dataset_from_alias(args.dataset_name)(args.data_dir)

    sents = dataset.get_texts(partition=args.partition)

    spacy_model = spacy.load('en_core_web_lg')
    predictor = pipeline("fill-mask")

    scores_output = []
    n_outputs = 0

    for idx, sent in enumerate(sents):
        spacy_sent = spacy_model(sent)

        if args.min_sent_length and len(spacy_sent) < args.min_sent_length:
            continue
        if args.max_sent_length and len(spacy_sent) > args.max_sent_length:
            continue

        tokens = []
        tokens_are_stop = []
        tokens_are_spacy_oov = []
        tokens_are_bert_oov = []
        tokens_are_punct = []
        tokens_are_space = []
        tokens_are_digit = []
        tokens_are_entity = []
        scores = []

        for token in spacy_sent:

            target_token = ' ' + token.text

            tokens_are_stop.append(token.is_stop)
            tokens_are_spacy_oov.append(token.is_oov)
            tokens_are_punct.append(token.is_punct)
            tokens_are_space.append(token.is_space)
            tokens_are_digit.append(token.is_digit)
            tokens_are_entity.append(bool(token.ent_type))
            token_is_bert_oov = len(predictor.tokenizer.tokenize(target_token)) != 1
            tokens_are_bert_oov.append(token_is_bert_oov)

            masked_sent = (sent[:token.idx] +
                           predictor.tokenizer.mask_token +
                           sent[token.idx + len(token):])
            token_score = predictor(masked_sent,
                                    targets=target_token)[0]['score']

            tokens.append(token.text)
            scores.append(token_score)

        scores_output.append({'tokens': tokens,
                              'is_stop': tokens_are_stop,
                              'is_spacy_oov': tokens_are_spacy_oov,
                              'is_bert_oov': tokens_are_bert_oov,
                              'is_punct': tokens_are_punct,
                              'is_space': tokens_are_space,
                              'is_digit': tokens_are_digit,
                              'is_entity': tokens_are_entity,
                              'scores': scores})
        n_outputs += 1

        if n_outputs % 1000 == 0:
            with open(args.output_file, 'w') as f:
                json.dump(scores_output, f)
            print("Saved", n_outputs, "sentence outputs to", args.output_file)

    with open(args.output_file, 'w') as f:
        json.dump(scores_output, f)
    print("Saved", n_outputs, "sentence outputs to", args.output_file)

    return scores_output


def main():
    parser = argparse.ArgumentParser(description="Score token likelihood in sentences using masked DistillBERT LM.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--output_file", "-output_file", help="Specify filepath where score output will be saved. Output is JSON format.",
                        type=str, required=True)
    parser.add_argument("--input_file", "-input_file", help="Specify input file with sentences to score (one sentence per line).",
                        type=str, required=False, default=None)
    parser.add_argument("--dataset_name", "-dataset_name", help="As alternative to providing input file,\
                        specify name of dataset for sentences to score.",
                        type=str, required=False, choices=list(Dataset.get_dataset_aliases().keys()))
    parser.add_argument("--data_dir", "-data_dir", help="Provide the path to the directory that contains the dataset.",
                        type=str, required=False, default=None)
    parser.add_argument("--partition", "-partition", help="Specify which partition of the dataset to get texts from.",
                        type=str, required=False, default=None)
    parser.add_argument("--min_sent_length", "-min_sent_length", help="Only process sentences with N>=min_sent_length number of tokens.",
                        type=int, required=False, default=None)
    parser.add_argument("--max_sent_length", "-max_sent_length", help="Only process sentences with N<=max_sent_length number of tokens.",
                        type=int, required=False, default=None)
    args = parser.parse_args()
    print(vars(args))

    scores_output = score(args)

if __name__ == '__main__':
    main()

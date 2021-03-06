import os
import sys
import argparse

from flask import Flask, request

from texgen.generate import generate_batch, check_if_needs_regen
from texgen.data import (load_tokenizer,
                         encode_into_spacy,
                         get_context_for_regeneration,
                         get_src_gen_alignment_idxs,
                         get_gen_redundancy_rate,
                         get_gen_length_from_ws_split)
from texgen.construct import load_model

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


@app.route('/expand', methods=['POST'])
def get_expansions():
    model = app.config['model']
    tokenizer = app.config['tokenizer']

    input_text = request.json['input'].strip().lower()
    input_tokens = [token.text for token in encode_into_spacy(input_text)]
    print("input tokens:", input_tokens)

    gen_attempt = 1
    max_gen_attempts = 5
    gen_output = []
    gen_tokens_set = set()
    min_gen_length = 7
    max_gen_length = 75
    max_returned_texts = 5
    batch_size = 20
    sample_p = 0.7
    max_redund_rate = 0.9

    print("Using sample decoding with p={}, min length={}, max_length={}".format(
        sample_p, min_gen_length, max_gen_length))

    while len(gen_output) < max_returned_texts and gen_attempt <= max_gen_attempts:

        print("attempt {}: generating...".format(gen_attempt))
        attempted_gen_texts = generate_batch(batch_src_texts=[input_text] * batch_size,
                                             tokenizer=tokenizer,
                                             model=model,
                                             max_decoding_length=75,
                                             batch_ctx_texts=None,
                                             infer_method='sample',
                                             sample_top_k=0,
                                             sample_p=sample_p,
                                             sample_temperature=1.0)

        for gen_text in attempted_gen_texts:

            spacy_gen_text = encode_into_spacy(gen_text)

            needs_regen = check_if_needs_regen(
                spacy_gen_text,
                src_tokens=input_tokens,
                min_postproc_length=min_gen_length,
                max_postproc_length=max_gen_length,
                require_src_in_gen=True,
                block_repeat=True,
                block_quotes=False,
                require_eos_punct=True,
                require_paired_punct=True,
                max_redundancy_rate=max_redund_rate,
                n_gen_per_src=max_returned_texts,
                prev_gen_tokens=gen_tokens_set,
                verbose=True
            )

            if not needs_regen:
                gen_tokens = [token.text.lower() for token in spacy_gen_text]
                input_token_idxs = get_src_gen_alignment_idxs(spacy_gen_text,
                                                              input_tokens)
                print("Added sentence:", gen_text)
                gen_tokens_set.update(set(gen_tokens) - set(input_tokens))
                gen_output.append({'text': gen_text,
                                   'input_token_idxs': input_token_idxs})

                if len(gen_output) == max_returned_texts:
                    print("Finished {} texts".format(max_returned_texts))
                    break

        gen_attempt += 1

    logger.info("Returning {} sentences".format(len(gen_output)))
    return {'output': gen_output}


def init_app(model_path):

    model, model_hparams = load_model(load_dir=model_path)
    model.eval()
    tokenizer = load_tokenizer(model_hparams['tokenizer'])
    print("Loaded model")

    app.config['tokenizer'] = tokenizer
    app.config['model'] = model


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", "-model_path", help="Specify directory path for infilling model",
                        type=str, required=True)
    parser.add_argument("--port", "-port", help="Specify port number for this server",
                        type=int, required=False, default=5000)

    args = parser.parse_args()
    init_app(args.model_path)
    app.run(host='0.0.0.0', port=args.port)

import os
import math
import random
import time
import uuid
import spacy
from nltk.tokenize import word_tokenize, sent_tokenize
from flask import Flask, request, session

spacy_model = spacy.load('en')

eval_input_items_dir = "../input_data/prompts/"
input_items_filenames = {'easy': os.path.join(eval_input_items_dir, "easy.txt"),
                         "hard": os.path.join(eval_input_items_dir, "hard.txt")}

eval_gen_sents_dir = "../input_data/gen_examples"
gen_sents_filenames = {"easy": os.path.join(eval_gen_sents_dir, "easy.txt"),
                       "hard": os.path.join(eval_gen_sents_dir, "hard.txt")}

user_output_dir = "../user_output"


def validate_outputs(output_texts, input_tokens, example_output_texts=None,
                     min_output_length=None, max_output_length=None):

    validation_statuses = []
    all_input_token_char_idxs = []

    for idx, output_text in enumerate(output_texts):
        output_ws_tokens = output_text.lower().split(" ")
        output_length = len(output_ws_tokens)
        spacy_output_text = spacy_model(output_text)
        # Ensure all input words are in the sentence
        input_token_char_idxs = get_input_output_alignment_idxs(spacy_output_text, input_tokens)
        all_input_token_char_idxs.append(input_token_char_idxs)

        if len(input_token_char_idxs) < len(input_tokens):
            output_token_set = set([token.text.lower() for token in spacy_output_text])
            if all([input_token.lower() in output_token_set for input_token in input_tokens]):
                validation_statuses.append({'is_valid': False,
                                            'error_msg': "Input words must appear in same order as shown in prompt"
                                            })
            else:
                validation_statuses.append({'is_valid': False,
                                            'error_msg': "Sentence must contain all words from prompt"
                                            })

        elif ((min_output_length and output_length < min_output_length)
                or (max_output_length and output_length > max_output_length)):
            validation_statuses.append({'is_valid': False,
                                        'error_msg': "Sentence must contain between {} and {} words".format(
                                            min_output_length,
                                            max_output_length)
                                        })

        elif idx > 0 and output_text in set(output_texts[:idx]):
            validation_statuses.append({'is_valid': False,
                                        'error_msg': "Sentence must be different from previous sentences"
                                        })

        elif example_output_texts and output_text in set(example_output_texts):
            validation_statuses.append({'is_valid': False,
                                        'error_msg': "Sentence must be different from example sentences"
                                        })
        else:
            validation_statuses.append({'is_valid': True, 'error_msg': "\u2713"})

    return validation_statuses, all_input_token_char_idxs


def get_input_output_alignment_idxs(spacy_output_text, input_tokens):

    input_token_start_char_idxs = []
    input_token_end_char_idxs = []
    next_token_idx = 0
    if spacy_output_text.text.strip():
        output_tokens = [token.text.lower() for token in spacy_output_text]
        for input_token in input_tokens:
            input_token_found = False
            for output_token_idx, output_token in enumerate(spacy_output_text[next_token_idx:],
                                                            start=next_token_idx):
                if output_token.text.lower() == input_token.lower():
                    start_char_idx = output_token.idx
                    end_char_idx = start_char_idx + len(input_token)
                    input_token_start_char_idxs.append(start_char_idx)
                    input_token_end_char_idxs.append(end_char_idx)
                    input_token_found = True
                    break
            next_token_idx = output_token_idx + 1
            if input_token_found == False:
                break

    return list(zip(input_token_start_char_idxs,
                    input_token_end_char_idxs))


def load_eval_data():
    all_input_items = []
    for level in input_items_filenames:
        input_items_filename = input_items_filenames[level]
        gen_sents_filename = gen_sents_filenames[level]
        with open(input_items_filename) as input_f, open(gen_sents_filename) as gen_f:
            for input_tokens, gen_sents in zip(input_f, gen_f):
                input_item = {}
                input_item['input_tokens'] = tuple(input_tokens.strip().split(" "))
                input_item['level'] = level
                input_item['gen_sents'] = gen_sents.strip().split("\t")
                input_item['input_token_char_idxs'] = [get_input_output_alignment_idxs(
                    spacy_output_text=spacy_model(gen_sent),
                    input_tokens=input_item['input_tokens'])
                    for gen_sent in input_item['gen_sents']]
                if len(input_item['input_token_char_idxs']) != len(input_item['gen_sents']):
                    print("error finding all input tokens for item with input_tokens = {} \
                          and gen_sents = {}".format(input_item['input_tokens'],
                                                     input_item['gen_sents']))
                    continue
                all_input_items.append(input_item)
    print("Loaded all eval data")
    return all_input_items

print("Loading eval items...")
all_input_items = load_eval_data()
unique_items_per_sess = 2
do_two_round_experiment = True
show_example_gen_sents = True  # Only applicable if do_two_round_experiment == False

min_user_sent_length = 7
max_user_sent_length = 50

show_gen_stories = True
use_profanity_filter = False
gen_pipeline = None

if show_gen_stories:
    from transformers import pipeline
    gen_pipeline = pipeline(task='text-generation', model='gpt2', tokenizer='gpt2')
    print("Loaded story generation model")

min_story_length = 75
max_story_length = 75

# if use_profanity_filter:
#     with open("profanity_list.txt") as f:
#         profane_wordset = set([word.strip() for word in f])
#     print("Loaded profanity filter")

app = Flask(__name__)
app.secret_key = 'supersecret'
print("App ready!")


@app.route('/index', methods=['GET'])
def index():
    session['session_id'] = uuid.uuid4()
    sampled_item_ids = random.sample(range(len(all_input_items)),
                                     unique_items_per_sess)

    if do_two_round_experiment:
        session['show_gen_sents'] = ([False] * unique_items_per_sess +
                                     [True] * unique_items_per_sess)
        sampled_item_ids = sampled_item_ids * 2
    else:  # if not experimental task, always show example generated sentences
        session['show_gen_sents'] = [show_example_gen_sents] * unique_items_per_sess

    session['item_ids'] = sampled_item_ids

    session['cur_item_idx'] = -1
    print("Initialized session with ID {}, {} input items".format(
        session['session_id'],
        len(session['item_ids']))
    )
    return {'session_id': str(session['session_id'])[:5],
            'n_input_items': len(session['item_ids'])}


@app.route('/retrieve_item', methods=['GET'])
def get_input_item():
    session['cur_item_idx'] += 1
    if session['cur_item_idx'] == len(session['item_ids']):
        print("All items in session completed!")
        return {}
    item_id = session['item_ids'][session['cur_item_idx']]
    item_level = all_input_items[item_id]['level']
    item_input_tokens = all_input_items[item_id]['input_tokens']
    gen_sents = all_input_items[item_id]['gen_sents']
    input_token_char_idxs = all_input_items[item_id]['input_token_char_idxs']
    show_gen_sents = session['show_gen_sents'][session['cur_item_idx']]
    print(("Retrieved input item {} of {} in session: item id = {}, level = {}, " +
           "inputs = {}, show gen = {}, gen sents = {}").format(
        session['cur_item_idx'] + 1,
        len(session['item_ids']),
        item_id,
        item_level, item_input_tokens, show_gen_sents, gen_sents))
    response = {'item_num': session['cur_item_idx'] + 1,
                'input_tokens': item_input_tokens,
                'gen_sents': gen_sents,
                'input_token_char_idxs': input_token_char_idxs,
                'show_gen_sents': show_gen_sents}
    session['start_time'] = time.time()
    return response


@app.route('/submit_item', methods=['POST'])
def try_submit_item():
    # First ensure user data is valid
    user_sents = request.json['userSentences']

    item_id = session['item_ids'][session['cur_item_idx']]
    item_level = all_input_items[item_id]['level']
    input_tokens = all_input_items[item_id]['input_tokens']
    gen_sents = all_input_items[item_id]['gen_sents']
    show_gen_sents = session['show_gen_sents'][session['cur_item_idx']]

    (validation_statuses,
     input_token_char_idxs) = validate_outputs(output_texts=user_sents,
                                               input_tokens=input_tokens,
                                               example_output_texts=gen_sents if show_gen_sents else None,
                                               min_output_length=min_user_sent_length,
                                               max_output_length=max_user_sent_length)

    if all(status['is_valid'] for status in validation_statuses):
        # Data is valid, save to file
        session['end_time'] = time.time()
        session['time_elapsed'] = session['end_time'] - session['start_time']
        # Ensure no tabs or line breaks in user sentences
        user_sents = [sent.replace("\n", " ").replace("\t", " ")
                      for sent in user_sents]
        filename = os.path.join(user_output_dir, str(session['session_id']) + '.txt')
        with open(filename, 'a+') as f:
            if session['cur_item_idx'] == 0:
                f.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                    'Session_Item_Index',
                    'Item_ID',
                    'Difficulty_Level',
                    'Generated_Examples_Shown',
                    'Time_Elapsed',
                    'Input_Words',
                    'User_Sentences'
                ))
            f.write("{}\t{}\t{}\t{}\t{:3f}\t{}\t{}\n".format(
                session['cur_item_idx'],
                item_id,
                item_level,
                show_gen_sents,
                session['time_elapsed'],
                " ".join(input_tokens),
                "\t".join(user_sents)
            ))
        print("Wrote user output for item id {} with words = {} to {}".format(item_id, input_tokens, filename))

    return {'statuses': validation_statuses,
            'input_token_char_idxs': input_token_char_idxs}


@app.route('/generate_stories', methods=['POST'])
def generate_stories():
    sents = request.json['userSentences']

    # To ensure text is not cut off mid-sentence, truncate story to include all but final sentence
    # Returned story will contain only text after initial sentence
    item_id = session['item_ids'][session['cur_item_idx']]
    input_tokens = all_input_items[item_id]['input_tokens']

    stories = []
    for sent in sents:
        acceptable = False
        max_attempts = 3
        attempt_num = 1
        while not acceptable and attempt_num <= max_attempts:
            story = gen_pipeline(text_inputs=sent,
                                 min_length=min_story_length,
                                 max_length=max_story_length,
                                 do_sample=True,
                                 top_p=0.7,
                                 top_k=0)[0]['generated_text'][len(sent):]
            if use_profanity_filter:
                if len(set(word_tokenize(story)).intersection(profane_wordset)) == 0:
                    acceptable = True
                else:
                    print("detected profane on attempt {}: {}".format(attempt_num, story))
            attempt_num += 1

        if not acceptable:
            story = ""
        # Add up to two sentences to story
        else:
            story_sents = sent_tokenize(story)
            if len(story_sents[:-1]) >= 3:  # First three story sentences after given user sentence
                story = " ".join(story_sents[:3])
            elif len(story_sents[:-1]) >= 1:  # Less than three additional sentences, select all up to last
                story = " ".join(story_sents[:-1])
            else:
                story = " ".join(story_sents)  # Not enough sentences, just return all
        stories.append(story)

    print("generated stories: {}".format([sent + story for sent, story in zip(sents, stories)]))

    return {'generated_stories': stories}

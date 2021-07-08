# InSentive

This repo contains code associated with the paper "Inspiration through Observation: Demonstrating the Influence of Automatically Generated Text on Creative Writing", published at the 2021 International Conference on Computational Creativity (ICCC 2021).

This paper examines a particular creative writing task, sentence infilling, where the objective is to "expand" a list of words into a complete sentence. We developed a model that automatically generates infilled sentences (called "InSentive": *In*filling for *Sent*ences in the Narra*tive* Domain). We then had both this automated model and human writers produce infilled sentences for the same lists of words. In one condition, the human authors observed automatically generated sentences while authoring their own sentences. We found evidence that these automated examples helped people write more appealing sentences. See the paper for much more detail.

This repo contains three main components related to these experiments.

1. The code for the InSentive model, including the process for creating a dataset to train this model. We also provide a link to download our trained model itself.
2. The code for a web demo that showcases the automated model. You can also view this demo online at the link given below.
3. The code for the human authoring task. This includes the web application used to conduct the human authoring task, as well as scripts our experiments used to analyze the resulting data. The data we collected, which contains human-authored sentences aligned with generated sentences, is available by request if you email me at mroemmele@sdl.com.

Install the dependencies in requirements.txt to run any of this code: "pip install -r requirements.txt"

## 1. InSentive Model

The task of sentence infilling (also called expansion or elaboration) takes a text as input and expands the text to include new tokens in addition to the input tokens. These new tokens can be inserted ("infilled") anywhere among the input tokens.

The models I've developed for infilling make use of [texgen library](https://github.com/roemmele/texgen). You will need to install this library in order to run any code in this (insentivize) repo ("pip install git+https://github.com/roemmele/texgen.git"; also defined in requirements.txt). See the documentation in the texgen repo for details about the model code itself. This README goes through the steps I used to automatically create a dataset for infilling, train a model on this dataset, and apply the trained model to generate infilled texts.

### Data

#### Automated Data Creation

My experiments involved artifically generating expansion datasets by automatically removing tokens from sentences in existing text datasets, which results in aligned pairs of token lists and corresponding infilled texts that contain those tokens. The script here for performing this process is make_dataset.py. This script takes a set of texts as input, segments them into sentences (if not already segmented), and then drops tokens in the sentences via random sampling. The result is a new dataset of source-target pairs where the source sentences are the one with the removed tokens and the target sentences are the original sentences. There are two methods for performing token dropping: the baseline I simply call "random", and then there is also a "syntax" method. The first method simply randomly drops tokens from sentences without regard to syntax. The second method is a syntax-aware method that prunes tokens from a tree such that when a token is dropped (tokens are also selected here by random sampling), all of its dependent tokens in its dependency parse are also dropped. Both these methods have parameters that I set according to informal qualitative evaluation, such as how aggressively to perform dropping, and adding constraints like requiring a certain proportion of semantic content words to grammatical function words in the output sentences. Take a look at the syntax_drop_spacy_sentence() and random_drop_spacy_sentence() to see how these parameters are applied. When running make_dataset.py you can specify applying only one drop method, or indicate both drop methods should be applied, which will randomly alternate between the two while iterating through sentences. See `python make_dataset.py -h` for a description of all arguments that can be specified when running this script.

##### Example

To generate infilling source-target pairs for the sentences in toy_data/raw_data.txt:

```
python make_dataset.py -data_file ../toy_data/raw_data.txt -output_data_dir ../toy_data/elab_pairs -drop_methods random syntax -n_src_per_tgt 1 -lowercase_src
```

This will produce the files sents.src and sents.tgt in the -output_data_dir directory. This script does not partition the data into train/valid/test sets, so this will need to be done as a separate step.

##### BookCorpus Infilling Dataset

My experiments with sentence infilling made use of the BookCorpus dataset, which consists mostly of fiction books. I obtained this data through the [https://github.com/soskek/bookcorpus](Homemade BookCorpus repo), and selected a subset of 10,000 files (books). I ran the data_creation/make_dataset.py script on these files to generate infilling pairs. I used only the "random" method described above for deriving source texts. I also filtered pairs where the original target sentence was shorter than 10 tokens, and I converted all tokens in the source (but not the target) to lowercase. Below is the command that replicates this (cd to data_creation/). This dataset was used to train the model running in the demo described below.

```
python make_dataset.py -data_dir [PATH/TO/INPUT/FILES/DIRECTORY] -output_data_dir [PATH/TO/OUTPUT/PAIRS/DIRECTORY] -drop_method random -min_tgt_length 10 -min_drop_rate 0.6 -min_open_class_prop 0.5 -lowercase_src -batch_size 1000
```

### Training

You can use train_script.py in the texgen repo to train an infilling model (run `python texgen/train.py -h` to see a description of all command-line arguments defined by texgen). Here's a minimal command for training a model on the data in toy_data/elab_pairs (note the training and validation data files are the same here just for simplicity - they should obviously be different files for a real experiment):

```
python train_script.py -train_src_file toy_data/elab_pairs/sents.src -train_tgt_file toy_data/elab_pairs/sents.tgt -eval_src_file toy_data/elab_pairs/sents.src -eval_tgt_file toy_data/elab_pairs/sents.tgt -config_file test/test_configs/gpt2_lm_config.json -save_dir test_model -valid_epoch_end
```

Here are the specific arguments I used to train a model on the BookCorpus infilling pairs dataset (described above). The architecture/hyperparameters for this model are the same ones defined in test/test_configs/gpt2_lm_config.json.

```
python train_script.py -train_src_file [PATH/TO/TRAIN/SOURCE/TEXTS] -train_tgt_file [PATH/TO/TRAIN/TARGET/TEXTS] -eval_src_file [PATH/TO/VALIDATION/SOURCE/TEXTS] -eval_tgt_file [PATH/TO/VALIDATION/TARGET/TEXTS] -save_dir [PATH/TO/MODEL/DIRECTORY] -patience 25 -max_epochs 100 -config_file test/test_configs/gpt2_lm_config.json -max_grad_norm 1.0 -batch_size 32  -accum_steps 8 -valid_iterations 25000
```

### Generation

You can use generation_script.py in the texgen repo to generate infilled sentences from a trained model. Run `python texgen/generate.py -h` to see a description of all command-line arguments. Here is an example command for applying a trained model to generate infilled texts for the token sequences in toy_data/elab_pairs/sents.src. Note that the -require_src_in_gen argument is particularly important to ensure that the output sentences contain all tokens from the source inputs.

```
python generation_script.py -src_texts_file toy_data/elab_pairs/sents.src -model_dir [PATH/TO/MODEL/DIRECTORY] -gen_texts_file toy_data/elab_output.txt -infer_method sample -sample_p 0.7 -max_gen_attempts 10 -require_src_in_gen -verbose
```

### Trained BookCorpus Infilling Model

The model trained on infilled sentences from 10,000 fiction books can be downloaded here: X. Supply this directory as the -model_dir argument in the command above and you can produce infilled sentences for any token sequences.

## 2. InSentive Web Demo

The above trained model is running in a web demo app that produces infilled sentences for any user-provided text. The code for this app (React front-end, Flask back-end) is here in the demo-app directory. You can try out the demo for yourself here at X, or run it locally on your own machine.

## 3. InSentive Human Authoring Experiment

Description coming soon.

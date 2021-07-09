# Data

This contains the human authoring data associated with sentence infilling task described in the paper "Inspiration through Observation: Demonstrating the Influence of Automatically Generated Text on Creative Writing". In line with the descriptions given in the paper, this data includes the result of the authoring task (authoring blocks) and the result of the rater evaluation of the authored items (judgment groups).

**authoring_blocks.json**: Each data point here is an authoring block associated with a single prompt categorized by difficulty level (easy or hard). A point consists of the two sentences participants authored before observing the generated examples (Pre_User_Sentences), the two sentences they authored after observation (Post_User_Sentences), and the observed generated examples themselves (Generated_Sentences). Each data point is indexed by a unique ID (Block_ID).

**judgment_group_responses.json**: Each data point here is one rater response for a single judgment group in the evaluation task. A judgment group consists of a Pre sentence, Post sentence, and Gen sentence that come from the same authoring block. The Block_ID column identifies the authoring block and corresponds to the same column in authoring_blocks.json. The Group_ID column is a unique ID for each judgment group. Since two raters responded to each group, there are two rows per each Group_ID. Each response is defined by which sentence the rater preferred as the most storiable within that group. This is indicated by the "Prefers_Pre_Sentence", "Prefers_Post_Sentence", and "Prefers_Generated_Sentence" columns, where the rater-selected sentence has a value of 1 and the other sentences in the group have a value of 0. Additionally, the full list of observed generated sentences for the authoring block associated with the group is also included (even though this data is also given in authoring_blocks.json).

See the notebook analysis.ipynb for code that loads this data and performs the analyses reported in the paper.

If you use this data in your own research, please cite the paper:

```
@inproceedings{roemmele2021,
  title={Inspiration through Observation: Demonstrating the Influence of Automatically Generated Text on Creative Writing},
  author={Roemmele, Melissa},
  booktitle={12th International Conference on Computational Creativity},
  year={2021},
}
```

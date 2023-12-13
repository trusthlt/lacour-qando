# LaCour! Questions and Opinions
Companion dataset and experiments to the [arXiv preprint](http://arxiv.org/abs/2312.05061) presenting the ``LaCour!`` subset ``Questions and Opinions``.

## Dataset

### Loading the dataset
To use the dataset, all you need is [dataset_questions_opinions.json](dataset_questions_opinions.json).

You can load the dataset e.g. with pandas:

```python
import pandas as pd
df = pd.read_json('dataset_questions_opinions.json')
```

The dataset contains the following fields:
* webcast_id: the identifier for the associated hearing webcast, can be linked to the rest of the LaCour! corpus
* name: the name of the judge (only used to link question and opinion)
* has_question: the boolean value whether the judge had a question during the hearing
* has_opinion: the boolean value whether the judge had an opinion in the consequent judgment
* language: the language of the question
* question: the question asked by the judge
* case_id: the identifier for the relevant judgment document
* opinion: the tuple containing both the opinion title and the entire opinion by the judge
* opinion_type: the inferred type of the opinion (label), categorized into ``PARTLY``, ``DISSENTING``, ``CONCURRING``, ``OPINION`` or ``UNKOWN`` if the type cannot be categorized

### Creating the dataset
[To be updated]
To create the dataset yourself, all relevant information has to be extracted first. For this please refer to the creation scripts in [lacour-generation](https://github.com/trusthlt/lacour-generation).

```
conda create -n lacour-qando python=3.9
conda activate lacour-qando
git clone https://github.com/trusthlt/lacour-qando.git
cd lacour-qando
pip install -r requirements.txt
```

## Experiments

[tbd]

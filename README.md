# prac_dsfinal


Analyzing relationships between bird calls and environmental data.

**Relevant Links**

* [Kaggle Dataset: Bird songs](https://www.kaggle.com/c/birdclef-2021)
* [Collaborative Notebooks: Deepnote](https://www.deepnote.com)
* [Repo template based on Cookie Cutter Data](https://github.com/drivendata/cookiecutter-data-science)
* [Data versioning: DVC](https://dvc.org/doc/start/data-and-model-versioning)
* [Linting manager: pre-commit](https://pre-commit.com/)
  * [Notebook Linting](https://github.com/nbQA-dev/nbQA)
  * [flake8](https://github.com/PyCQA/flake8)
  * [black](https://github.com/psf/black)
  * [isort](https://github.com/pycqa/isort)
  * [flake8-bugbear](https://github.com/PyCQA/flake8-bugbear)
* [Custom CLI Tools: click](https://github.com/pallets/click)

## Installation

```shell
$ python -m venv venv
$ source ./venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ brew install pre-commit dvc
(venv) $ pre-commit install
```

If you want to skip the pre-commit checks, you need to pass the
`--no-verify` flag.

Now you'll want to [setup your kaggle keys](https://github.com/Kaggle/kaggle-api#api-credentials)

```shell
(venv) $ cp env.sample .env  # Now replace the keys with your keys
```

## DVC

To pull the latest data from DVC

```shell
(venv) $ dvc pull
```

This should pull data from Google Drive into the `data/` folder.

## Project Organization

```
├── LICENSE
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.py           <- makes project pip installable (pip install -e .) so prac_dsfinal can be imported
└── prac_dsfinal                <- Source code for use in this project.
    ├── __init__.py    <- Makes prac_dsfinal a Python module
    │
    ├── data           <- Scripts to download or generate data
    │   └── make_dataset.py
    │
    ├── features       <- Scripts to turn raw data into features for modeling
    │   └── build_features.py
    │
    └── models         <- Scripts to train models and then use trained models to make
        │                 predictions
        ├── predict_model.py
        └── train_model.py

```

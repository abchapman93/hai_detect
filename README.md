# hai_detect

hai_detect is an implementation of pyConText. The purpose of this implementation is to identify mentions of and classify reports for three types of Healthcare-Associated Infections (HAIs):
* Surgical Site Infections (Superfical, Deep Incisional, and Organ/Space)
* Urinary Tract Infections
* Pneumonia

This project is an extension of fcFinder, which focused only on Organ/Space SSIs.
This package will be developed and maintained by:
* Alec Chapman
* Jacob Wan
* Brian Bucher, MD (senior author)

## Introduction
hai_detect is a specific implementation of pyConText, a Python implementation of the ConText algorithm. [The GitHub repo for pyConText](https://github.com/chapmanbe/pyConTextNLP) includes useful information and tutorials.

The first step of this project, fcFinder, was implemented to identify evidence of Organ/Space SSIs in radiology reports. This was published and presented at the 2017 Annual AMIA Proceedings 'Detecting Evidence of Intra-abdominal Surgical Site Infections from Radiology Reports Using Natural Language Processing, Chapman et al.' [AMIA 2017 Proceedings](https://amia2017.zerista.com/event/member/389135). The manuscript for this paper and publications utilizing pyContext/ConText will be contained in the directory **Publications**.

## Installation
Download hai_detect from GitHub at https://github.com/abchapman93/hai_detect . We will later set up installation using pypi.

## Code Structure
*Note:* This is in development and may change.

### root
In addition to *__init__.py* and *README.md*, the root directory will contain the following files:
* *main.py* This is a script that will accept the directory containing data as an argument and run the hai_detect algorithm on the data found in the directory.
* *AggregateModel.py* This module defines a class that aggregates the three models found in *Models* and finds all mentions of HAIs in a report.

### utils
This directory will contain scripts that will read offer utilities for data wrangling/exploration, such as identifying number of patients with HAIs, average number of notes per patient, etc.


### models
This directory will contain two modules that define the classes for classifying text. *MentionLevelModels.py* contains the class `MentionLevelModel`, which takes implements the pyConText algorithm using targets and modifiers.

The second module will define a classes for report-level classification.
* *mention_level_models.py*
* *document_level_models.py*

### annotations
This directory contains the classes that process text documents and annotations. It contains two modules, `Annotation.py`, which defines the classes that hold the NLP findings, and `ClinicalTextDocument`, which takes a text report, links to annotations, and compares the annotations.

### lexicon
This directory will contain the *.tsv.* files that pyConText uses to instantiate targets and modifiers. There will be on generic file for modifiers and one for targets.
* *targets.tsv*
* *modifiers.tsv*

"""
Classes defined for extracting and classifying mention-level annotations of HAIs.
"""
import os
import pyConTextNLP.pyConTextGraph as pyConText
import pyConTextNLP.itemData as itemData

from nltk import word_tokenize

from utils import helpers


class MentionLevelModel(object):
    """
    # TODO: Should we just use this as one model?
    This class will be used as an abstract model
    from which other models will inherit.
    """

    def __init__(self, targets_file, modifiers_file):
        """Instantiate targets and modifiers"""
        self.targets_file = targets_file
        self.modifiers_file = modifiers_file
        self.targets = self.instantiate_targets()
        self.modifiers = self.instantiate_modifiers()


    def instantiate_targets(self):
        targets = itemData.instantiateFromCSVtoitemData(self.targets_file)
        return targets


    def instantiate_modifiers(self):
        modifiers = itemData.instantiateFromCSVtoitemData(self.modifiers_file)
        return modifiers


    def _preprocess_text(self, text):
        """
        Takes a report as a string and preprocesses it
        """
        #TODO: Decide how to represent text after preprocessing/classification
        #text = helpers.preprocess(text)
        text = text.lower()
        text = text.split() # Remove excess whitespaces
        text = ' '.join(text)

        return text



    def markup_sentence(self, sentence, prune_inactive=True):
        """
        Identifies all markups in a sentence
        """
        markup = pyConText.ConTextMarkup()
        markup.setRawText(sentence)
        #markup.cleanText()
        markup.markItems(self.modifiers, mode="modifier")
        markup.markItems(self.targets, mode="target")
        try:
            markup.pruneMarks()
        except TypeError as e:
            print("Error in pruneMarks")
            print(markup)
            print(e)
        markup.dropMarks('Exclusion')
        # apply modifiers to any targets within the modifiers scope
        markup.applyModifiers()
        markup.pruneSelfModifyingRelationships()
        if prune_inactive:
            markup.dropInactiveModifiers()
        return markup


if __name__ == '__main__':
    targets = os.path.abspath('../lexicon/targets.tsv')
    modifiers = os.path.abspath('../lexicon/modifiers.tsv')
    model = MentionLevelModel(targets, modifiers)
    print(model.targets)
    string = "The patient shows symptoms of pneumonia.".lower()
    print(model.markup_sentence(string))

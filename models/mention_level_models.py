"""
Classes defined for extracting and classifying mention-level annotations of HAIs.
"""
import os
import pyConTextNLP.pyConTextGraph as pyConText
import pyConTextNLP.itemData as itemData

from nltk import word_tokenize


class MentionLevelModel(object):
    """
    This class will be used as an abstract model
    from which other models will inherit.
    """

    def __init__(self, targets_file, modifiers_file):
        """Instantiate targets and modifiers"""
        self.targets_file = 'file://'+targets_file
        self.modifiers_file = 'file://'+modifiers_file
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

        text = text.lower()
        text = ' '.join(word_tokenize(text))

        return text


    def extract_markups(self, text):
        """
        Extracts pyConText markups from a string.
        First preprocesses the string.
        Returns a list of markups
        """
        text = self.preprocess_text(text)
        pass


class SSIModel(MentionLevelModel):
    """
    This class that will be used to classify UTIs
    """

    # class attribute to define acceptable mention types
    __mention_types = ['SUPERFICIAL SSI', 'DEEP INCISIONAL SSI', 'ORGAN/SPACE SSI']

    def __init__(self, targets_file, modifiers_file):
        super().__init__(targets_file, modifiers_file)


    def preprocess_text(self, text):
        """
        Additional preprocessing sepcific to this class
        after general preprocessing is completed by
        `self._preprocess_string`
        """
        text = self._preprocess_text(text)
        return text


class UTIModel(MentionLevelModel):
    """
    This class that will be used to classify UTIs
    """
    # class attribute to define acceptable mention types
    __mention_types = ['UTI']

    def __init__(self, targets_file, modifiers_file):
        super().__init__(targets_file, modifiers_file)


    def preprocess_text(self, text):
        """
        Additional preprocessing sepcific to this class
        after general preprocessing is completed by
        `self._preprocess_string`
        """
        text = self._preprocess_text(text)
        return text


class PneumoniaModel(MentionLevelModel):
    # class attribute to define acceptable mention types
    __mention_types = ['PNEUMONIA']

    def __init__(self, targets_file, modifiers_file):
        super().__init__(targets_file, modifiers_file)


    def preprocess_text(self, text):
        """
        Additional preprocessing sepcific to this class
        after general preprocessing is completed by
        `self._preprocess_string`
        """
        text = self._preprocess_text(text)
        return text


if __name__ == '__main__':
    targets = os.path.abspath('../lexicon/pneumonia.tsv')
    modifiers = os.path.abspath('../lexicon/modifiers.tsv')
    model = PneumoniaModel(targets, modifiers)
    print(model.targets)
    string = "The patient shows symptoms of pneumonia. Signed, Dr. Doctor, MD"
    print(model.preprocess_text(string))

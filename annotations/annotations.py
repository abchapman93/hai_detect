"""
This module defines classes that are used to represent texts and annotations.
"""
import os
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize import WhitespaceTokenizer

from pyConTextNLP import pyConTextGraph as pyConText
import pyConTextNLP.itemData as itemData


class ClinicalTextDocument(object):
    """
    This class is a representation of a single clinical documents.
    It is initialized with `text`, an unprocessed text document.
    In order to preserve the initial document spans,
    this is saved as an attribute `raw_text`.
    """

    def __init__(self, text):
        self.raw_text = text
        self.original_spans = self.get_text_spans(text)
        self.preprocessed_text = self.preprocess(text)
        self.split_text_and_spans = None

        # Split into sentences
        # While maintaining the original text spans
        sentences, word_spans, sentence_spans = self.split_sentences(self.preprocessed_text, self.original_spans)
        self.sentences = sentences
        self.word_spans = word_spans
        self.sentence_spans = sentence_spans


    def get_text_spans(self, text):
        """
        Returns a list of two-tuples consisitng of (`word`, (`start`, `end`))
        for each word in `text`.
        The tokens are tokenized only by whitespaces
        :param text: [str]
        :return: a list of two-tuples representing individual tokens and their spans
        """
        span_generator = WhitespaceTokenizer().span_tokenize(text)
        return list(span_generator)


    def preprocess(self, text):
        """
        Returns preprocessed text.
        Currently only lower-cased
        """
        # Split by white space
        text = text.lower()
        words = text.split()

        # Do preprocessing by removing replacing tokens with empty strings
        # or changing tokens.
        # The original spans will be maintained

        text = ' '.join(words)
        return text


    def split_sentences(self, text, spans):
        """
        Iterates through tokens in text.split().
        At each termination point, a new sentence is started
        unless that token is part of the exception words.
        :return:
            `sentences`: a list of lists of words split by whitespace
                - [['this', 'is', 'a', 'sentence'],
                  ['and', 'this', 'is', 'another.']]
            `word_spans`: a list lists of two-tuples representing word start and end points
                - [[(0, 4), (5, 7), (8, 9), (10, 19)],
                  [(20, 23), (24, 28), (29, 31), (32, 40)]]
            `sentence_spans`: a list of start and end point for sentences
                - [(0, 19), (20, 40)])
            list of sentences and spans
        """

        termination_points = '.!?'
        exception_words = ['dr.', 'm.d', 'mr.', 'ms.', 'mrs.', ]

        words = text.split()

        sentences = [] # List of list of words
        word_spans = [] # List of list of start, end points for words
        sentence_spans = [] # List of start, end points for sentences

        current_sentence = []
        current_spans = []
        for word, span in zip(words, spans):
            print(word, span)
            # Populate `current_sentence` with words
            # and `current_spans` with spans for each word
            current_sentence.append(word)
            current_spans.append(span)

            if word[-1] in termination_points and word not in exception_words:
                # Add `current_sentence` and `current_spans` to larger lists
                sentences.append(current_sentence)
                word_spans.append(current_spans)
                sentence_spans.append((current_spans[0][0], current_spans[-1][-1]))

                # Start a new sentence
                current_sentence = []
                current_spans = []

        # Take care of any words remaining
        if len(current_sentence):
            sentences.append(current_sentence)
            word_spans.append(current_spans)
            sentence_spans.append((current_spans[0][0], current_spans[-1][-1]))

        return sentences, word_spans, sentence_spans


class AnnotationDocument(object):
    """
    This class represents an entire document
    and annotations
    """

    def __init__(self):
        pass


class Annotation(object):
    """
    This class represents an annotation of a medical concept from text.
    It can be initialized either from an eHOST knowtator.xml annotation
    or from a pyConText markup.
    """

    def __init__(self):
        self.sentence = None
        self.text = None
        self.span_in_sentence = None
        self.span_in_document = None
        self.attributes = {
            'assertion': 'positive', # positive, probable, negated, indication
            'temporality': 'present', # current, historical, future/hypothetical
            'anatomy': [],
        }

        # 'definite negated existence', 'anatomy', ...
        self.modifier_categories = []
        # Will eventually be 'Positive Evidence of SSI', 'Negated Evidence of Pneumonia', ...
        self.classification = None
        self.annotator = None




    def from_ehost(self, xml_tag):
        pass

    def from_markup(self, markup, tag_object, sentence, sentence_span):
        """
        Takes a markup and a tag_object, a target node from that markup.
        Sentence is the raw text.
        Sentence_span is the span of the sentence in the document
        and is used to update the span for the markup, which is at a sentence level.
        Returns a single annotation object.

        The tag_object can be obtained by iterating through the list
        returned from`markup.getMarkedTargets()`
        """
        self.annotator = 'hai_detect'


        # Get the entire span in sentence.
        spans = []
        spans.extend(tag_object.getSpan()) # Span of the target term
        for modifier in markup.getModifiers(tag_object):
            spans.extend(modifier.getSpan()) # Spans for each modifier

        self.span_in_sentence = (min(spans), max(spans))

        # Get the span in the entire document.
        sentence_offset = sentence_span[0]
        self.span_in_document = (self.span_in_sentence[0] + sentence_offset, self.span_in_sentence[1] + sentence_offset)

        # Add the text for the whole sentence
        self.sentence = sentence
        # And for the annotation itself
        self.text = sentence[self.span_in_sentence[0]:self.span_in_sentence[1]]

        # Get categories of the modifiers
        self.modifier_categories.extend([mod.getCategory()[0] for mod in markup.getModifiers(tag_object)])

        # Update attributes
        # These will be used later to classify the annotation
        if 'definite existence' in self.modifier_categories:
            self.attributes['assertion'] = 'positive'
        if 'definite_negated_existence' in self.modifier_categories:
            self.attributes['assertion'] = 'negated'
        if 'indication' in self.modifier_categories:
            self.attributes['assertion'] = 'indication'
        if 'probable_existence' in self.modifier_categories:
            self.attributes['assertion'] = 'probable'
        print(self.modifier_categories)
        #for mod in markup.getModifiers():
            #print(mod.getCategory())

        if 'anatomy' in self.modifier_categories:
            self.attributes['anatomy'] = [mod.getLiteral() for mod in markup.getModifiers(tag_object)
                                          if 'anatomy' in mod.getCategory()]




        pass

    def classify_annotation(self):
        pass

    def compare(self, second_annotation):
        pass

    def __str__(self):
        string =  'Annotation by: {a}\nSentence: {s}\nText: {t}\nSpan: {sp}\n'.format(
             a=self.annotator, s=self.sentence, sp=self.span_in_document, t=self.text)
        string += 'Attributes:\n    Assertion: {assertion}\n    Temporality: {temporality}\n    Anatomical Sites: {anatomy}\n'.format(
            **self.attributes)
        string += 'Classification: {c}'.format(c=self.classification)

        return string


def markup_sentence(s, modifiers, targets, prune_inactive=True):
    """
    """
    markup = pyConText.ConTextMarkup()
    markup.setRawText(s)
    #markup.cleanText()
    markup.markItems(modifiers, mode="modifier")
    markup.markItems(targets, mode="target")
    markup.pruneMarks()
    markup.dropMarks('Exclusion')
    # apply modifiers to any targets within the modifiers scope
    markup.applyModifiers()
    markup.pruneSelfModifyingRelationships()
    if prune_inactive:
        markup.dropInactiveModifiers()
    return markup




if __name__ == '__main__':
    string = "The patient shows symptoms of pneumonia. The wound is CDI. \
    He has not developed an urinary tract infection.\n Signed, Dr. Doctor, MD"

    sentence = "There is no evidence of surgical site infection near the abdomen but there is a wound infection.".lower()
    #TODO: sentence span should come from a clinical text document and should reflect the original, uncleaned text
    sentence_span = (0, len(sentence))

    targets = os.path.abspath('../lexicon/ssi.tsv')
    modifiers = os.path.abspath('../lexicon/modifiers.tsv')

    targets = itemData.instantiateFromCSVtoitemData(targets)
    modifiers = itemData.instantiateFromCSVtoitemData(modifiers)

    m = markup_sentence(sentence, modifiers=modifiers, targets=targets)
    for target in m.getMarkedTargets():
        annotation = Annotation()
        annotation.from_markup(m, target, sentence, sentence_span)
        print(annotation)
    exit()
    target = m.getMarkedTargets()[0]

    print(annotation)
    exit()

    print(m.nodes(data=True));
    print(m.getMarkedTargets()); exit()

    document = ClinicalTextDocument(string)
    print(document.raw_text_spans)
    print(document.preprocessed_text)
    print(document.split_sentences(document.preprocessed_text, document.raw_text_spans))

    exit()




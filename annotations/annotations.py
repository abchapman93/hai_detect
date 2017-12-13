"""
This module defines classes that are used to represent texts and annotations.
"""
import os
import re
from datetime import datetime
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize import WhitespaceTokenizer

import xml.etree.ElementTree as ElementTree
from xml.etree.ElementTree import Element, SubElement
from xml.dom import minidom

from pyConTextNLP import pyConTextGraph as pyConText
import pyConTextNLP.itemData as itemData

from models.mention_level_models import MentionLevelModel


class ClinicalTextDocument(object):
    """
    This class is a representation of a single clinical documents.
    It is initialized either with `text`, an unprocessed text document
    and `rpt_id`, a unique identifier for the file (most often the filename),
    OR `filepath`, a filepath to a single report.
    In order to preserve the initial document spans,
    this is saved as an attribute `raw_text`.
    """

    def __init__(self, text=None, rpt_id='', filepath=None):
        if (not text) and filepath:
            text = self.from_filepath(filepath)
            rpt_id = os.path.splitext(os.path.basename(filepath))[0]

        self.raw_text = text
        self.rpt_id = rpt_id
        self.original_spans = self.get_text_spans(text)
        self.preprocessed_text = self.preprocess(text)
        self.split_text_and_spans = None
        self.sentences = [] # This will be a list of dictionairies
                            # where each dict contains {
                            # 'idx': int, 'text': sentence, 'word_spans': [(start, end), ...], 'span': (start, end)
                            # }
        self.annotations = []
        self.sentences_with_annotations = []
        self.element_tree = None

        # Split into sentences
        # While maintaining the original text spans
        self.sentences = self.split_sentences(self.preprocessed_text, self.original_spans)


    def from_filepath(self, filepath):
        with open(filepath) as f:
            text = f.read()
        return text


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
        #word_spans = [] # List of list of start, end points for words
        #sentence_spans = [] # List of start, end points for sentences

        idx = 0
        sentence_dict = {}
        current_sentence = []
        current_spans = []
        for word, span in zip(words, spans):
            # Populate `current_sentence` with words
            # and `current_spans` with spans for each word
            current_sentence.append(word)
            current_spans.append(span)

            if word[-1] in termination_points and word not in exception_words:
                # Add `current_sentence` and `current_spans` to larger lists
                sentence_dict['text'] = ' '.join(current_sentence)
                sentence_dict['words'] = current_sentence
                sentence_dict['idx'] = idx
                sentence_dict['span'] = (current_spans[0][0], current_spans[-1][-1])
                sentence_dict['word_spans'] = current_spans
                sentences.append(sentence_dict)

                # Start a new sentence
                idx += 1
                sentence_dict = {}
                current_sentence = []
                current_spans = []

        # Take care of any words remaining
        if len(current_sentence):
            sentence_dict['text'] = ' '.join(current_sentence)
            sentence_dict['words'] = current_sentence
            sentence_dict['idx'] = idx
            sentence_dict['span'] = (current_spans[0][0], current_spans[-1][-1])
            sentence_dict['word_spans'] = current_spans
            sentences.append(sentence_dict)

        return sentences

    def annotate(self, model):
        """
        This methods takes a MentionLevelModel that identifies targets and modifiers.
        For each sentence in self.sentences, the model identifies all findings using pyConText.
        These markups are then used to create Annotations and are added to `sentence['annotations']`
        """
        for sentence_num, sentence in enumerate(self.sentences):
            markup = model.markup_sentence(sentence['text'])
            targets = markup.getMarkedTargets()

            # Create annotations out of targets
            for target in targets:
                annotation = Annotation()
                annotation.from_markup(target, markup, sentence['text'], sentence['span'])
                annotation.sentence_num = sentence_num
                # TODO: decide whether to exclude annotations without anatomy
                self.sentences_with_annotations.append(sentence_num)
                self.annotations.append(annotation)


    def get_annotations(self):
        """
        Returns a list of annotations.
        """
        return this.annotations


    def to_etree(self):
        """
        Creates an eTree XML element
        """
        root = Element('annotations')
        root.set('textSource', self.rpt_id + '.txt')
        # TODO:
        for annotation in self.annotations:
            root.append(annotation.to_etree())
            #root.append(annotation.get_xml())
            #root.append(annotation.get_mention_xml())

        # xml for adjudication status
        adjudication_status = SubElement(root, 'eHOST_Adjudication_status')
        adjudication_status.set('version','1.0')
        selected_annotators = SubElement(adjudication_status,'Adjudication_Selected_Annotators')
        selected_annotators.set('version','1.0')
        selected_classes = SubElement(adjudication_status,'Adjudication_Selected_Classes')
        selected_classes.set('version','1.0')
        adjudication_others = SubElement(adjudication_status,'Adjudication_Others')

        check_spans = SubElement(adjudication_others,'CHECK_OVERLAPPED_SPANS')
        check_spans.text = 'false'
        check_attributes = SubElement(adjudication_others,'CHECK_ATTRIBUTES')
        check_attributes.text = 'false'
        check_relationship = SubElement(adjudication_others,'CHECK_RELATIONSHIP')
        check_relationship.text = 'false'
        check_class = SubElement(adjudication_others,'CHECK_CLASS')
        check_class.text = 'false'
        check_comment = SubElement(adjudication_others,'CHECK_COMMENT')
        check_comment.text = 'false'

        return ElementTree.ElementTree(root)


        #self.element_tree = ElementTree.ElementTree(root)



    def to_knowtator(self, outdir):
        """
        This method saves all annotations in an instance of ClinicalTextDocument to a .knowtator.xml file
        to be imported into eHOST.
        outdir is the directory to which the document will be saved.
        The outpath will be '/path/to/outdir/rpt_id.knowtator.xml'
        """
        if not os.path.isdir(outdir):
            raise FileNotFoundError("{} is not a directory".format(outdir))
        outpath = os.path.join(outdir, self.rpt_id + '.txt.knowtator.xml')
        element_tree = self.to_etree()
        f_out = open(outpath, 'w')
        element_tree.write(f_out, encoding='unicode')
        print("Saved at {}".format(outpath))
        f_out.close()




    def __str__(self):
        string = ''
        string += 'Report {0}\n'.format(self.rpt_id)
        for sentence_num, sentence in enumerate(self.sentences):
            string += '{text} '.format(**sentence)
            if sentence_num in self.sentences_with_annotations:
                for annotation in [a for a in self.annotations if a.sentence_num == sentence_num]:
                    string +=  annotation.get_short_string() + '\n'
        return string


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

    # Dictionary mapping pyConText target types to eHOST class names
    _annotation_types = {'organ/space surgical site infection': 'Evidence of SSI',
                         'deep surgical site infection': 'Evidence of SSI',
                         'superficial surgical site infection': 'Evidence of SSI',
                         'negated superficial surgical site infection': 'Evidence of SSI',
                           'urinary tract infection': 'Evidence of UTI',
                           'pneumonia': 'Evidence of Pneumonia'
    }

    # Classifications based on assertion
    # NOTE:
    # May change the value of 'probable' to 'Positive Evidence'
    _annotation_classifications = {'Evidence of SSI': {
                                        'positive': 'Positive Evidence of SSI',
                                        'negated': 'Negated Evidence of SSI',
                                        'probable': 'Probable Evidence of SSI',
                                        'indication': 'Indication of SSI'
                                    },
                                    'Evidence of UTI': {
                                        'positive': 'Positive Evidence of UTI',
                                        'negated': 'Negated Evidence of UTI',
                                        'probable': 'Probable Evidence of UTI',
                                        'indication': 'Indication of UTI',
                                    },
                                    'Evidence of Pneumonia': {
                                        'positive': 'Positive Evidence of Pneumonia',
                                        'negated': 'Negated Evidence of Pneumonia',
                                        'probable': 'Probable Evidence of Pneumonia',
                                        'indication': 'Indication of Pneumonia'
                                    }
    }

    def __init__(self):
        self.sentence = None
        self.datetime = datetime.now().strftime('%m%d%Y %H:%M:%S')
        self.id = ''  # TODO: Change this
        self.text = None
        self.sentence_num = None
        self.span_in_sentence = None
        self.span_in_document = None
        self.annotation_type = None # eHOST class names: 'Evidence of SSI', 'Evidence of Pneumonia', 'Evidence of UTI'
        self.attributes = {
            'assertion': 'positive', # positive, probable, negated, indication
            'temporality': 'current', # current, historical, future/hypothetical
            'anatomy': [],
        }

        # 'definite negated existence', 'anatomy', ...
        self.modifier_categories = []
        # Will eventually be 'Positive Evidence of SSI', 'Negated Evidence of Pneumonia', ...
        self.classification = None
        self.annotator = None




    def from_ehost(self, xml_tag):
        pass


    def from_markup(self, tag_object, markup, sentence, sentence_span):
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
        self.id = tag_object.getTagID()

        # Get category of target
        self.markup_category = tag_object.getCategory()[0]
        # Make sure this is an annotation class that we recognize
        if self.markup_category not in self._annotation_types:
            raise NotImplementedError("{} is not a valid annotation type, must be one of: {}".format(
                self.markup_category, set(self._annotation_types.values())
            ))

        self.annotation_type = self._annotation_types[self.markup_category]

        # If the target is a surgical site infection,
        # classify the type
        # ['organ/space', 'superficial', 'deep']
        if 'surgical site infection' in self.markup_category:
            self.attributes['infection_type'] = re.search('([a-z/]*) surgical site infection', self.markup_category).group(1)


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
        # This is the core logic for classifying markups
        # `assertion` default value is 'positive'
        if self.markup_category == 'negated superficial surgical site infection':
            self.attributes['assertion'] = 'negated'
        elif 'definite_existence' in self.modifier_categories:
            self.attributes['assertion'] = 'positive'
        elif 'definite_negated_existence' in self.modifier_categories:
            self.attributes['assertion'] = 'negated'
        elif 'indication' in self.modifier_categories:
            self.attributes['assertion'] = 'indication'
        elif 'probable_existence' in self.modifier_categories:
            self.attributes['assertion'] = 'probable'


        # TODO: Update temporality

        # Add anatomical sites to instances of surgical site infections
        if 'surgical site infection' in self.markup_category:
                self.attributes['anatomy'] = [mod.getLiteral() for mod in markup.getModifiers(tag_object)
                                          if 'anatomy' in mod.getCategory() or
                                          'surgical site' in mod.getCategory()]

        self.classify()


    def classify(self):
        """
        This method applies heuristics for classifying an annotation
        For example, an annotation that has `category` = `surgical site infection`,
        `assertion` = `negated` and `temporality` = `current` would be classified as
        'Negative Evidence of Surgical Site Infection'.

        Sets object's attribute `classification`.
        Returns classification.
        """

        classification = self._annotation_classifications[self.annotation_type][self.attributes['assertion']]
        if self.attributes['temporality'] != 'current':
            classification += ' - {}'.format(self.attributes['temporality'].title())

        # Exclude any annotations of a surgical site infection that doesn't have anatomy
        # TODO: Implement coreference resolution in `from_markup()`
        # TODO: Test whether we actually want to do this
        if classification == 'Positive Evidence of SSI' and self.attributes['anatomy'] == []:
            classification += ' - No Anatomy'

        self.classification = classification
        return classification



    def compare(self, second_annotation):
        pass


    def to_etree(self):
        """
        This method returns an eTree element that represents the annotation
        and can be appended to the rest of the document and saved as a knowtator xml file.
        """
        annotation_body = Element('annotation')

        mention_id = SubElement(annotation_body, 'mention')
        mention_id.set('id', str(self.id))

        annotator_id = SubElement(annotation_body, 'annotator')
        annotator_id.set('id', 'eHOST_2010')
        annotator_id.text = self.annotator

        span = SubElement(annotation_body, 'span', {'start': str(self.span_in_document[0]),
                                                    'end': str(self.span_in_document[1])})
        spanned_text = SubElement(annotation_body, 'spannedText')
        spanned_text.text = self.text
        creation_date = SubElement(annotation_body, 'creationDate')
        creation_date.text = self.datetime

        return annotation_body



    def get_short_string(self):
        """
        This returns a brief string representation of the annotation
        That can be used for printing ClinicalTextDocuments after annotation
        """
        string = '<annotation '
        string += 'annotator={} '.format(self.annotator)
        string += 'text="{}" '.format(self.text.upper())
        string += 'classification={}'.format(self.classification)
        string += '></annotation>'
        return string

    def __str__(self):
        string =  'Annotation by: {a}\nSentence: {s}\nText: {t}\nSpan: {sp}\n'.format(
             a=self.annotator, s=self.sentence, sp=self.span_in_document, t=self.text)
        string += 'Attributes:\n    Assertion: {assertion}\n    Temporality: {temporality}\n'.format(**self.attributes)
        if self.annotation_type == 'Evidence of SSI':
            string += '    Anatomical Sites: {anatomy}\n'.format(**self.attributes)
            string += '    Infection type: {i}\n'.format(i=self.attributes['infection_type'])
        string += 'Classification: {c}'.format(c=self.classification)

        return string


def main():
    """
    An example of processing one text document.
    """

    # Create a model with modifiers and targets
    targets = os.path.abspath('../lexicon/targets.tsv')
    modifiers = os.path.abspath('../lexicon/modifiers.tsv')
    model = MentionLevelModel(targets, modifiers)

    text = "We examined the patient yesterday. He shows signs of pneumonia.\
    The wound is CDI. He has not developed a urinary tract infection\
    However, there is a wound infection near the abdomen. There is no surgical site infection.\
    There is an abscess. Signed, Dr.Doctor MD."
    rpt_id = 'example_report'
    document = ClinicalTextDocument(text, rpt_id='example_report')
    document.annotate(model)
    print(document)

    outdir = 'tmp'
    document.to_knowtator(outdir)
    exit()

    for annotation in document.annotations:
        print(annotation)
        print(annotation.to_etree())
        print()


if __name__ == '__main__':
    main()
    exit()




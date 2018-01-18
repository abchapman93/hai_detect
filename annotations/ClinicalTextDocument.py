"""
This module defines classes that are used to represent texts and annotations.
"""
import os

from nltk.tokenize import WhitespaceTokenizer

#import xml.etree.ElementTree as ElementTree
#from xml.etree.ElementTree import Element, SubElement

from lxml import etree
from lxml.etree import Element, SubElement

from utils import helpers
from annotations.Annotation import Annotation
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

        self.split_text_and_spans = None
        self.sentences = [] # This will be a list of dictionairies
                         # where each dict contains {
                         # 'idx': int, 'text': sentence, 'word_spans': [(start, end), ...], 'span': (start, end)
                         # }
        self.annotations = []
        self.sentences_with_annotations = []
        self.element_tree = None
        self.filepath = filepath

        if (text or filepath or rpt_id != ''):
            processText(text, rpt_id, filepath)

    def processText(self, text=None, rpt_id='', filepath=None):
        if (not text) and filepath:
            text = self.from_filepath(filepath)
            rpt_id = os.path.splitext(os.path.basename(filepath))[0]

        self.raw_text = text
        self.rpt_id = rpt_id
        self.original_spans = self.get_text_spans(text)
        self.preprocessed_text = self.preprocess(text)

        # self.split_text_and_spans = None
        # self.sentences = [] # This will be a list of dictionairies
        #                     # where each dict contains {
        #                     # 'idx': int, 'text': sentence, 'word_spans': [(start, end), ...], 'span': (start, end)
        #                     # }
        # self.annotations = []
        # self.sentences_with_annotations = []
        # self.element_tree = None

        # Split into sentences
        # While maintaining the original text spans
        self.sentences = self.split_sentences(self.preprocessed_text, self.original_spans)

    def cal_diff_score(self, other):

        total_len = len(self.annotations) + len(other.annotations)

        match_len = 0
        score = 0

        for ann1 in self.annotations:
            for ann2 in other.annotations:
                if (ann1.isSimilar(ann2)):
                    match_len += 2 #both sides

        score = match_len / total_len

        return score
        pass


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
        #words = text.split()

        # Do preprocessing by removing replacing tokens with empty strings
        # or changing tokens.
        # The original spans will be maintained

        #text = ' '.join(words)
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

        termination_points = '.!?;'
        termination_words = ['a/p:'] # Words to terminate at that we didn't catch in preprocessing
        exception_words = ['dr.', 'm.d', 'mr.', 'ms.', 'mrs.', ]
        # Find header points before splitting the text
        #headers = helpers.find_headers(text)
        #header_points = [m.span()[0] for m in headers]

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

            # If you reach a termination point and it's not one of the above exception words,
            # append this sentence and start a new one
            if (word in termination_words) or (word[-1] in termination_points and word not in exception_words):
                    #span[1] in header_points:  # Took this out, instead added a period in preprocessing
                # Add `current_sentence` and `current_spans` to larger lists
                sentence_dict['text'] = ' '.join(current_sentence)
                sentence_dict['words'] = current_sentence
                sentence_dict['idx'] = idx
                sentence_dict['span'] = (current_spans[0][0], current_spans[-1][-1])
                sentence_dict['word_spans'] = current_spans
                sentences.append(sentence_dict)
                #if span[1] in header_points:
                #    print("Split at header")
                #    print(' '.join(current_sentence))

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
        to_exclude = ['infection', 'discharge']
        for sentence_num, sentence in enumerate(self.sentences):
            #print(sentence)
            #print(sentence['text'])
            #print(type(sentence['text']))
            markup = model.markup_sentence(sentence['text'])
            targets = markup.getMarkedTargets()

            # Create annotations out of targets
            # TODO: Prune overlapping annotations
            sentence_annotations = []
            for target in targets:
                annotation = Annotation()
                annotation.from_markup(target, markup, sentence['text'], sentence['span'])
                # If classification is None, this markup should be disregarded
                if not annotation.classification:
                    continue
                annotation.sentence_num = sentence_num
                sentence_annotations.append(annotation)
            sentence_annotations = self.prune_annotations(sentence_annotations)
            for annotation in sentence_annotations:
                if annotation.annotation_type not in to_exclude:
                    self.sentences_with_annotations.append(sentence_num)
                    self.annotations.append(annotation)

    def prune_annotations(self, annotations):
        """
        Prunes annotations by collapsing multiple annotations of the same classification within a sentence
        into one with the largest span
        """
        annotation_classifications = set([a.classification for a in annotations])
        pruned_annotations = []
        for classification in annotation_classifications:
            annotations_of_classification = [a for a in annotations if a.classification == classification]
            if len(annotations_of_classification) == 1:
                pruned_annotations.append(annotations_of_classification[0])
                continue
            # Add information from all of the annotations to the one that will be returned
            # If anything else needs to be added, do it here
            first_annotation = annotations_of_classification[0]
            pruned_annotations.append(first_annotation)

        return pruned_annotations





    def get_annotations(self):
        """
        Returns a list of annotations.
        """
        return self.annotations


    def to_etree(self):
        """
        Creates an eTree XML element
        """
        root = Element('annotations')
        root.set('textSource', self.rpt_id + '.txt')
        # TODO:
        for annotation in self.annotations:
            elements_to_append = annotation.to_etree()
            for element in elements_to_append:
                root.append(element)
            #root.append(annotation.to_etree())
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
        return root
        #return ElementTree.ElementTree(root)


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
        f_out.write(etree.tostring(element_tree, pretty_print=True, encoding='unicode'))
        #element_tree.write(f_out, pretty_print=True, encoding='unicode')
        print("Saved at {}".format(outpath))
        f_out.close()




    def __str__(self):
        string = ''
        string += 'Report: {0}\n'.format(self.rpt_id)
        for sentence_num, sentence in enumerate(self.sentences):
            string += '{text} '.format(**sentence)
            if sentence_num in self.sentences_with_annotations:
                for annotation in [a for a in self.annotations if a.sentence_num == sentence_num]:
                    string +=  annotation.get_short_string() + '\n'
        return string


def main():
    """
    An example of processing one text document.
    """

    # Create a model with modifiers and targets
    targets = os.path.abspath('../lexicon/targets.tsv')
    modifiers = os.path.abspath('../lexicon/modifiers.tsv')
    model = MentionLevelModel(targets, modifiers)

    text = "  Impression: We examined the patient yesterday. He shows signs of pneumonia.\
    The wound is CDI. He has not developed a urinary tract infection\
    However, there is a wound infection near the abdomen. There is no surgical site infection. There is an abscess  Surgical Sites: There is a surgical site infection. Signed, Dr.Doctor MD."
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

"""
This module defines classes that are used to represent texts and annotations.
"""

from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize import WhitespaceTokenizer


class ClinicalTextDocument(object):
    """
    This class is a representation of a single clinical documents.
    It is initialized with `text`, an unprocessed text document.
    In order to preserve the initial document spans,
    this is saved as an attribute `raw_text`.
    """

    def __init__(self, text):
        self.raw_text = text
        self.raw_text_spans = self.get_text_spans(text)
        self.preprocessed_text = self.preprocess(text)
        self.split_text_and_spans = None



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



if __name__ == '__main__':
    string = "The patient shows symptoms of pneumonia. The wound is CDI. \
    He has not developed an urinary tract infection.\n Signed, Dr. Doctor, MD"
    document = ClinicalTextDocument(string)
    print(document.raw_text_spans)
    print(document.preprocessed_text)
    print(document.split_sentences(document.preprocessed_text, document.raw_text_spans))

    exit()
    print(document.raw_text)
    print(PunktSentenceTokenizer.span_tokenize(document))




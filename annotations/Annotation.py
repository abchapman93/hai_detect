"""
This module contains two classes that are used for creating and evaluating NLP findings.
The first is `Annotation`, which can be instantiated using either a pyConText markup or an pandas Series from Excel.
The Annotation object keeps track of temporality, assertion and the class of the findings.
It has the following main attributes:
    - `Annotation.classification`: this is a string representing the final evaluation of the finding. This is created
        based on the logic in `Annotaiton.classify()` and is decided based on annotation_type, temporality, and assertion.
    - `Annotation.annotation_type`: a string representing the class of the finding. This matches the `Class` field in
        an eHOST annotation.
    - `Annotation.attributes`: this is a dictionary that is meant to match the `attributes` in an eHOST annotation.
        It contains these subfields:
        -- `assertion`: whether the finding is negated or postive.
        -- `temporality`: whether the finding currently exists, has in the past, or is a future/hypothetical risk.

The second is `AnnotationComparison`, which is used to compare two overlapping annotations and decide whether they are
a match.
"""

import re
from datetime import datetime
#from xml.etree.ElementTree import Element, SubElement
from lxml.etree import Element, SubElement


class Annotation(object):
    """
    This class represents an annotation of a medical concept from text.
    It can be initialized either from an eHOST knowtator.xml annotation
    or from a pyConText markup.
    """

    # Dictionary mapping pyConText target types to eHOST class names
    # pyConText target => Annotation.annotation_type
    _annotation_schema = {'organ-space surgical site infection': 'Evidence of SSI',
                         'deep surgical site infection': 'Evidence of SSI',
                         'superficial surgical site infection': 'Evidence of SSI',
                         'negated superficial surgical site infection': 'Evidence of SSI',
                          'surgical site infection': 'Evidence of SSI',
                           'urinary tract infection': 'Evidence of UTI',
                           'pneumonia': 'Evidence of Pneumonia'
    }

    # Classifications based on assertion
    # NOTE:
    _annotation_classifications = {'Evidence of SSI': {
                                        'present': 'Positive Evidence of SSI',
                                        'probable': 'Positive Evidence of SSI',
                                        'negated': 'Negated Evidence of SSI',
                                        'indication': 'Indication of SSI'
                                    },
                                    'Evidence of UTI': {
                                        'present': 'Positive Evidence of UTI',
                                        'probable': 'Positive Evidence of UTI',
                                        'negated': 'Negated Evidence of UTI',
                                        'indication': 'Indication of UTI',
                                    },
                                    'Evidence of Pneumonia': {
                                        'present': 'Positive Evidence of Pneumonia',
                                        'probable': 'Postive Evidence of Pneumonia',
                                        'negated': 'Negated Evidence of Pneumonia',
                                        'indication': 'Indication of Pneumonia'
                                    }
    }

    def __init__(self):
        self.sentence = None
        self.datetime = datetime.now().strftime('%m%d%Y %H:%M:%S') # TODO: Change this to match eHOST
        self.id = ''  # TODO: Change this
        self.text = None
        self.sentence_num = None
        self.span_in_sentence = None
        self.span_in_document = None
        self.annotation_type = None # eHOST class names: 'Evidence of SSI', 'Evidence of Pneumonia', 'Evidence of UTI'
        self.attributes = {
            'assertion': 'present', # present, probable, negated, indication
            'temporality': 'current', # current, historical, future/hypothetical
        }


        # These attributes will only be populated if this annotation is instantiated from a markup
        self.modifier_categories = []
        self.markup_category = None
        # Will eventually be 'Positive Evidence of SSI', 'Negated Evidence of Pneumonia', ...
        self._classification = None
        self.annotator = None



    @property
    def classification(self):
        return self._classification


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
        self.id = str(tag_object.getTagID())

        # Get category of target
        self.markup_category = tag_object.getCategory()[0]

        # Find all modifier categories
        self.modifier_categories.extend([mod.getCategory()[0] for mod in markup.getModifiers(tag_object)])

        # Make sure this is an annotation class that we recognize
        #if self.markup_category not in self._annotation_schema:
        #    raise NotImplementedError("{} is not a valid annotation type, must be one of: {}".format(
        #        self.markup_category, set(self._annotation_schema.values())
        #    ))

        # Try mapping the markup TYPE to one of our categories in _annotation_schema
        # If it isn't recognized, just use the markup category
        try:
            self.annotation_type = self._annotation_schema[self.markup_category]
        except KeyError:
            self.annotation_type = self.markup_category



        # Get the entire span in sentence.
        spans = []
        spans.extend(tag_object.getSpan()) # Span of the target term
        for modifier in markup.getModifiers(tag_object):
            spans.extend(modifier.getSpan()) # Spans for each modifier

        self.span_in_sentence = (min(spans), max(spans))

        # Get the span in the entire document.
        #sentence_offset = sentence_span[0]
        #self.span_in_document = (self.span_in_sentence[0] + sentence_offset, self.span_in_sentence[1] + sentence_offset)
        # ALTERNATIVE: setting span to entire sentence instead of just the markup span
        self.span_in_document = sentence_span

        # Add the text for the whole sentence
        self.sentence = sentence
        # And for the annotation itself
        #self.text = sentence[self.span_in_sentence[0]:self.span_in_sentence[1]]
        self.text = sentence


        # Update attributes
        # Case 1-2, 4: A wound or drain description that implies a surgical site infection
        # TODO: If `drain` needs to be treated differently, separate it here
        if self.markup_category in {'anatomy', 'surgical site', 'drain'}:
            self._set_wound_description()

        # Case 3: An explicit mention of a surgical site infection
        elif self.markup_category in {'explicit superficial surgical site infection',
                               'explicit deep surgical site infection',
                               'explicit organ-space surgical site infection'}:
            self._set_explicit_ssi()

        elif self.markup_category == 'urinary tract infection':
            self._set_uti()

        elif self.markup_category == 'pneumonia':
            self._set_pneumonia()

        # Case 5: The risks of surgery
        elif self.markup_category == 'procedure':
            self._set_risk_of_procedure()


        # Now that all of the attributes have been set,
        # we can implement the classification logic
        self.classify()


    def _set_wound_description(self):
        """
        This method sets the attributes for a markup that has a target of the classes
        anatomy, surgical site, or drain. Checks for surgical site modifiers.
        """

        # Cases 1-2: a wound or drain site with description of infection
        if 'negated superficial surgical site infection' in self.modifier_categories:
            self.annotation_type = 'Evidence of SSI'
            self.attributes['ssi_class']= 'superficial' # Corresponds to 'classification' in eHOST schema
            self.attributes['assertion'] = 'negated' # Automatically set assertion to negated, don't look for mods
            self._set_temporal_attributes()

        elif 'superficial surgical site infection' in self.modifier_categories:
            self.annotation_type = 'Evidence of SSI'
            self.attributes['ssi_class']= 'superficial'
            self._set_assertion_attributes()
            self._set_temporal_attributes()


        elif 'deep surgical site infection' in self.modifier_categories:
            self.annotation_type = 'Evidence of SSI'
            self.attributes['ssi_class']= 'deep'
            self._set_assertion_attributes()
            self._set_temporal_attributes()

        elif 'organ-space surgical site infection' in self.modifier_categories:
            self.annotation_type = 'Evidence of SSI'
            self.attributes['ssi_class']= 'organ-space'
            self._set_assertion_attributes()
            self._set_temporal_attributes()



        # Case 4: An opened wound
        elif 'dehiscence' in self.modifier_categories:
            self.annotation_type = 'Evidence of SSI'
            self.attributes['ssi_class']= 'superficial'

        # Otherwise, this is just a mention of an anatomical or surgical site
        # Without any evidence for or against infection and will be excluded
        else:
            pass


    def _set_explicit_ssi(self):
        """
        This method sets the attributes for an explicit mention of surgical site infection.
        Looks at lexical modifiers for assertion and temporality
        """

        self.annotation_type = 'Evidence of SSI'

        if self.markup_category == 'explicit negated superficial surgical site infection':
            self.attributes['ssi_class']= 'superficial' # Corresponds to 'classification' in eHOST schema
            self.attributes['assertion'] = 'negated'

        else:
            self.attributes['ssi_class'] = re.search('explicit ([a-z]+) surgical site infection', self.markup_category).group(1)
            self._set_assertion_attributes()
            self._set_temporal_attributes()


    def _set_risk_of_procedure(self):
        """
        This method checks for infection modifiers and future/hypothetical temporality
        for targets of class 'procedure'.
        """
        ssi_mods = [k for (k, v) in self._annotation_schema.items() if v == 'Evidence of SSI']
        # Check if any SSI modifiers are present
        if len(set(self.modifier_categories).intersection(set(ssi_mods))) > 0:
            # If there are, see if the temporality is future/hypothetical
            self._set_temporal_attributes()
            if self.attributes['temporality'] == 'future/hypothetical':
                self.annotation_type = 'Evidence of SSI'
                self.attributes['ssi_class'] = 'superficial'
            else:
                self.annotation_type = None


    def _set_uti(self):
        """
        This method sets the attributes for UTI.
        Looks at lexical modifiers for assertion and temporality
        """
        self._set_assertion_attributes()
        self._set_temporal_attributes()


    def _set_pneumonia(self):
        """
        This method sets the attributes for UTI.
        Looks at lexical modifiers for assertion and temporality
        """
        self._set_assertion_attributes()
        self._set_temporal_attributes()


    def _set_assertion_attributes(self):
        """
        This method sets the attribute 'assertion' in `self.attributes`. Looks for modifiers of classes
        'negated_existence' or 'probable_existence'. Otherwise is set to 'definite'
        :return:
        """
        if 'definite_negated_existence' in self.modifier_categories or \
                        'probable_negated_existence' in self.modifier_categories:
            self.attributes['assertion'] = 'negated'
        elif 'probable_existence' in self.modifier_categories:
            self.attributes['assertion'] = 'probable'
        else:
            self.attributes['assertion'] = 'present'


    def _set_temporal_attributes(self):
        """
        This methods sets the attributes for temporality for modifiers of class
        'historical' and 'future/hypothetical'. If there are no modifiers,
        temporality is set to 'current'
        """
        if 'future' in self.modifier_categories or 'hypothetical' in self.modifier_categories:
            self.attributes['temporality'] = 'future/hypothetical'
        elif 'historical' in self.modifier_categories:
            self.attributes['temporality'] = 'historical'
        else:
            self.attributes['temporality'] = 'current'


    def classify(self):
        """
        This method applies heuristics for classifying an annotation
        For example, an annotation that has `category` = `surgical site infection`,
        `assertion` = `negated` and `temporality` = `current` would be classified as
        'Negative Evidence of Surgical Site Infection'.

        Sets object's attribute `classification`.
        Returns classification.
        """

        if self.annotation_type == None or self.annotation_type not in self._annotation_classifications:
            return None

        try:
            classification = self._annotation_classifications[self.annotation_type][self.attributes['assertion']]
        except KeyError:
            classification = self.annotation_type
        if self.attributes['temporality'] != 'current':
            classification += ' - {}'.format(self.attributes['temporality'].title())

        # Exclude any annotations of a surgical site infection that doesn't have anatomy
        # TODO: Implement coreference resolution in `from_markup()`

        self._classification = classification
        return classification




    def compare(self, second_annotation):
        pass


    def to_etree(self):
        """
        This method returns an eTree element that represents the annotation
        and can be appended to the rest of the document and saved as a knowtator xml file.
        It returns two etree elements, annotation_body and class_mention.
        eHOST uses both of these to display an annotation.
        """
        elements_to_rtn = []  #  A list of elements that will be returned
                              #  and then appended to the body
        annotation_body = Element('annotation')
        # TO RETURN
        elements_to_rtn.append(annotation_body)

        mention_id = SubElement(annotation_body, 'mention')
        mention_id.set('id', self.id)

        annotator_id = SubElement(annotation_body, 'annotator')
        annotator_id.set('id', 'eHOST_2010')
        annotator_id.text = self.annotator

        span = SubElement(annotation_body, 'span', {'start': str(self.span_in_document[0]),
                                                    'end': str(self.span_in_document[1])})
        spanned_text = SubElement(annotation_body, 'spannedText')
        spanned_text.text = self.text
        creation_date = SubElement(annotation_body, 'creationDate')
        creation_date.text = self.datetime


        # Now create class_mention
        class_mention = Element("classMention")
        class_mention.set("id", self.id)
        # TO RETURN
        elements_to_rtn.append(class_mention)
        #mention_class.set('id', self.classification)
        mention_class = SubElement(class_mention, 'mentionClass')
        mention_class.set('id', self.annotation_type)
        mention_class.text = self.text

        # Add attributes
        # ASSERTION
        # These fields point to stringSlotMention fields that contain  the attributes
        slot_mention_assertion_id = self.id + '1'

        has_slot_mention_assertion = SubElement(class_mention, 'hasSlotMention')
        has_slot_mention_assertion.set('id', slot_mention_assertion_id)

        string_slot_mention_assertion = Element('stringSlotMention')
        # TO RETURN
        elements_to_rtn.append(string_slot_mention_assertion)
        string_slot_mention_assertion.set('id', slot_mention_assertion_id)
        mention_slot_assertion = SubElement(string_slot_mention_assertion, 'mentionSlot')
        mention_slot_assertion.set('id', 'assertion')
        string_slot_mention_value_assertion = SubElement(string_slot_mention_assertion, 'stringSlotMentionValue')
        string_slot_mention_value_assertion.set('value', self.attributes['assertion'])

        # TEMPORALITY
        slot_mention_temporality_id = self.id + '2'
        has_slot_mention_temporality = SubElement(class_mention, 'hasSlotMention')
        has_slot_mention_temporality.set('id', slot_mention_temporality_id)

        string_slot_mention_temporality = Element('stringSlotMention')
        # TO RETURN
        elements_to_rtn.append(string_slot_mention_temporality)
        string_slot_mention_temporality.set('id', slot_mention_temporality_id)
        mention_slot_temporality = SubElement(string_slot_mention_temporality, 'mentionSlot')
        mention_slot_temporality.set('id', 'temporality')
        string_slot_mention_value_temporality = SubElement(string_slot_mention_temporality, 'stringSlotMentionValue')
        string_slot_mention_value_temporality.set('value', self.attributes['temporality'])

        if self.annotation_type != 'Evidence of SSI':
            return elements_to_rtn


        # CLASSIFICATION
        # Add 'classification' field for 'infection_type'
        slot_mention_classification_id = self.id + '3'
        has_slot_mention_classification = SubElement(class_mention, 'hasSlotMention')
        has_slot_mention_classification.set('id', slot_mention_classification_id)

        string_slot_mention_classification = Element('stringSlotMention')
        # TO RETURN
        elements_to_rtn.append(string_slot_mention_classification)
        string_slot_mention_classification.set('id', slot_mention_classification_id)
        mention_slot_classification = SubElement(string_slot_mention_classification, 'mentionSlot')
        mention_slot_classification.set('id', 'classification')
        string_slot_mention_value_classification = SubElement(string_slot_mention_classification, 'stringSlotMentionValue')
        string_slot_mention_value_classification.set('value', self.attributes['ssi_class'])




        return elements_to_rtn
        #return annotation_body, class_mention



    def get_short_string(self):
        """
        This returns a brief string presentation of the annotation
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
            string += '    Infection type: {i}\n'.format(i=self.attributes['ssi_class'])
        string += 'Classification: {c}'.format(c=self.classification)

        return string

class AnnotationComparison(object):
    """
    This class is used to compare two overlapping annotations.
    Parameters:
        a: the first Annotation which should be considered the gold standard
        b: the second overlapping Annotation which will be evaluated against a
        rpt_id: the name of the report the annotations were created from
        assert_map: a dictionary mapping assertion values to integers that define which
             should be considered a match. For example, if 'probable' and 'definite'
            should be considered matches, they could both map to 0.
            and 'negated' could map to 1. This is the default setting.
        temp_map: a dictionary mapping temporality values similar to assert_map.

    """

    def __init__(self, a, b, rpt_id='classification', assert_map={}, temp_map={}):
        self.a = a
        self.b = b
        self.rpt_id = rpt_id

        if len(assert_map) == 0:
            self.assert_map = {
            'definite': 0,
            'probable': 0,
            'negated': 1
        }
        else:
            self.assert_map = assert_map

        if len(temp_map) == 0:
            self.temp_map = {
            'current': 0,
            'historical': 1,
            'future/hypothetical':
        }
        else:
            self.temp_map = temp_map

    @property
    def is_match(self):
        return self.compare_annotations()


    def compare_annotations(self):
        """
        Checks whether annotation type, assertion, and temporality are equal between the two Annotations.
        Assertion and Temporality matches are defined by assert_map and temp_map.
        :returns Boolean
        """
        return self.compare_classification() & self.compare_assertion() & self.compare_temporality()


    def compare_classification(self):
        """
        This method checks whether the classifications of
        the two annotations are exactly the same.
        """
        return self.a.classification() == self.b.classification()


    def compare_assertion(self):
        """
        Compares assertion of both Annotations.
        In this schema, 'definite' and 'probable' are considered equal
        """

        return self.assert_map[self.a.attributes['assertion']] == \
            self.assert_map[self.b.attributes['assertion']]


    def compare_temporality(self):
        """
        Compares temporality of both Annotations.
        :return:
        """

        return self.temp_map[self.a.attributes['temporality']] == \
               self.temp_map[self.b.attributes['temporality']]



if __name__ == '__main__':
    annotation = Annotation()

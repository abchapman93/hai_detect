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
    _annotation_schema = {'organ/space surgical site infection': 'Evidence of SSI',
                         'deep surgical site infection': 'Evidence of SSI',
                         'superficial surgical site infection': 'Evidence of SSI',
                         'negated superficial surgical site infection': 'Evidence of SSI',
                          'surgical site infection': 'Evidence of SSI',
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
        self.datetime = datetime.now().strftime('%m%d%Y %H:%M:%S') # TODO: Change this to match eHOST
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
        self.id = str(tag_object.getTagID())

        # Get category of target
        self.markup_category = tag_object.getCategory()[0]
        # TODO: Do we want to exclude any markups that aren't in the main categories?
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

        # If the target is a surgical site infection,
        # classify the type
        # ['organ/space', 'superficial', 'deep']
        if 'surgical site infection' in self.markup_category:
            try:
                self.attributes['infection_type'] = re.search('([a-z/]*) surgical site infection', self.markup_category).group(1)
            except AttributeError:
                self.attributes['infection_type'] = ''


        # Get the entire span in sentence.
        spans = []
        spans.extend(tag_object.getSpan()) # Span of the target term
        for modifier in markup.getModifiers(tag_object):
            spans.extend(modifier.getSpan()) # Spans for each modifier

        self.span_in_sentence = (min(spans), max(spans))

        # Get the span in the entire document.
        #sentence_offset = sentence_span[0]
        #self.span_in_document = (self.span_in_sentence[0] + sentence_offset, self.span_in_sentence[1] + sentence_offset)
        # NOTE: setting span to entire sentence instead of just the markup span
        self.span_in_document = sentence_span

        # Add the text for the whole sentence
        self.sentence = sentence
        # And for the annotation itself
        #self.text = sentence[self.span_in_sentence[0]:self.span_in_sentence[1]]
        self.text = sentence

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
        elif 'definite_negated_existence' in self.modifier_categories or 'probable_negated_existence' in self.modifier_categories:
            self.attributes['assertion'] = 'negated'
        elif 'indication' in self.modifier_categories:
            self.attributes['assertion'] = 'indication'
        elif 'probable_existence' in self.modifier_categories:
            self.attributes['assertion'] = 'probable'


        # TODO: Update temporality
        if 'future' in self.modifier_categories or 'hypothetical' in self.modifier_categories:
            self.attributes['temporality'] = 'future/hypothetical'
        if 'historical' in self.modifier_categories:
            self.attributes['temporality'] = 'historical'



        # Add anatomical sites to instances of surgical site infections
        if 'surgical site infection' in self.markup_category or self.markup_category == 'infection':
                self.attributes['anatomy'] = [mod.getLiteral() for mod in markup.getModifiers(tag_object)
                                          if 'anatomy' in mod.getCategory() or
                                          'surgical_site' in mod.getCategory()]

        # TODO: Create a flow chart showing this logic

        # If there is no anatomical site for a positive surgical site infection
        # Change the class
        if self.annotation_type == 'Evidence of SSI' and len(self.attributes['anatomy']) == 0\
                and self.attributes['assertion'] == 'positive'\
                and self.attributes['temporality'] == 'current':
            self.annotation_type = 'Evidence of SSI - No Anatomy'

        # If there is an anatomical site and assertion is positive,
        # or assertion is negative,
        # change 'infection' annotations to 'Evidence of SSI'
        if self.annotation_type == 'infection':
            #print("This is an infection")
            #print(self.attributes['assertion'])
            #print(self.attributes['anatomy'])
            if self.attributes['assertion'] in ('positive', 'probable') and len(self.attributes['anatomy']) > 0:
                self.annotation_type = 'Evidence of SSI'
            elif self.attributes['assertion'] == 'negated':
                self.annotation_type = 'Evidence of SSI'

        classification = self.classify()
        #print(classification)



    def classify(self):
        """
        This method applies heuristics for classifying an annotation
        For example, an annotation that has `category` = `surgical site infection`,
        `assertion` = `negated` and `temporality` = `current` would be classified as
        'Negative Evidence of Surgical Site Infection'.

        Sets object's attribute `classification`.
        Returns classification.
        """
        #print(self.annotation_type)
        try:
            classification = self._annotation_classifications[self.annotation_type][self.attributes['assertion']]
        except KeyError:
            #print("Unknown:")
            #print(self.annotation_type)
            classification = self.annotation_type
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

        #TODO: 'classification' for SSIs
        #slot_mention3_id = self.id + '3'
        return elements_to_rtn
        #return annotation_body, class_mention



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
            #string += '    Infection type: {i}\n'.format(i=self.attributes['infection_type'])
        string += 'Classification: {c}'.format(c=self.classification)

        return string

if __name__ == '__main__':
    annotation = Annotation()

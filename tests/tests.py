import unittest
import os

import pyConTextNLP.itemData as itemData

from annotations import Annotation, ClinicalTextDocument
from models.mention_level_models import MentionLevelModel


class TestAnnotations(unittest.TestCase):

    def setUp(self):
        self.targets = os.path.abspath('../lexicon/targets.tsv')
        self.modifiers = os.path.abspath('../lexicon/modifiers.tsv')

        try:
            itemData.instantiateFromCSVtoitemData(self.modifiers)
        except IndexError as e:
            print("Modifiers failed to load")
            raise e
        try:
            itemData.instantiateFromCSVtoitemData(self.targets)
        except IndexError as e:
            print("Targets failed to load")
            raise e


        #targets = 'https://raw.githubusercontent.com/abchapman93/hai_detect/master/lexicon/targets.tsv'
        #modifiers = 'https://raw.githubusercontent.com/abchapman93/hai_detect/master/lexicon/modifiers.tsv'
        self.model = MentionLevelModel(self.targets, self.modifiers)

        self.doc1 = ClinicalTextDocument.ClinicalTextDocument('There is an abscess near the abdomen.')
        self.doc1.annotate(self.model)
        self.annotation_pos_ssi1 = self.doc1.annotations[0]

        self.doc2 = ClinicalTextDocument.ClinicalTextDocument('There is no erythema to be seen along the surgical site.')
        self.doc2.annotate(self.model)
        self.annotation_neg_ssi2 = self.doc2.annotations[0]

        self.doc3 = ClinicalTextDocument.ClinicalTextDocument('We discussed the risks of surgery, including abscess and \
                                                              erythema.')
        self.doc3.annotate(self.model)
        self.annotation_hyp_ssi3 = self.doc3.annotations[0]

        self.doc4 = ClinicalTextDocument.ClinicalTextDocument('There is abscess.')
        self.doc4.annotate(self.model)


        self.doc5 = ClinicalTextDocument.ClinicalTextDocument('The patient has a history of wound infection.')
        self.doc5.annotate(self.model)
        self.annotation_hist_ssi5 = self.doc5.annotations[0]


    def test_modifiers_load(self):
        try:
            itemData.instantiateFromCSVtoitemData(self.modifiers)
        except IndexError as e:
            self.fail(msg="Modifiers failed to load")


    def test_targets_load(self):
        try:
            itemData.instantiateFromCSVtoitemData(self.targets)
        except IndexError as e:
            self.fail(msg="Targets failed to load.")


    def test_doc1_has_positive_ssi(self):
        self.assertEqual(self.annotation_pos_ssi1.classification, 'Positive Evidence of SSI', msg='doc1 classification failed')


    def test_doc2_has_neg_ssi(self):
        self.assertEqual(self.annotation_neg_ssi2.classification, 'Negated Evidence of SSI')


    def test_doc3_has_hyp_ssi(self):
        self.assertEqual(self.annotation_hyp_ssi3.classification, 'Positive Evidence of SSI - Future/Hypothetical')


    def test_doc4_has_no_annotation(self):
        self.assertEqual(len(self.doc4.annotations), 0, 'Doc4 has an annotation when it should have none.')


    def test_doc5_has_pos_hist_ssi(self):
        self.assertEqual(self.annotation_hist_ssi5.classification, 'Positive Evidence of SSI - Historical')

    def test_doc5_has_hist_mod(self):
        self.assertEqual(self.annotation_hist_ssi5.attributes['temporality'], 'historical')
        #self.assertEqual()



if __name__ == '__main__':
    unittest.main()

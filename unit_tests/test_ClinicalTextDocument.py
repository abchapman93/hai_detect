import os
import unittest
from annotations.Annotation import Annotation
from annotations.ClinicalTextDocument import ClinicalTextDocument
from models.mention_level_models import MentionLevelModel

class test_ClinicalTextDocument(unittest.TestCase):

        
    
    anno_bin = []
    def setUp(self):
        # self._makeAnnotationsList()
        pass

    def tearDown(self):
        pass
    
    # def _anno(self, span, classy, attri):
    #     anno = Annotation()
    #     anno.span_in_sentence = span
    #     anno._classification = classy
    #     anno.attributes = attri
    #     return anno
    
    # def _makeAnnotationsList(self):
        
    #     #Set1 
    #     self.anno_bin.append(self._anno((1,10), 'SSI', {'assertion':'positive', 
    #                                                             'temporality':'current',
    #                                                             'anatomy':['superficial']}))
                                                                
    #     self.anno_bin.append(self._anno((11,15), 'Pneumonia', {'assertion':'positive', 
    #                                                             'temporality':'histroical',
    #                                                             'anatomy':['Pneumonia']}))
                                                                
    #     self.anno_bin.append(self._anno((20,30), 'UTI', {'assertion':'positive', 
    #                                                      'temporality':'histroical',
    #                                                       'anatomy':['UTI']}))
                                                                
    #     self.anno_bin.append(self._anno((40,50), 'SSI', {'assertion':'Negative', 
    #                                                             'temporality':'current',
    #                                                             'anatomy':['feet']}))
                                                                
    #     self.anno_bin.append(self._anno((50,60), 'Pneumonia', {'assertion':'negative', 
    #                                                             'temporality':'current',
    #                                                             'anatomy':['Pneumonia']}))
    #     #_set2
        
    #     #_overlap but should be the same
    #     self.anno_bin.append(self._anno((3,10), 'SSI', {'assertion':'positive', 
    #                                                             'temporality':'current',
    #                                                             'anatomy':['superficial']}))
                                                                
    #     self.anno_bin.append(self._anno((13,15), 'Pneumonia', {'assertion':'positive', 
    #                                                             'temporality':'histroical',
    #                                                             'anatomy':['Pneumonia']}))
                                                                
    #     self.anno_bin.append(self._anno((23,30), 'UTI', {'assertion':'positive', 
    #                                                      'temporality':'histroical',
    #                                                       'anatomy':['UTI']}))
                                                                
    #     self.anno_bin.append(self._anno((40,47), 'SSI', {'assertion':'Negative', 
    #                                                             'temporality':'current',
    #                                                             'anatomy':['feet']}))
                                                                
    #     self.anno_bin.append(self._anno((52,58), 'Pneumonia', {'assertion':'negative', 
    #                                                             'temporality':'current',
    #                                                             'anatomy':['Pneumonia']}))
                                                                
    #     #SET 3                                              
    #       #_overlap and not the same
    #     self.anno_bin.append(self._anno((3,10), 'Pneumonia', {'assertion':'positive', 
    #                                                             'temporality':'histroical',
    #                                                             'anatomy':['Pneumonia']}))
        
        
    #     self.anno_bin.append(self._anno((13,15), 'SSI', {'assertion':'positive', 
    #                                                             'temporality':'current',
    #                                                             'anatomy':['superficial']}))
                                                                
    #     self.anno_bin.append(self._anno((23,30), 'SSI', {'assertion':'Negative', 
    #                                                             'temporality':'current',
    #                                                             'anatomy':['feet']}))
                                                                
    #     self.anno_bin.append(self._anno((40,47), 'UTI', {'assertion':'positive', 
    #                                                      'temporality':'histroical',
    #                                                       'anatomy':['UTI']}))
                                                                
                                                                
    #     self.anno_bin.append(self._anno((52,58), 'UTI', {'assertion':'negative', 
    #                                                             'temporality':'current',
    #                                                             'anatomy':['Pneumonia']}))
                                                                
                                                                
    #     #_overlap and  same as set 2
    #     self.anno_bin.append(self._anno((3,9), 'Pneumonia', {'assertion':'positive', 
    #                                                             'temporality':'histroical',
    #                                                             'anatomy':['Pneumonia']}))
        
        
    #     self.anno_bin.append(self._anno((12,15), 'SSI', {'assertion':'positive', 
    #                                                             'temporality':'current',
    #                                                             'anatomy':['superficial']}))
                                                                
    #     self.anno_bin.append(self._anno((21,31), 'SSI', {'assertion':'Negative', 
    #                                                             'temporality':'current',
    #                                                             'anatomy':['feet']}))
                                                                
    #     self.anno_bin.append(self._anno((39,52), 'UTI', {'assertion':'positive', 
    #                                                      'temporality':'histroical',
    #                                                       'anatomy':['UTI']}))
                                                                
                                                                
    #     self.anno_bin.append(self._anno((48,62), 'UTI', {'assertion':'negative', 
    #                                                             'temporality':'current',
    #                                                             'anatomy':['Pneumonia']}))
                                                                
                                                                                                

 
    
    def test_annotate(self):
        print ('')
        targets = os.path.abspath('./lexicon/targets.tsv')
        modifiers = os.path.abspath('./lexicon/modifiers.tsv')
        model = MentionLevelModel(targets, modifiers)
        
        neg_multi = \
        """
            bdomen: flat, no distention. Patient bowel sounds normal, nontender, no masses,
            no organomegally and no guarding surgical sites: is healing well assessment: 
            35 year old male demonstrates improved pain control status post non-perforated appendicitis.
        """
            
        ssi_single = \
        """
            idline wound with 0.5 cm defect at the superior aspect with small amount of purulent drainage,
            additional 0.5cm defect at the umbilicus, both repacked with nu-gauze..
        """
        
        ssi_multi_joined = \
        """
           her wound was examined, 
           She had indicated some discomforted,
           I observed small amount of purulent drainage
           I will follow up by phone 
        """
        
        ssi_multi = \
        """
           her wound was examined. 
           After lengthy visit and she had indicated some discomforted.
           I observed small amount of purulent drainage.
           I will follow up by phone.
        """
        
        doc = ClinicalTextDocument(neg_multi)
        doc.annotate(model)
    
        self.assertTrue(doc.annotations['hai_detect'][0].classification, 'Negated Evidence of SSI - Historical')
        
        
        doc = ClinicalTextDocument(ssi_single)
        doc.annotate(model)
        self.assertTrue(doc.annotations['hai_detect'][0].classification, 'Positive Evidence of SSI')
        
        print ('---------ssi multi joined--------')
        doc = ClinicalTextDocument(ssi_multi_joined)
        doc.annotate(model)
        self.assertTrue(doc.annotations['hai_detect'][0].classification, 'Positive Evidence of SSI')
        
        
        print ('--------- ssi MULTI -----------')
        doc = ClinicalTextDocument(ssi_multi)
        doc.annotate(model)
        
        self.assertTrue(doc.annotations['hai_detect'][0].classification, 'Positive Evidence of SSI')
        
        
        
        
    # def test_xxperiment(self):
     
       
    #     pass
        
        
if __name__ == '__main__':
    suit = unittest.TestLoader().loadTestsFromTestCase(test_ClinicalTextDocument)
    unittest.TextTestRunner(verbosity=2).run(suit)

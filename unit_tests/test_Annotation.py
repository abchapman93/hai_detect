import unittest
from annotations.Annotation import Annotation
import os.path
from openpyxl import load_workbook
from hai_exceptions.exceptions import MalformedeHostExcelRow, MalformedSpanValue


class test_Annotation(unittest.TestCase):
    annotation = Annotation()
    def setUp(self):
        
        self.annotation = Annotation()
        try:
            self.annotation.attributes.pop('assertion')
            self.annotation.attributes.pop('temporality')
        except KeyError:
            pass

    def tearDown(self):
        pass
        
    def test_classify(self):
        
        annotation = Annotation()
        annotation.annotation_type = 'Evidence of SSI'
        retVal = annotation.classify()
        self.assertEqual(retVal, 'Positive Evidence of SSI')
        
        
        annotation.attributes['anatomy'] = ['Arm']
        retVal = annotation.classify()
        self.assertEqual(retVal, 'Positive Evidence of SSI')
        
        annotation.annotation_type = "HELLO WORLD"
        retVal = annotation.classify()
        
    
    # def test_from_ehost_xlsx(self):
    #     sampleFile = "sample_annotations.xlsx"
    #     self.assertEqual(os.path.isfile(sampleFile), True)
        
        
    #     wb = load_workbook(filename=sampleFile, read_only=False)
    #     ws=wb.active # just getting the first worksheet regardless of its name
        
        
    #     self.setUp()
    #     annotation = self.annotation
        
        
    #     row = list(ws)[2]
    #     annotation.from_ehost_xlsx(row)
        
    #     self.assertEqual(annotation.sentence, "drains")
    #     self.assertEqual(annotation.annotation_type, "DRAINAGE") 
    #     self.assertEqual(annotation.span_in_sentence, (2608, 2614))
    #     self.assertRaises(KeyError, lambda: annotation.attributes['classification'])
    #     self.assertRaises(KeyError, lambda: annotation.attributes['assertion'])
    #     self.assertRaises(KeyError, lambda: annotation.attributes['temporality'])
   
        
        
    #     self.setUp()
    #     annotation = self.annotation
    #     row = list(ws)[3]
    #     annotation.from_ehost_xlsx(row)
            
    #     self.assertEqual(annotation.sentence, "3 drains in place with serosanguinous output")
    #     self.assertEqual(annotation.annotation_type, "Evidence of SSI")
    #     self.assertEqual(annotation.span_in_sentence, ( 1234,15069))
    #     self.assertEqual(annotation.attributes['classification'],"superficial" )
    #     self.assertEqual(annotation.attributes['assertion'],"negated")
    #     self.assertEqual(annotation.attributes['temporality'],"current")
            
    #     self.setUp()  
    #     annotation = self.annotation
    #     row = list(ws)[4]
    #     annotation.from_ehost_xlsx(row)
        
            
    #     self.assertEqual(annotation.sentence, "Patient has a history of UTI")
    #     self.assertEqual(annotation.annotation_type, "Evidence of UTI")
    #     self.assertEqual(annotation.span_in_sentence, ( 2261,2305))
    #     self.assertEqual(annotation.attributes['classification'],"Evidence of UTI" )
    #     self.assertEqual(annotation.attributes['assertion'],"positive")
    #     self.assertEqual(annotation.attributes['temporality'],"historical")

        
    #     self.setUp()
    #     annotation = self.annotation
    #     row = list(ws)[5]
    #     self.assertRaises(MalformedSpanValue, lambda: annotation.from_ehost_xlsx(row))
         
    #     self.assertIs(annotation.sentence, None)
    #     self.assertIs(annotation.annotation_type, None)
    #     self.assertIs(annotation.span_in_sentence, None)
    #     self.assertRaises(KeyError, lambda: annotation.attributes['classification'])
    #     self.assertRaises(KeyError, lambda: annotation.attributes['assertion'])
    #     self.assertRaises(KeyError, lambda: annotation.attributes['temporality'])
   
    #     self.setUp()
    #     annotation = self.annotation
    #     row = list(ws)[6]
    #     self.assertRaises(MalformedSpanValue, lambda: annotation.from_ehost_xlsx(row))
         
    #     self.assertIs(annotation.sentence, None)
    #     self.assertIs(annotation.annotation_type, None)
    #     self.assertIs(annotation.span_in_sentence, None)
    #     self.assertRaises(KeyError, lambda: annotation.attributes['classification'])
    #     self.assertRaises(KeyError, lambda: annotation.attributes['assertion'])
    #     self.assertRaises(KeyError, lambda: annotation.attributes['temporality'])
   
    def _anno_overlap(self, left, right, threshold=0.01):
        return (left.isOverlap(right, threshold) 
                and right.isOverlap(left, threshold))
    
    def test_isOverlap(self):
        left = Annotation()
        right = Annotation()
        left.span_in_document = None
        right.span_in_document = None
        self.assertFalse(self._anno_overlap(left, right))
        
        left.span_in_document = (1,10)
        right.span_in_document = None
        self.assertFalse(self._anno_overlap(left, right))

        left.span_in_document = (1,10)
        right.span_in_document = (11, 20)
        
        self.assertFalse(self._anno_overlap(left, right))
        
        left.span_in_document = (1, 10)
        right.span_in_document = (10, 20)
        self.assertFalse(self._anno_overlap(left, right))
        
        left.span_in_document = (1, 11)
        right.span_in_document = (10, 20)
        self.assertFalse(self._anno_overlap(left, right, 0.30))
        
        left.span_in_document = (1, 11)
        right.span_in_document = (10, 20)
        self.assertFalse(self._anno_overlap(left, right, 0.20))
        
        left.span_in_document = (1, 11)
        right.span_in_document = (10, 20)
        self.assertTrue(self._anno_overlap(left, right, 0.10)) 
        
        
        left.span_in_document = (1, 10)
        right.span_in_document = (1, 10)
        self.assertTrue(self._anno_overlap(left, right))
        
        left.span_in_document = (1, 10)
        right.span_in_document = (8, 20)
        self.assertTrue(self._anno_overlap(left, right))
        
        left.span_in_document = (1, 10)
        right.span_in_document = (9, 10)
        self.assertTrue(self._anno_overlap(left, right))
        
        left.span_in_document = (1, 10)
        right.span_in_document = (1, 5)
        self.assertTrue(self._anno_overlap(left, right))
        
        left.span_in_document = (11, 11)
        right.span_in_document = (9, 11)
        self.assertFalse(self._anno_overlap(left, right))
        
    # def test_isSimilar(self):
    #     left = Annotation()
    #     right = Annotation()
    #     self.assertTrue(left.isSimilar(right)) #empty annotation can be similar? 
        
    #     left.span_in_document = (1,10)
    #     right.span_in_document = (2,10)
    #     self.assertTrue(left.isSimilar(right)) #overlap and empty then is similar


    #     left.span_in_document = (1,10)
    #     right.span_in_document = (2,10)
    #     left. = "SSI"
    #     right._classification = ""
        
    #     self.assertFalse(left.isSimilar(right)) #overlap but attri differs 
        
    #     left.span_in_document = (1,10)
    #     right.span_in_document = (2,10)
    #     left.classification = "SSI"
    #     right.classification = "SSI"
    #     self.assertTrue(left.isSimilar(right)) #overlap but attri differs 
        

    #     left.span_in_document = (1,10)
    #     right.span_in_document = (2,10)
    #     left.classification = "SSI"
    #     left.attributes = {'assertion':'positive', 
    #                     'temporality':'current', 
    #                     'anatomy':[],
    #     }
    #     right.classification = "SSI"
    #     right.attributes = {}
    #     self.assertFalse(left.isSimilar(right)) #overlap but attri differs 



    #     left.span_in_document = (1,10)
    #     right.span_in_document = (2,10)
    #     left.classification = "SSI"
    #     left.attributes = {'assertion':'positive', 
    #                     'temporality':'current', 
    #                     'anatomy':[],
    #     }
    #     right.classification = "SSI"
    #     right.attributes = {'assertion':'positive', 
    #                     'temporality':'current', 
    #                     'anatomy':[],
    #     }
    #     self.assertTrue(left.isSimilar(right)) #overlap but attri differs 



    #     left.span_in_document = (1,10)
    #     right.span_in_document = (2,10)
    #     left.classification = "SSI"
    #     left.attributes = {'assertion':'positive', 
    #                     'temporality':'current', 
    #                     'anatomy':["surgical site"],
    #     }
    #     right.classification = "SSI"
    #     right.attributes = {'assertion':'positive', 
    #                     'temporality':'future', 
    #                     'anatomy':[],
    #     }
    #     self.assertFalse(left.isSimilar(right)) #overlap but attri differs 

    #     left.span_in_document = (1,10)
    #     right.span_in_document = (2,10)
    #     left.classification = "SSI"
    #     left.attributes = {'assertion':'positive', 
    #                     'temporality':'current', 
    #                     'anatomy':["surgical site"],
    #     }
    #     right.classification = "SSI"
    #     right.attributes = {'assertion':'positive', 
    #                     'temporality':'current', 
    #                     'anatomy':[],
    #     }
    #     self.assertFalse(left.isSimilar(right)) #overlap but attri differs 



    #     left.span_in_document = (1,10)
    #     right.span_in_document = (2,10)
    #     left.classification = "SSI"
    #     left.attributes = {'assertion':'positive', 
    #                     'temporality':'current', 
    #                     'anatomy':["surgical site"],
    #     }
    #     right.classification = "SSI"
    #     right.attributes = {'assertion':'positive', 
    #                     'temporality':'current', 
    #                     'anatomy':["surgical site"],
    #     }
    #     self.assertTrue(left.isSimilar(right)) #overlap but attri differs 



    #     # left.span_in_document = (1,10)
    #     # right.span_in_document = (11, 20)
        
    #     # self.assertFalse(self._anno_overlap(left, right))
        
    #     # left.span_in_document = (1, 10)
    #     # right.span_in_document = (10, 20)
    #     # self.assertFalse(self._anno_overlap(left, right))

   
        
        
if __name__ == '__main__':
    suit = unittest.TestLoader().loadTestsFromTestCase(test_Annotation)
    unittest.TextTestRunner(verbosity=2).run(suit)

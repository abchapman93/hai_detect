import unittest
from annotations.Annotation import Annotation
import os.path
from openpyxl import load_workbook


class test_Annotation(unittest.TestCase):
    annotation = Annotation()
    def setUp(self):
        self.annotation = Annotation()
        self.annotation.attributes.pop('assertion')
        self.annotation.attributes.pop('temporality')

    def tearDown(self):
        pass
        
    def test_classify(self):
        
        annotation = Annotation()
        annotation.annotation_type = 'Evidence of SSI'
        retVal = annotation.classify()
        self.assertEqual(retVal, 'Positive Evidence of SSI - No Anatomy')
        
        
        annotation.attributes['anatomy'] = ['Arm']
        retVal = annotation.classify()
        self.assertEqual(retVal, 'Positive Evidence of SSI')
        
        annotation.annotation_type = "HELLO WORLD"
        retVal = annotation.classify()
        
        
    def test_from_ehost_xlsx(self):
        sampleFile = "sample_annotations.xlsx"
        self.assertEqual(os.path.isfile(sampleFile), True)
        
        
        wb = load_workbook(filename=sampleFile, read_only=False)
        ws=wb.active # just getting the first worksheet regardless of its name
        
        
        self.setUp()
        annotation = self.annotation
        
        
        row = list(ws)[2]
        annotation.from_ehost_xlsx(row);
        
        self.assertEqual(annotation.sentence, "drains")
        self.assertEqual(annotation.annotation_type, "DRAINAGE")
        self.assertRaises(KeyError, lambda: annotation.attributes['classification'])
        self.assertRaises(KeyError, lambda: annotation.attributes['assertion'])
        self.assertRaises(KeyError, lambda: annotation.attributes['temporality'])
   
        
        
        self.setUp()
        row = list(ws)[3]
        annotation.from_ehost_xlsx(row);
            
        self.assertEqual(annotation.sentence, "3 drains in place with serosanguinous output")
        self.assertEqual(annotation.annotation_type, "Evidence of SSI")
        self.assertEqual(annotation.attributes['classification'],"superficial" )
        self.assertEqual(annotation.attributes['assertion'],"negated")
        self.assertEqual(annotation.attributes['temporality'],"current")
            
        self.setUp()  
        row = list(ws)[4]
        annotation.from_ehost_xlsx(row);
            
        self.assertEqual(annotation.sentence, "Patient has a history of UTI")
        self.assertEqual(annotation.annotation_type, "Evidence of UTI")
        self.assertEqual(annotation.attributes['classification'],"Evidence of UTI" )
        self.assertEqual(annotation.attributes['assertion'],"positive")
        self.assertEqual(annotation.attributes['temporality'],"historical")

        
        self.setUp()
        row = list(ws)[5]
        annotation.from_ehost_xlsx(row);
        
        self.assertIs(annotation.sentence, None)
        self.assertEqual(annotation.annotation_type, None)
        self.assertEqual(annotation.attributes['classification'],"Evidence of UTI" )
        self.assertEqual(annotation.attributes['assertion'],"positive")
        self.assertEqual(annotation.attributes['temporality'],"historical")

        
        
if __name__ == '__main__':
    suit = unittest.TestLoader().loadTestsFromTestCase(test_Annotation)
    unittest.TextTestRunner(verbosity=2).run(suite)
import unittest
from annotations.Annotation import Annotation
import os.path


class test_Annotation(unittest.TestCase):
    def setup(self):
        annotation = Annotation()
        annotation.id="1234567890"
        
    
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
        annotation = Annotation()
        
        annotation.from_ehost_xlsx('myPath')
        mynewId = annotation.id
        self.assertEqual(mynewId, "12345")
        
        self.assertEqual(os.path.isfile("sample_annotations.xlsx"), True)
        self.assertEqual(annotation.from_ehost_xlsx('myPath'), False)
        self.assertEqual(annotation.from_ehost_xlsx('sample_annotations.xlsx'), True)
        
        
        
        
if __name__ == '__main__':
    suit = unittest.TestLoader().loadTestsFromTestCase(test_Annotation)
    unittest.TextTestRunner(verbosity=2).run(suite)
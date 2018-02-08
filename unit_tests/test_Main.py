import unittest
from annotations.Annotation import Annotation
import os.path
from openpyxl import load_workbook
from hai_exceptions.exceptions import MalformedeHostExcelRow, MalformedSpanValue
# from compare_annotation import import_from_xlsx


class test_Main(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass
        
    # def test_import_from_xlsx(self):
        
    #     sampleFile = "sample_annotations_large.xlsx"
    #     self.assertEqual(os.path.isfile(sampleFile), True)
    #     wb = load_workbook(filename=sampleFile, read_only=False)
    #     ws=wb.active # just getting the first worksheet regardless of its name
    #     self.assertEqual(len(list(ws)), 363)
        
    #     mydocs = import_from_xlsx(sampleFile)
    #     self.assertIs(type(mydocs),dict)
      
      
    #     self.assertEqual(len(mydocs), 47)
    #     sample_doc = "no_234858_392582886_01-06-2014_PHYSICIAN_Progress_Notes.txt"
    #     self.assertEqual(len(mydocs[sample_doc].annotations), 10) #10 annotations
        
    #     anno = mydocs[sample_doc].annotations[0]
    #     self.assertEqual(anno.span_in_sentence, ( 1288,1303))
    #     self.assertEqual(anno.annotation_type, "INCISION")
        
    #     anno = mydocs[sample_doc].annotations[3]
    #     self.assertEqual(anno.span_in_sentence, ( 1288,1361))
    #     self.assertEqual(anno.annotation_type, "Evidence of SSI")
    #     sentence = "Surgical Sites: is healing well and has no signs or symptoms of infection"
    #     self.assertEqual(anno.sentence, sentence)
    #     self.assertEqual(anno.attributes["assertion"],"negated")
    #     self.assertEqual(anno.attributes["classification"],"superficial")
    #     self.assertEqual(anno.attributes["temporality"],"current")


    #     anno = mydocs[sample_doc].annotations[4]
    #     self.assertEqual(anno.span_in_sentence, ( 2090,2157))
    #     self.assertEqual(anno.annotation_type, "HAI Status")
    #     sentence = "Based on THIS DOCUMENT ONLY the patient DOES or DOES NOT have a HAI"
    #     self.assertEqual(anno.sentence, sentence)
    #     self.assertEqual(anno.attributes["Surgical Site Infection"],"No")
    #     self.assertEqual(anno.attributes["Urinary Tract Infection"],"No")
    #     self.assertEqual(anno.attributes["Pneumonia"],"No")

       
        
        
    #     sample_doc = 'yes_999508_448838701_05-24-2014_PHYSICIAN_Progress_Notes.txt'
    #     self.assertEqual(len(mydocs[sample_doc].annotations), 2) #10 annotations
        
    #     anno = mydocs[sample_doc].annotations[0]
    #     self.assertEqual(anno.span_in_sentence, ( 404,471))
    #     self.assertEqual(anno.annotation_type, "HAI Status")
    #     sentence = "Based on THIS DOCUMENT ONLY the patient DOES or DOES NOT have a HAI"
    #     self.assertEqual(anno.sentence, sentence)
    #     self.assertEqual(anno.attributes["Surgical Site Infection"],"No")
    #     self.assertEqual(anno.attributes["Urinary Tract Infection"],"No")
    #     self.assertEqual(anno.attributes["Pneumonia"],"No")

    #     anno = mydocs[sample_doc].annotations[1]
    #     self.assertEqual(anno.span_in_sentence, ( 404,471))
    #     self.assertEqual(anno.annotation_type, "HAI Status")
    #     sentence = "Based on THIS DOCUMENT ONLY the patient DOES or DOES NOT have a HAI"
    #     self.assertEqual(anno.sentence, sentence)
    #     self.assertEqual(anno.attributes["Surgical Site Infection"],"No")
    #     self.assertEqual(anno.attributes["Urinary Tract Infection"],"No")
    #     self.assertEqual(anno.attributes["Pneumonia"],"No")



        
        
        
    # def test_xxperiment(self):
     
       
    #     pass
        
        
if __name__ == '__main__':
    suit = unittest.TestLoader().loadTestsFromTestCase(test_Annotation)
    unittest.TextTestRunner(verbosity=2).run(suit)

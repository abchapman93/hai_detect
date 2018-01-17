import unittest
from annotations.Annotation import Annotation
from annotations.ClinicalTextDocument import ClinicalTextDocument

class test_ClinicalTextDocument(unittest.TestCase):
    
    anno_bin = []
    def setUp(self):
        self._makeAnnotationsList()
        pass

    def tearDown(self):
        pass
    
    def _anno(self, span, classy, attri):
        anno = Annotation()
        anno.span_in_sentence = span
        anno.classification = classy
        anno.attributes = attri
        return anno
    
    def _makeAnnotationsList(self):
        
        #Set1 
        self.anno_bin.append(self._anno((1,10), 'SSI', {'assertion':'positive', 
                                                                'temporality':'current',
                                                                'anatomy':['superficial']}))
                                                                
        self.anno_bin.append(self._anno((11,15), 'Pneumonia', {'assertion':'positive', 
                                                                'temporality':'histroical',
                                                                'anatomy':['Pneumonia']}))
                                                                
        self.anno_bin.append(self._anno((20,30), 'UTI', {'assertion':'positive', 
                                                         'temporality':'histroical',
                                                          'anatomy':['UTI']}))
                                                                
        self.anno_bin.append(self._anno((40,50), 'SSI', {'assertion':'Negative', 
                                                                'temporality':'current',
                                                                'anatomy':['feet']}))
                                                                
        self.anno_bin.append(self._anno((50,60), 'Pneumonia', {'assertion':'negative', 
                                                                'temporality':'current',
                                                                'anatomy':['Pneumonia']}))
        #_set2
        
        #_overlap but should be the same
        self.anno_bin.append(self._anno((3,10), 'SSI', {'assertion':'positive', 
                                                                'temporality':'current',
                                                                'anatomy':['superficial']}))
                                                                
        self.anno_bin.append(self._anno((13,15), 'Pneumonia', {'assertion':'positive', 
                                                                'temporality':'histroical',
                                                                'anatomy':['Pneumonia']}))
                                                                
        self.anno_bin.append(self._anno((23,30), 'UTI', {'assertion':'positive', 
                                                         'temporality':'histroical',
                                                          'anatomy':['UTI']}))
                                                                
        self.anno_bin.append(self._anno((40,47), 'SSI', {'assertion':'Negative', 
                                                                'temporality':'current',
                                                                'anatomy':['feet']}))
                                                                
        self.anno_bin.append(self._anno((52,58), 'Pneumonia', {'assertion':'negative', 
                                                                'temporality':'current',
                                                                'anatomy':['Pneumonia']}))
                                                                
        #SET 3                                              
          #_overlap and not the same
        self.anno_bin.append(self._anno((3,10), 'Pneumonia', {'assertion':'positive', 
                                                                'temporality':'histroical',
                                                                'anatomy':['Pneumonia']}))
        
        
        self.anno_bin.append(self._anno((13,15), 'SSI', {'assertion':'positive', 
                                                                'temporality':'current',
                                                                'anatomy':['superficial']}))
                                                                
        self.anno_bin.append(self._anno((23,30), 'SSI', {'assertion':'Negative', 
                                                                'temporality':'current',
                                                                'anatomy':['feet']}))
                                                                
        self.anno_bin.append(self._anno((40,47), 'UTI', {'assertion':'positive', 
                                                         'temporality':'histroical',
                                                          'anatomy':['UTI']}))
                                                                
                                                                
        self.anno_bin.append(self._anno((52,58), 'UTI', {'assertion':'negative', 
                                                                'temporality':'current',
                                                                'anatomy':['Pneumonia']}))
                                                                
                                                                
        #_overlap and  same as set 2
        self.anno_bin.append(self._anno((3,9), 'Pneumonia', {'assertion':'positive', 
                                                                'temporality':'histroical',
                                                                'anatomy':['Pneumonia']}))
        
        
        self.anno_bin.append(self._anno((12,15), 'SSI', {'assertion':'positive', 
                                                                'temporality':'current',
                                                                'anatomy':['superficial']}))
                                                                
        self.anno_bin.append(self._anno((21,31), 'SSI', {'assertion':'Negative', 
                                                                'temporality':'current',
                                                                'anatomy':['feet']}))
                                                                
        self.anno_bin.append(self._anno((39,52), 'UTI', {'assertion':'positive', 
                                                         'temporality':'histroical',
                                                          'anatomy':['UTI']}))
                                                                
                                                                
        self.anno_bin.append(self._anno((48,62), 'UTI', {'assertion':'negative', 
                                                                'temporality':'current',
                                                                'anatomy':['Pneumonia']}))
                                                                
                                                                                                

    
    def test_cal_diff_score(self):
        
        
        annos = self.anno_bin
        mydoc = ClinicalTextDocument()
        otherdoc = ClinicalTextDocument()
        
        mydoc.annotations = self.anno_bin[0:5] #set1
        otherdoc.annotations = self.anno_bin[0:5] #set1
        
        score = mydoc.cal_diff_score(otherdoc)
        
        self.assertEqual(mydoc.cal_diff_score(otherdoc),1)
        self.assertEqual(otherdoc.cal_diff_score(mydoc),1)
        
        mydoc.annotations = self.anno_bin[0:5] #set1
        otherdoc.annotations = self.anno_bin[5:10] #set2
        
        self.assertEqual(mydoc.cal_diff_score(otherdoc),1)
        self.assertEqual(otherdoc.cal_diff_score(mydoc),1)
        
        
        mydoc.annotations = self.anno_bin[5:10] #set2
        otherdoc.annotations = self.anno_bin[15:20] #set3
        
        self.assertEqual(mydoc.cal_diff_score(otherdoc),0)
        self.assertEqual(otherdoc.cal_diff_score(mydoc),0)
        
        
        mydoc.annotations = self.anno_bin[5:10] #set2
        otherdoc.annotations = self.anno_bin[7:12] #set3
        
        self.assertEqual(mydoc.cal_diff_score(otherdoc),0.60)
        self.assertEqual(otherdoc.cal_diff_score(mydoc),0.60)
        
        
        mydoc.annotations = self.anno_bin[5:10] #set2
        otherdoc.annotations = self.anno_bin[0:20] #set3
        
        self.assertEqual(mydoc.cal_diff_score(otherdoc),0.80)
        self.assertEqual(otherdoc.cal_diff_score(mydoc),0.80)
        
        
        pass
        


        
        
        
    # def test_xxperiment(self):
     
       
    #     pass
        
        
if __name__ == '__main__':
    suit = unittest.TestLoader().loadTestsFromTestCase(test_Annotation)
    unittest.TextTestRunner(verbosity=2).run(suit)
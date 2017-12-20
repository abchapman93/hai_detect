"""
This module contains helper functions
for text processing
"""
import sys
import re

def preprocess_human(text):
    """
    Adds new lines before all headers
    in order to make the text more readable
    """
    header_patterns = [r'Review of Systems:',  r'Physical Exam(ination)?:', r'(Patient )?(Active )?Problem List',
                       r'Risks and benefits:', r'Time out:', r'Chief Complaint:', r'Marital Status:', 'Attending Physician:',
                       'Events of last 24 hours:', 'Current Medications:', 'Years of Education:', 'Current Unit:',
                       'Cardio Rate:', 'Plan:', 'Assessment and Plan:', 'Patient Instructions:', 'Patient Education:',

                       ]
    default_header = r'([\s]{2,}([a-z ]*){1,2}:)' #  Simple default header pattern that will grab words followed by colons
    header_patterns.append(default_header)
    #header = re.compile(default_header, flags=re.IGNORECASE)
    header = re.compile('({})'.format('|'.join(header_patterns)), flags=re.IGNORECASE)
    # Put a period and two lines before every header
    text = header.sub(r'.\n\n\1', text)
    list_element = re.compile(r'-[a-z\s]*\?:\s+(yes|no|unsure)', flags=re.IGNORECASE)
    # Put a period and a new line before every list element
    text = list_element.sub(r'.\n\1', text)
    return text


def find_headers_and_lists(text):
    """
    Finds headers and lists in the text and returns starting points for each of them.
    This allows us to properly split sentences before headers and bullet-point lists.
    """
    header_and_list_points = []
    header = re.compile(r'[\s]{2,}([a-z ]*){1,2}:', flags=re.IGNORECASE)
    header_points = list(header.finditer(text))
    header_and_list_points.extend(header_points)
    list_elements = re.compile(r'-[a-z\s]*\?:\s+(yes|no)', flags=re.IGNORECASE)
    list_points = list(list_elements.finditer(text))
    header_and_list_points.extend(list_points)
    return header_and_list_points




if __name__ == '__main__':
    infile = sys.argv[1]
    string = open(infile).read()
    #print(find_headers_and_lists(string))
    string = "Review of Systems: this. Chief complaint: that. Problem List: -Pneumonia. Physical Exam: okay. Physical Examination: that, that."
    print(string)
    preprocessed = preprocess_human(string)
    print('Preprocessed:')
    print(preprocessed)
    exit()
    string = "  Impression: We examined the patient yesterday. He shows signs of pneumonia.\
    The wound is CDI. He has not developed a urinary tract infection\
    However, there is a wound infection near the abdomen. There is no surgical site infection. There is an abscess  Surgical Sites: There is a surgical site infection. Signed, Dr.Doctor MD."

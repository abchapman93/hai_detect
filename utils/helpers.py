"""
This module contains helper functions
for text processing
"""
import re

def preprocess_human(text):
    """
    Adds new lines before all headers
    in order to make the text more readable
    """

    header = re.compile(r'(\b[A-Za-z]*:\s*\b)')
    text = header.sub(r'\n\1', text)
    return text


def find_headers(text):
    """
    Finds headers in the text and returns starting points for each of them.
    This allows us to properly split sentences before headers.
    """

    header = re.compile(r'[\s]{2,}([a-z ]*){1,2}:')
    header_points = list(header.finditer(text))
    return [m for m in header_points]




if __name__ == '__main__':
    string = "  Impression: We examined the patient yesterday. He shows signs of pneumonia.\
    The wound is CDI. He has not developed a urinary tract infection\
    However, there is a wound infection near the abdomen. There is no surgical site infection. There is an abscess  Surgical Sites: There is a surgical site infection. Signed, Dr.Doctor MD."
    print(find_header_points(string.lower()))
    print(string[257:270])

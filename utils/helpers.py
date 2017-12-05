"""
This module contains helper functions
for text processing
"""
import re

def preprocess(text):
    """
    Adds new lines before all headers
    in order to make the text more readable
    """

    header = re.compile(r'(\b[A-Za-z]*:\s*\b)')
    text = header.sub(r'\n\1', text)
    return text

if __name__ == '__main__':
    string = "IMPRESSION: This is my impression. FINDINGS:         This is what I will tell you."
    print(preprocess(string))

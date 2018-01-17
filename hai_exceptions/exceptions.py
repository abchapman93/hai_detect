#define custom exceptions for hai_detect

class HAIError (Exception):
    '''Base Class'''
    pass

class MalformedeHostExcelRow(HAIError):
    "Raised when parsing eHost Annotation excel file. If the row is not enough arguments, etc"
    pass

class MalformedSpanValue(HAIError):
    "Raised used when the system trying to pase the span but the span is not in tuple format"
    pass
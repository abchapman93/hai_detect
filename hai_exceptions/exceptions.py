#define custom exceptions for hai_detect

class HAIError (Exception):
    '''Base Class'''
    pass

class MalformedeHostExcelRow(HAIError):
    "Raised when parsing eHost Annotation excel file. If the row is not enough arguments, etc"
    pass

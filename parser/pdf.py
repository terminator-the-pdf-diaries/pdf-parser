from PDFparser import *

class PDF:
    # PDF object
    def __init__(self, json):
        '''
        column: table headers
        pg_head: beginning of page that contains specific table
        pg_end: end of page that contains specific table
        table_head: beginning of table to be parsed - inclusive
        table_end: end of table to be parsed - inclusive

        keywords: keywords identify required table fields for calculation
        page_pattern: a pattern that identifies the page needed
        table_pattern: a pattern that identifies the table
        '''

        self.pg_head = json['format']['Begin_of_Page_Text']
        self.pg_end = json['format']['End_of_Page_Text']
        self.table_head = json['format']['Begin_of_Table_Text']
        self.table_end = json['format']['End_of_Table_Text']

        '''
        this process to be done in api
        '''
        raw_keywords = json['keyword_match']

        # build keyword dictionary
        keywords = {}
        for key, val in raw_keywords.items():
            key = self.strip(key)
            keywords[key] = val

        self.keywords = keywords

        # build column header
        raw_column = json['headers']
        column = [PDF.strip(c) for c in raw_column]

        self.column = column

        self.page_pattern = PDFparser().gen_regex(self.pg_head, self.pg_end, False)
        print('PAGE PATTERN: ', self.page_pattern)
        
        self.table_pattern = PDFparser().gen_regex(self.table_head, self.table_end, True)
        print('TABLE PATTERN: ', self.table_pattern)
        print()

    @staticmethod
    def strip(string):
        '''
        removes special characters, white space, and capitalization for matching
        '''

        string = (''.join(e for e in string if e.isalnum())).lower()
        return string

if __name__ == "__main__":
    pass
else:
    print("pdf.py is being imported into another module")
    print()

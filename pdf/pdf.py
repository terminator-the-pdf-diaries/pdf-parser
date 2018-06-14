from PDFparser import *


class PDF:
    # PDF object
    def __init__(self):
        '''
        column: table headers
        pg_head: beginning of page that contains specific table
        pg_end: end of page that contains specific table
        table_head: beginning of table to be parsed - inclusive
        table_end: end of table to be parsed - inclusive

        keywords: keywords identify required table fields for calculation
        filter: filters extraneous columns from analysis
        page_pattern: a pattern that identifies the page needed
        content_pattern: a pattern that identifies the table

        transpose: flag for transposing table
        '''
        self.column = None
        self.pg_head = None
        self.pg_end = None
        self.table_head = None
        self.table_end = None

        self.keywords = None  # keywords filtered for calculations
        self.filter = None

        self.page_pattern = None
        self.content_pattern = None

        self.transpose = False

    def strip_json(self, json):
        '''
        strips json of special characters for keyword matching
        '''

        temp = {}
        for key, val in json.items():
            key = ''.join(e for e in key if e.isalnum())
            temp[key] = val
        return temp

    def set_properties(self, json):
        '''
        sets pdf properties with provided DB fields
        '''

        self.pg_head = json['format']['Begin_of_Page_Text']
        self.pg_end = json['format']['End_of_Page_Text']
        self.table_head = json['format']['Begin_of_Table_Text']
        self.table_end = json['format']['End_of_Table_Text']
        self.transpose = json['format']['Transpose']
        self.column = json['headers']
        self.keywords = self.strip_json(json['keyword_match'])
        self.filter = json['excluded_headers']

        self.page_pattern = PDFparser().gen_regex(self.pg_head, self.pg_end, False)
        self.content_pattern = PDFparser().gen_regex(
            self.table_head, self.table_end, True)


if __name__ == "__main__":
    pass
else:
    print("pdf.py is being imported into another module")

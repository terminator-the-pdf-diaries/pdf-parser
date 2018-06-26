# =========================================
#
# Parses PDF and builds dataframe to be passed
# off for calculation
#
# =========================================

from tika import parser
import re
import pandas as pd
import sys


class PDFparser:

    def __init__(self):
        pass

    def gen_regex(self, head, end, is_content):
        ''' generates regex pattern
            is_content: flags for content pattern
        '''

        s = ''
        if (is_content):
            # grabs the first matching table
            s = '({}).*?({})'
        else:
            # grabs the matching pages
            s = '({}).*({})'
        #print(s.format(head, end))
        return s.format(head, end)

    def parse(self, string):
        '''
        Tika library to parse PDF
        '''

        parsedPDF = parser.from_buffer(string)

        # Extract the text content from the parsed PDF
        pdf = parsedPDF["content"]
        # check - to be implemented
        # dump parse to file, output dump to new terminal
        #print('PARSE DUMP')
        # print()
        # print(pdf)

        # Convert double newlines into single newlines
        pdf = pdf.replace('\n\n', '\n').replace(
            'Gain/(Loss)', 'GainLoss').replace('46_1274', '')  # .replace('/', '')
        return pdf

    @staticmethod
    def is_numeric(string):
        '''
        checks if string contains a digit 
        '''
        if (re.search(r'\d', string) is not None):
            try:
                float(string)
                return True
            except ValueError:
                return False
        else:
            return False

    def create_df(self, pdf_content, page_pattern, table_pattern, column_headings, line_pattern=r'([a-z, ]+)([%,$,\(,\), \., 0-9 -]+)'):
        '''Create a Pandas DataFrame from lines of text in a PDF.

        Arguments:
        pdf_content -- all of the text Tika parses from the PDF
        page_pattern -- a pattern that identifies the page needed
        table_pattern -- a pattern that identifies the table
        line_pattern -- a pattern that separates the category name or values
        column_headings -- the list of column headings for the DataFrame
        '''

        #line_pattern = '([a-z, ]+)([%,$,\(,\), \., 0-9 -]+)'

        list_of_line_items = []
        # Filter the page to get year to date
        page_match = re.search(page_pattern, pdf_content, re.DOTALL)

        # if pattern input locates a match
        if (page_match):
            print('PAGE MATCH: ', page_match)
            print()

            # group 0 - inclusive
            content_match = re.search(
                table_pattern, page_match.group(0), re.DOTALL)

            if (content_match):
                print('CONTENT MATCH: ', content_match)
                print()

                content_match = content_match.group(0)

                print('TABLE MATCH GROUP 0')
                print(content_match)
                print()

                # Split on newlines to create a sequence of strings
                content_match = content_match.split('\n')

                for item in content_match:
                    line_items = []
                    # Use line_pattern to separate the category and values to group 1 and group 2
                    line_match = re.search(line_pattern, item, re.I)

                    # only if it matches pattern
                    if not (line_match is None):
                        # Grab the agency name or revenue source, strip whitespace, and remove commas, special characters, lowercased
                        category = line_match.group(
                            1).strip().replace(' ', '').lower()
                        category = (
                            ''.join(e for e in category if e.isalnum()))

                        # Grab the dollar values, strip whitespace, remove $s, ), and commas, and replace ( with -
                        values_string = line_match.group(2).strip().\
                            replace('$', '').replace(',', '').replace(
                                '(', '-').replace(')', '')

                        line_items.append(category)

                        # set string value types for future dataframe calculation
                        temp = []
                        for s in values_string.split():
                            if (PDFparser.is_numeric(s)):
                                temp.append(float(s))
                            else:
                                temp.append(str(s))
                        # temp = [float(s) if PDFparser.is_numeric(
                        #     s) else str(s) for s in values_string.split()]

                        line_items.extend(temp)
                        list_of_line_items.append(line_items)

                # Convert to dataframe with headings
                df = pd.DataFrame(list_of_line_items, columns=column_headings)
                print('PARSER GENERATED PDF DATAFRAME')
                print(df)
                print()
                print()
                return df
            else:
                print('CONTENT MATCH: {} \n Unable to parse, check input'.format(
                    content_match))
                print()
                return None
        else:
            print('PAGE MATCH: {} \n Unable to parse, check input'.format(page_match))
            print()
            return None


if __name__ == "__main__":
    pass
else:
    print("pdfparser.py is being imported into another module")
    print()

from tika import parser
import re
import pandas as pd


class PDFparser:

    def __init__(self):
        pass

    def gen_regex(self, head, end, is_content):
        ''' generates regex pattern
            is_content: flags for content pattern
        '''

        s = ''
        if (is_content):
            s = '({}.*).*?({})'
        else:
            s = '({}).*?({})'
        return s.format(head, end)

    def parse(self, text_string):
        '''
        Tika library to parse PDF
        '''
        parsedPDF = parser.from_buffer(text_string)

        # Extract the text content from the parsed PDF
        pdf = parsedPDF["content"]

        # Convert double newlines into single newlines
        pdf = pdf.replace('\n\n', '\n').replace(
            'Gain/(Loss)', 'GainLoss').replace('46_1274', '')  # .replace('/', '')
        return pdf

    def create_df(self, pdf_content, page_pattern, content_pattern, column_headings, line_pattern=r'([a-z, ]+)([%,$,\(,\), \., 0-9 -]+)'):
        """Create a Pandas DataFrame from lines of text in a PDF.

        Arguments:
        pdf_content -- all of the text Tika parses from the PDF
        page_pattern -- a pattern that identifies the page needed
        content_pattern -- a pattern that identifies the table
        line_pattern -- a pattern that separates the category name or values
        column_headings -- the list of column headings for the DataFrame
        """

        #line_pattern = '([a-z, ]+)([%,$,\(,\), \., 0-9 -]+)'

        list_of_line_items = []
        # Filter the page to get year to date
        page_match = re.search(page_pattern, pdf_content, re.DOTALL)

        # group 0 - inclusive
        content_match = re.search(
            content_pattern, page_match.group(0), re.DOTALL)
        content_match = content_match.group(0)

        # Split on newlines to create a sequence of strings
        content_match = content_match.split('\n')

        for item in content_match:
            line_items = []
            # Use line_pattern to separate the category and values to group 1 and group 2
            line_match = re.search(line_pattern, item, re.I)

            # only if it matches pattern
            if not (line_match is None):
                # Grab the agency name or revenue source, strip whitespace, and remove commas
                category = line_match.group(1).strip().replace(' ', '')

                # Grab the dollar values, strip whitespace, remove $s, ), and commas, and replace ( with -
                values_string = line_match.group(2).strip().\
                    replace('$', '').replace(',', '').replace(
                        '(', '').replace(')', '')

                line_items.append(category)
                line_items.extend(values_string.split())

                list_of_line_items.append(line_items)

        # Convert to dataframe with headings
        df = pd.DataFrame(list_of_line_items, columns=column_headings)
        return df


if __name__ == "__main__":
    pass
else:
    print("pdfparser.py is being imported into another module")

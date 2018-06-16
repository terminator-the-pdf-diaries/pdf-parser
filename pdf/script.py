##=========================================
#   
# Provide input path and db_feed (json) 
# to kick off parsing and calculation
#
# process_pdf(input_path, db_feed)
#
##=========================================

from PDFparser import *
from pdf import PDF

def calc(df):
    '''
    perform calculation based off of specified calculation rules
    currently just sums

    TO BE IMPLEMENTED:
    calculation rules
    '''

    # shape filter
    # n x 1 = sum by column
    # 1 x n = sum by row

    
    # changing column to float dtype for calculation
    # types must be set in by parser - to be implemented

    cols = df.columns
    print(cols)
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
    
    print(df.shape)
    print()
    # n x 1
    if (df.shape[0] > 1 and df.shape[1] == 1):
        print('DF IS: SERIES SHAPE')
        print(df)

        # adding calculated value to df
        df.loc['calculated_result'] = df.sum()

    # 1 x n
    elif (df.shape[0] == 1 and df.shape[1] > 1):
        print('DF IS: ARRAY SHAPE')
        print(df)

        df['calculated_result'] = df[df.columns].sum(axis=1)

        # transposing
        df = df.T

    print()
    print('END RESULT')
    print(df)
    return df

def prep_df(df, col_for_calc, row_for_calc):
    '''
    preps dataframe for calculation
    '''

    print('DF SHAPE BEFORE FILTER: ', df.shape)
    
    # filtering df by col
    df = df[col_for_calc]
    print('DF SHAPE AFTER FILTER: ', df.shape)
    print()

    # filtering df by row value in first column
    col_name = df.columns[0]

    print('KEEP ROWS: ', row_for_calc)
    print()
    print('ROWS BEING FILTERED')
    print()
    print(df[col_name])
    print()

    # row logical filter
    row_logical_filter = df[col_name].isin(row_for_calc)
    print('logical filter RESULT')
    print(df[col_name].isin(row_for_calc))
    print()

    # remove rows by logical filter
    df = df[row_logical_filter]

    print('PREPPED DF: ')

    # setting column[0] as index - assume first column always nonnumerical categories
    df.set_index(df.columns[0], inplace=True)
    print(df)

    return df

def rename(col, keywords, generated):
    '''
    dataframe formatting for end result to be sent to JDE
    '''

    new_col = []
    for c in col:
        print('old col name: {}'.format(c))
        if c in keywords:
            c = keywords[c]
            print('new col name: {}'.format(c))
            new_col.append(c)    
        elif c in generated:
            new_col.append(c)
    return new_col


def retrieve():
    pass

def col_check(keywords,col):
    '''
    checks and assigns row/col category to keywords
    '''

    # check for keyword in column header
    keyword_list = list(keywords.keys())
    print('KEYWORD LIST: ', keyword_list)
    print()
    print('COLUMN HEADER: ', col)
    print()

    row_keywords = [key for key in list(keywords.keys()) if key not in col]
    print('ROW KEYWORDS :', row_keywords)
    print()

    # set difference between keywords and row keywords
    # keywords not in row are classified to be column keywords
    col_keywords = list(set(keyword_list).symmetric_difference(set(row_keywords)))

    # assume first column header always contains row keyword
    col_keywords.insert(0, col[0])
    
    print('COLUMN KEYWORDS: ', col_keywords)
    print()

    return (col_keywords, row_keywords)


def process_pdf(input_path, db_feed):
    '''
    kicks off script process
    db_feed - pdf json from db
    input_path - path to pdf
    '''

    # initializing pdf object & set parameters
    pdf_object = PDF()
    pdf_object.set_properties(db_feed)
    
    # parsing pdf - input path (?)
    pdf_content = PDFparser().parse(input_path)
    
    # building dataframe
    df = PDFparser().create_df(pdf_content, pdf_object.page_pattern, pdf_object.table_pattern, pdf_object.column)
    
    print(df.dtypes)

    col_keywords, row_keywords = col_check(pdf_object.keywords, pdf_object.column)
    
    # prep df for calculation (removing columns unecessary for calculation)
    df = prep_df(df, col_keywords, row_keywords)

    calc(df)

def main():

    #input_path = "./data/Arby/40721_Arby_Bottom_2017-12-31.pdf"
    #input_path = "./data/TGIFriday/20044_TGI_Friday_Nose danger track_2017-12-31.pdf"
    
    # use 65008 for updated wingstop format
    input_path = "./data/WingStop/65008_WingStop_Half here talk_2017-12-31.pdf"

    #=================
    #      ARBY
    #=================

    arby_feed = {
      "format": {
        "Transpose": 1,
        "Begin_of_Page_Text": "For the Year",
        "Begin_of_Table_Text": "Opening Equity",
        "Company_ID": 1,
        "End_of_Page_Text": "Proprietary Confidential Business Information",
        "End_of_Table_Text": "Remaining Commitment"
      },
      "headers": ["Category","Total Fund","Investor's Allocation"],
      "excluded_headers": ["Total Fund"],
      "keyword_match": 
        {"Total Contributions": "Contributions",\
        "Total Distributions": "Distributions",\
        "Realized Gain/(Loss)": "Realized Gain/Loss",\
        "Professional Fees": "Ordinary Income",\
        "Other Expenses": "Ordinary Income",\
        "Change in Unrealized": "Unrealized MTM",\
        "Idle Funds Interest Income": "Ordinary Income",\
        "Equity Transfer": "Ordinary Income",\
        "Closing Equity": "Ending Equity Balance",\
        "Investor's Allocation": "Allocation"}
    } 
    
    #=================
    #      TGI
    #=================

    tgi_feed = {
    "excluded_headers": [],
    "format": {
        "Transpose": 1,
        "Begin_of_Page_Text": "Inception to Date",
        "Begin_of_Table_Text": "Total",
        "Company_ID": 2,
        "End_of_Page_Text": "Page",
        "End_of_Table_Text": "Page"
    },
    "headers": ['Commitment Percentage',\
    'Commitment Amount',\
    'Beginning Balance',\
    'Contributions',\
    'Distributions',\
    'Realized Gains (Losses), Net',\
    'Unrealized Gains (Losses), Net',\
    'Management Fee, Net',\
    'Other Income',\
    'Other Expense',\
    'Transfers',\
    'Asset Transfer',\
    'Ending Balance'],
    "keyword_match": {
        "Contributions": "Contributions", "Distributions": "Ordinary Income",\
        "Realized Gains/(Losses), Net,": "Unrealized MTM", "Unrealized Gains/(Losses), Net": "Professional Fees",\
        "Other Expense": "Distributions", " Ending Balance": "Ending Equity Balance", "total": "Total"
        }
        #{"Total Contributions": "Contributions", "Total Distributions": "Ordinary Income",\
        #"Realized Gain/(Loss)": "Unrealized MTM", "Professional Fees": "Realized Gain/Loss",\
        #"Other Expenses": "Distributions", "Change in Unrealized": "Ending Equity Balance"
        #}
    }

    #=================
    #    WINGSTOP
    #=================

    wingstop_feed = {
    "format": {
        "Company_ID": 2,
        "Begin_of_Page_Text": "Statement of Partners' Capital",
        #"Begin_of_Page_Text": "The Northwestern Mutual Life I",
        "End_of_Page_Text": "CONFIDENTIAL & PROPRIETARY",
        "End_of_Table_Text": "CONFIDENTIAL & PROPRIETARY",
        "Begin_of_Table_Text": "The Northwestern Mutual Life I",
        "Transpose": 0
    },
    "headers": [
        "Company Name",
        "Capital Contribution percentage",
        "Partner's capital commitments",
        #"Funded capital commitments",
        "Recall provision receivable",
        "Cumulative distributions",
        "Cumulative gain allocations",
        # check capitalization: Net gain before Investment gain
        "Net gain before investment gain",
        "Net gain on investments unrealized",
        "Net gain on investments realized",
        "Distributions",
        "Total partners' capital"
    ],
    "excluded_headers": [],
    "keyword_match": {
        #"Contributions": "Contributions",
        "Net gain before investment gain": "Ordinary Income",
        "Net gain on investments unrealized": "Unrealized MTM",
        "Net gain on investments realized": "Realized Gain/Loss",
        "Distributions": "Distributions",
        "Total partners' capital": "Ending Equity Balance",
        "The Northwestern Mutual Life Insurance Company": "The Northwestern Mutual Life Insurance Company",
    }
}
    # pass pdf off to parse & perform calculations
    process_pdf(input_path, wingstop_feed)

if __name__ == "__main__":
    main()
else:
    print("script.py is being imported into another module")
    print()
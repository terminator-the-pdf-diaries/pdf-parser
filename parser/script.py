# =========================================
#
# Provide input path and db_feed (json)
# to kick off parsing and calculation
#
# process_pdf(string, db_feed)
#
# =========================================

#import PDFparser

from PDFparser import *
from pdf import PDF


def calc(df):
    '''
    perform calculation based off of specified calculation rules
    currently just sums all rows

    TO BE IMPLEMENTED:
    calculation rules
    '''

    # shape filter
    # n x 1 = sum by column
    # 1 x n = sum by row

    print(df.shape)

    # n x 1
    if (df.shape[0] > 1 and df.shape[1] == 1):
        print('DF IS: SERIES SHAPE')

    # 1 x n
    elif (df.shape[0] == 1 and df.shape[1] > 1):
        print('DF IS: ARRAY SHAPE')
        print('DF BEFORE TRANSPOSE\n')
        print(df)

        # transposing
        df = df.T

    print()
    print('DF FOR CALCULATION:')
    print(df) 
    print()   
    
    # calculation by buckets
    df['IA_Classification'] = df.index
    df.index = pd.RangeIndex(len(df.index))  
    df = df.groupby('IA_Classification').sum()

    # reseting index
    df['IA_Classification'] = df.index
    df.index = pd.RangeIndex(len(df.index))  

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


def col_check(keywords, col):
    '''
    checks and assigns row/col category to keywords
    '''

    # check for keyword in column header
    keyword_list = list(keywords.keys())
    print('KEYWORD LIST: ', keyword_list)
    print()
    print('COLUMN HEADER: ', col)
    print()

    row_keywords = [key for key in keyword_list if key not in col]
    print('ROW KEYWORDS :', row_keywords)
    print()

    # set difference between keywords and row keywords
    # keywords not in row are classified to be column keywords
    col_keywords = list(
        set(keyword_list).symmetric_difference(set(row_keywords)))

    # assume first column header always contains row keyword
    col_keywords.insert(0, col[0])

    print('COLUMN KEYWORDS: ', col_keywords)
    print()

    return (col_keywords, row_keywords)


def rename(strings, keywords):
    '''
    dataframe formatting for end result to be sent to JDE
    renames strings to keyword values in PDF properties
    '''

    new_strings = []
    for c in strings:
        print('old col name: {}'.format(c))
        if c in keywords:
            c = keywords[c]
            print('new col name: {}'.format(c))
            print()
            new_strings.append(c)
        else:
            new_strings.append(c)
    return new_strings


def send(df):
    '''
    send to DB in JSON format
    '''
    print('result from YAO', df.to_dict('records'))
    return df.to_dict('records')


def process_df(pdf_object, df):
    print(df.dtypes)
    print()

    col_keywords, row_keywords = col_check(
        pdf_object.keywords, pdf_object.column)

    # prep df for calculation (removing columns unecessary for calculation)
    df = prep_df(df, col_keywords, row_keywords)
    # df = calc(df)

    print('DF INDEX: ', df.index)
    print('DF COLUMNS: ', df.columns)
    print()

    # renaming to match IA classification before sending to DB
    df.index = rename(df.index, pdf_object.keywords)
    df.columns = rename(df.columns, pdf_object.keywords)
    df = calc(df)

    print('END RESULT')
    print(df)
    return send(df)


def process_pdf(input_path, db_feed):
    '''
    kicks off pdf processing
    db_feed - pdf json from db
    input_path - path to pdf
    '''

    # initializing pdf object & set parameters
    pdf_object = PDF(db_feed)

    # parsing pdf - input path (?)
    pdf_content = PDFparser().parse(input_path)

    # building dataframe
    df = PDFparser().create_df(pdf_content, pdf_object.page_pattern,
                               pdf_object.table_pattern, pdf_object.column)

    # continue df transformation & filtering only if parsing success
    if (df is not None):
        return process_df(pdf_object, df)
    else:
        print('no dataframe passed')


def main():

    #input_path = "./data/Arby/46286_Arby_Fed_2017-12-31.pdf"
    #input_path = "./data/TGIFriday/20044_TGI_Friday_Nose danger track_2017-12-31.pdf"

    # use 65008 for updated wingstop format
    input_path = "./data/WingStop/65008_WingStop_Half here talk_2017-12-31.pdf"

    #=================
    #      ARBY
    #=================

    arby_feed = {
        "format": {
            "Company_ID": 1,
            "Begin_of_Page_Text": "For the Year",
            "End_of_Page_Text": "Proprietary Confidential Business Information",
            "End_of_Table_Text": "Remaining Commitment",
            "Begin_of_Table_Text": "Opening Equity"
        },
        "headers": [
            "Category",
            "Total Fund",
            "Investor's Allocation"
        ],
        "keyword_match": {
            "Total Contributions": "Contributions",
            "Total Distributions": "Distributions",
            "Realized Gain/(Loss)": "Realized Gain/Loss",
            "Professional Fees": "Ordinary Income",
            "Other Expenses": "Ordinary Income",
            "Change in Unrealized": "Unrealized MTM",
            "Idle Funds Interest Income": "Ordinary Income",
            "Equity Transfer": "Ordinary Income",
            "Closing Equity": "Ending Equity Balance",
            "Investor's Allocation": "Amount"
        }
    }

    #=================
    #      TGI
    #=================

    tgi_feed = {
        "format": {
            "Company_ID": 3,
            "Begin_of_Page_Text": "Inception to Date",
            "End_of_Page_Text": "Page",
            "End_of_Table_Text": "Page",
            "Begin_of_Table_Text": "Total"
        },
        "headers": [
            "Commitment Percentage",
            "Commitment Amount",
            "Beginning Balance",
            "Contributions",
            "Distributions",
            "Realized Gains (Losses), Net",
            "Unrealized Gains (Losses), Net",
            "Management Fee, Net",
            "Other Income",
            "Other Expense",
            "Transfers",
            "Asset Transfer",
            "Ending Balance"
        ],
        "keyword_match": {
            "Contributions": "Contributions",
            "Distributions": "Distributions",
            "Realized Gains (Losses), Net": "Realized Gain/Loss",
            "Unrealized Gains (Losses), Net": "Unrealized MTM",
            "Management Fee, Net": "Ordinary Income",
            "Other Income": "Ordinary Income",
            "Other Expense": "Ordinary Income",
            "total": "Amount",
            "Ending Balance": "Ending Equity Balance"
        }
    }

    #=================
    #    WINGSTOP
    #=================

    wingstop_feed = {
        "format": {
            "Company_ID": 2,
            "Begin_of_Page_Text": "Statement of Partners' Capital",
            "End_of_Page_Text": "CONFIDENTIAL & PROPRIETARY",
            "End_of_Table_Text": "CONFIDENTIAL & PROPRIETARY",
            "Begin_of_Table_Text": "The Northwestern Mutual Life I"
        },
        "headers": [
            "Company Name",
            "Capital Contribution percentage",
            "Partner's capital commitments",
            "Recall provision receivable",
            "Cumulative distributions",
            "Cumulative gain allocations",
            "Net gain before Investment gain",
            "Net gain on investments unrealized",
            "Net gain on investments realized",
            "Distributions",
            "Total partners' capital"
        ],
        "keyword_match": {
            "Net gain before investment gain": "Ordinary Income",
            "Net gain on investments unrealized": "Unrealized MTM",
            "Net gain on investments realized": "Realized Gain/Loss",
            "Distributions": "Distributions",
            "Total partners' capital": "Ending Equity Balance",
            "The Northwestern Mutual Life Insurance Company": "Amount"
        }
    }

    # pass pdf off to parse & perform calculations
    process_pdf(input_path, wingstop_feed)


if __name__ == "__main__":
    main()
else:
    print("script.py is being imported into another module")
    print()

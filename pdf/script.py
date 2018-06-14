# import csv
# import glob
# import os
# import sys
from PDFparser import *
from pdf import PDF

# perform dataframe calculation, return json 
def calc(df):
    # shape filter
    # n x 1 = sum by column
    # 1 x n = sum by row

    # df.shape = row x col

    print(df.shape)
    # n x 1
    if (df.shape[0] > 1 and df.shape[1] == 1):
        print('SERIES')
        #df.set_index(df.columns[0], inplace=True)

        # grab the first non categorical column name 
        calc_col_name = df.columns[0]
        print(calc_col_name)

        print(df[calc_col_name])

        # changing column to float dtype
        df[calc_col_name] = df[calc_col_name].astype(float)
        print(df)

        df.loc['OrdinaryIncome'] = df.sum()

        # adding calculated value to df
        #df.loc[-1] = ['OrdinaryIncome', 000]

    # 1 x n
    elif (df.shape[0] == 1 and df.shape[1] > 1):
        print('ARRAY')
        
        #df['sum'] = df[df.columns].sum(axis=1)

        # adding calculated value to df
        #df['OrdinaryIncome'] = # sum
    
    #pass

def prep_df(df, col_for_calc, row_for_calc):
    print('COL FOR CALC')
    print(col_for_calc)
    print('ROW FOR CALC')
    print(row_for_calc)
    print(df)
    
    # filtering df by col
    df = df[col_for_calc]

    # filtering df by row value in first column
    col_name = df.columns[0]
    print('INCLUDED ROWS: ', row_for_calc)
    print('ROWS BEING FILTERS :', df[col_name])

    # row logical filter
    print(df[col_name].isin(row_for_calc))

    df = df[df[col_name].isin(row_for_calc)]

    # filter df by index value based off of necessary rows for calc
    df.drop(df.index[row_for_calc])
    print(df)

    print('INDEX')
    print(df.index)

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

def col_check(keywords,column):
    # strip column head of special characters for keyword matching
    new_col = []
    
    for col in column:
        col = ''.join(e for e in col if e.isalnum())
        new_col.append(col)

    print('OLD COLUMN')
    print(column)
    print()
    print('NEW COLUMN')
    print(new_col)
    print()
    print('KEYWORDS')
    print(keywords)
    print()

    keep_col = []
    # assume first column header always contain row keywords 
    keep_col.append(new_col[0])
    keep_row = []
    
    # check for keyword in column header
    keyword_list = list(keywords.keys())
    print(keyword_list)

    for key in keyword_list:
        print()
        print('KEY ', key)
        if key in new_col:
            print('KEEP IN COLUMN')
            keep_col.append(key)
        else: 
            keep_row.append(key)
            print('KEEP IN ROW')

    print('KEEP COL ', keep_col)
    print('KEEP ROW', keep_row)

    return (new_col, keep_col, keep_row)

def main():
    # get pdf (input path)
    #input_path = "../pdf-parser/data/Arby/40721_Arby_Bottom_2017-12-31.pdf"
    #input_path = "../pdf-parser/data/TGIFriday/20044_TGI_Friday_Nose danger track_2017-12-31.pdf"
    input_path = "../pdf-parser/data/WingStop/51660_WingStop_Farther as numeral_2017-12-31.pdf"

    # retrieving json 
    # arby
    '''
    get_data = {
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
    
    # tgi
    get_data = {
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
    "keyword_match": 
        {"Contributions": "Contributions", "Distributions": "Ordinary Income",\
        "Realized Gain/(Loss)": "Unrealized MTM", "Realized Gain/Loss Net": "Professional Fees",\
        "Other Expenses": "Distributions", "Change in Unrealized": "Ending Equity Balance"
        }
        #{"Total Contributions": "Contributions", "Total Distributions": "Ordinary Income",\
        #"Realized Gain/(Loss)": "Unrealized MTM", "Professional Fees": "Realized Gain/Loss",\
        #"Other Expenses": "Distributions", "Change in Unrealized": "Ending Equity Balance"
        #}
}


    tgi_column = ['Commitment Percentage','Commitment Amount','Beginning Balance','Contributions','Distributions',\
                   'Realized Gains (Losses), Net','Unrealized Gains (Losses), Net','Management Fee, Net','Other Income',\
                  'Other Expense','Transfers','Asset Transfer','Ending Balance']
    
    tgi_pg_head = 'Your Share - Inception to Date'
    tgi_pg_end = 'Page'
    tgi_tble_head = 'Total'
    tgi_tble_end = 'Page'
    tgi_keywords = ['Total Contributions','Total Distributions','Realized Gain/(Loss)','Other Expenses',\
                     'Change in Unrealized','Idle Funds Interest Income','Equity Transfer','12/31/2017 Closing Equity']
    
    # initializing pdf object
    TGI = PDF(tgi_column, tgi_pg_head, tgi_pg_end, tgi_tble_head, tgi_tble_end, tgi_keywords)

    tgi_df = PDFparser.create_df(pdf_content, TGI.page_pattern, TGI.content_pattern, TGI.column)
    print(tgi_df)
    '''
    
    # windpoint
    get_data = {
    "format": {
        "Company_ID": 2,
        "Begin_of_Page_Text": "The Northwestern Mutual Life I",
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


    # initializing pdf object & set parameters
    pdf_object = PDF()
    pdf_object.set_properties(get_data)
    
    # parsing pdf
    pdf_content = PDFparser().parse(input_path)
    
    # building dataframe
    df = PDFparser().create_df(pdf_content, pdf_object.page_pattern, pdf_object.content_pattern, pdf_object.column)

    new_col_header, col_for_calc, row_for_calc = col_check(pdf_object.keywords, pdf_object.column)

    # renaming column to stripped whitespace
    df.columns = new_col_header

    # prep df for calculation (removing columns unecessary for calculation)
    df = prep_df(df, col_for_calc, row_for_calc)
    calc(df)
    # calculating ordinary income
    #calculate(df, pdf_object.column, pdf_object.keywords, pdf_object.filter, pdf_object.transpose)


if __name__ == "__main__":
    main()
else:
    print("script.py is being imported into another module")
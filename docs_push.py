import gspread_pandas

def push_to_docs(df, email, book_name, sheet_name):
    print("Pushing to docs .... ")
    spread = gspread_pandas.Spread(email, book_name, sheet_name)
    spread_df = spread.sheet_to_df()
    spread_df = spread_df.append(df)
    spread.df_to_sheet(spread_df)
    
    #tab = workbook.fetch_tab(sheet_name)
    #tab.insert_data(df)
    return None
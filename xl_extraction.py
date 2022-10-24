import pandas as pd
import openpyxl as opxl


def df_from_named_table_in_xl(xl, table_name: str) -> pd.DataFrame:
    """
        Get named table (table_name) from the excel file (xl)
        :param xl - path to the excel file
        :param table_name - string of the named table
        :return dataframe from named table in xl
    """
    wb = opxl.open(xl)

    table = None
    # loop over sheets
    for ws in wb.worksheets:
        try:  # if table in worksheet take it and get out of the loop
            table = ws.tables[table_name]
            break
        except KeyError:
            continue

    if table:
        return pd.DataFrame([[cell.value for cell in _range] for _range in ws[table.ref][1:]],
                            columns=table.column_names)
    else:
        print(f'No table named:{table_name}\nin file:{xl}')
        return pd.DataFrame()


if __name__ == '__main__':
    xl_file = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Tour Triangle\Finision load cases\initial test data\FinitionsScriptTest.xlsx'
    df_in = df_from_named_table_in_xl(xl_file, 'LC_to_copy')
    df_out = df_from_named_table_in_xl(xl_file, 'Loads_to_paste')

    print(df_in)
    print(df_out)

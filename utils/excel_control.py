from typing import List

import pandas as pd


class ExcelControl:
    def __init__(self, excel_file) -> None:
        self.ef = pd.ExcelFile(excel_file)

    def get_sheet_names(self) -> List:
        return list(self.ef.sheet_names)

    def get_sheet_data(self, sheet_name) -> "pd.DataFrame":
        return pd.read_excel(self.ef, sheet_name=sheet_name)

    def get_rows_data(self, sheet_name) -> List:
        rows_list = []
        for row in self.get_sheet_data(sheet_name=sheet_name).iterrows():
            rows_list.append(row[1])
        return rows_list


if __name__ == '__main__':
    from config import TESTDATA_FILE

    ec = ExcelControl(TESTDATA_FILE)
    # print(ec.get_sheet_names())
    # print(ec.get_sheet_data('xiaofa'))
    # data = ec.get_sheet_data('xiaofa')
    # print(len(ec._get_rows_data(data)))
    # rows_data = ec.get_rows_data(data)
    # print(len(rows_data))

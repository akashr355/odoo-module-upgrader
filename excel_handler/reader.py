import openpyxl


def read_credentials(file_path):
    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active
    creds = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if all(row[:4]):
            creds.append(
                {"url": row[0], "db": row[1], "username": row[2], "password": row[3]}
            )
    return creds

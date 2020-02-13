import unicodedata


class TableParser(object):
    def __init__(self):
        self._csv_table_index = 0

    def get_table_content(self, table_body):
        rows = self._find_table_rows(table_body)
        app_body = []
        for row in rows:
            if row.get_attribute('style'):
                continue
            row_cells = self._find_row_cells(row)
            app_row = []
            for cell in row_cells:
                if self._is_cell_to_skip(cell):
                    continue
                cell_value = self._get_cell_value(cell)
                app_row.append(cell_value)
                colspan = cell.get_attribute('colspan')
                if colspan:
                    for x in range(int(colspan) - 1):
                        app_row.append(' ')
            app_body.append(app_row)
        return app_body

    @staticmethod
    def _get_cell_value(cell):
        cell_value = cell.get_attribute("innerText").strip()
        cell_value = str(unicodedata.normalize("NFKD", cell_value))

        return cell_value

    @staticmethod
    def _is_cell_to_skip(cell):
        if cell.get_attribute("class") in [
            # "dx-datagrid-group-space dx-command-expand",
            # "dx-command-expand dx-datagrid-group-space",
            # "dx-datagrid-group-space dx-command-expand dx-cell-focus-disabled"
        ]:
            return True
        return False

    @staticmethod
    def _find_row_cells(row):
        row_cells = row.find_elements_by_tag_name('td')
        return row_cells

    @staticmethod
    def _find_table_rows(table):
        rows = table.find_elements_by_xpath("./tbody/tr")
        return rows

    def add_cells_to_html_report(self, app_content, baseline_content, html_report, header=False):
        success = True
        for row_index, row in enumerate(baseline_content):
            html_report.add_row()
            for cell_index, value in enumerate(row):
                try:
                    app_value = app_content[row_index][cell_index]
                    if value == app_value:
                        html_report.add_pass_cell(value, app_value, header)
                    else:
                        success = False
                        html_report.add_fail_cell(value, app_value, header)
                except IndexError:
                    html_report.add_fail_cell(value, "NO DATA", header)
                    success = False
        return success

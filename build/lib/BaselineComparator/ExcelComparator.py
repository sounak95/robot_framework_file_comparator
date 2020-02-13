import datetime
import os
import xlrd
from Libraries.Common.BaselineComparator.json_comparator import number_truncate

class MxBook:

    def __init__(self, filename):

        self.path, self.name = os.path.split(filename)
        self.book = xlrd.open_workbook(filename)
        self.check_sheet = 0

    def get_sheet(self, sheet_index=None):

        return self.book.sheet_by_index(sheet_index if sheet_index else self.check_sheet)

    def has_sheet(self, sheet_name):

        try:
            self.check_sheet = self.book.sheet_names().index(sheet_name)
        except ValueError:
            return False

        return True


class ExcelComparator:

    def __init__(self, app_file, baseline_file):
        self.app_book = self._open_book(app_file, "app_file")
        self.baseline_book = self._open_book(baseline_file, "baseline_file")
        self.report = None

    @staticmethod
    def _open_book(filename, param_name):

        try:
            book = MxBook(filename)
        except IOError:
            raise AssertionError("ERROR: [%s] No such file or directory: '%s'" % (param_name, filename))
        
        return book

    @staticmethod
    def _get_check_sheet(book):

        try:
            sheet = book.get_sheet()
        except IndexError:
            # TODO
            raise AssertionError("ERROR: [%s] Failed to load desired sheet from ..." % ("TODO!",))

        return sheet

    def check_sheets(self, sheet_name):

        if sheet_name != "":
            if not self.app_book.has_sheet(sheet_name):
                raise AssertionError("ERROR: No sheet named '%s' found in app file '%s'" %
                                     (sheet_name, self.app_book.name))

            if not self.baseline_book.has_sheet(sheet_name):
                raise AssertionError("ERROR: No sheet named '%s' found in app file '%s'" %
                                     (sheet_name, self.baseline_book.name))

    def compare(self, report, nb_of_digit_after_decimal):

        self.report = report
        success = True

        ex_data = self._get_check_sheet(self.baseline_book)
        re_data = self._get_check_sheet(self.app_book)

        row_index = 0
        while row_index < ex_data.nrows and row_index < re_data.nrows:

            ex_row = ex_data.row(row_index)
            re_row = re_data.row(row_index)

            if row_index == 0:
                self._manage_status_header(len(ex_row), len(re_row))

            if not self._manage_matched_row(ex_row, re_row, row_index, nb_of_digit_after_decimal):
                success = False

            row_index += 1

        # Missing rows
        while row_index < ex_data.nrows:
            success = False
            self._manage_missing_row(ex_data.row(row_index), row_index, error_type="missing")
            row_index += 1

        # Additional rows
        while row_index < re_data.nrows:
            success = False
            self._manage_missing_row(re_data.row(row_index), row_index, error_type="additional")
            row_index += 1

        return success

    def _manage_status_header(self, ex_length, re_length):

        self.report.add_row()
        self.report.add_info_cell("")

        cell_index = 0
        while cell_index < ex_length and cell_index < re_length:
            self.report.add_info_cell("Matching col", "%s" % (xlrd.colname(cell_index),))
            cell_index += 1

        # Missing columns
        while cell_index < ex_length:
            self.report.add_info_cell("Missing col", "%s" % (xlrd.colname(cell_index),))
            cell_index += 1

        # Additional columns
        while cell_index < ex_length:
            self.report.add_infor_cell("Additional col", "%s" % (xlrd.colname(cell_index),))
            cell_index += 1

    def _manage_matched_row(self, ex_row, re_row, row_index, nb_of_digit_after_decimal):

        self.report.add_info_row("Matching row", "%d" % (row_index + 1,))

        success = True

        cell_index = 0
        while cell_index < len(ex_row) and cell_index < len(re_row):

            # For future reference:
            # Cell Class object attributes (based on xlrd documentation):
            #  - ctype (int)
            #  - value (depends on ctype)
            #  - xf_index - None if workbook is opened with "formatting_info" disabled
            # XL_CELL_EMPTY (0)     - empty string u''
            # XL_CELL_TEXT (1)      - a Unicode string
            # XL_CELL_NUMBER (2)    - float
            # XL_CELL_DATE (3)      - float
            # XL_CELL_BOOLEAN (4)   - int; 1 means TRUE, 0 means FALSE
            # XL_CELL_ERROR (5)     - int representing internal Excel codes
            # XL_CELL_BLANK (6)     - empty string u'' (only when open_workbook(..., formatting_info=True) is used)

            if ex_row[cell_index].ctype == xlrd.XL_CELL_DATE:

                ex_value, ex_value_as_datetime = self._get_value_as_datetime(ex_row[cell_index])
                re_value, re_value_as_datetime = self._get_value_as_datetime(ex_row[cell_index])

                if ex_value == re_value:
                    self.report.add_pass_cell(re_value_as_datetime, ex_value_as_datetime)
                else:
                    self.report.add_fail_cell(re_value_as_datetime, ex_value_as_datetime)
                    success = False

            elif (ex_row[cell_index].ctype == xlrd.XL_CELL_NUMBER) and nb_of_digit_after_decimal :
                ex_value = self._get_value_as_float(ex_row[cell_index], nb_of_digit_after_decimal)
                re_value = self._get_value_as_float(re_row[cell_index], nb_of_digit_after_decimal)

                if ex_value == re_value:
                    self.report.add_pass_cell(re_value, ex_value)
                else:
                    self.report.add_fail_cell(re_value, ex_value)
                    success = False

            else:
                ex_value = self._get_value_as_str(ex_row[cell_index])
                re_value = self._get_value_as_str(re_row[cell_index])

                if ex_value == re_value:
                    self.report.add_pass_cell(re_value, ex_value)
                else:
                    self.report.add_fail_cell(re_value, ex_value)
                    success = False

            cell_index += 1

        # Missing columns
        while cell_index < len(ex_row):
            ex_value = ex_row[cell_index].value
            # TODO:
            self.report.add_warn_cell("NO DATA", ex_value)
            success = False

            cell_index += 1

        # Additional column
        while cell_index < len(re_row):
            re_value = re_row[cell_index].value
            # TODO:
            self.report.add_warn_cell(re_value, "NO DATA")
            success = False

            cell_index += 1

        return success

    def _manage_missing_row(self, row_data, row_index, error_type="missing"):

        self.report.add_info_row("%s row" % (error_type.title()), "(%d)" % (row_index,))

        cell_index = 0
        while cell_index < len(row_data):
            cell_value = row_data[cell_index].value
            if error_type == "missing":
                self.report.add_warn_cell("NO DATA", "%s" % str(cell_value))
            elif error_type == "additional":
                self.report.add_warn_cell("%s" % str(cell_value), "NO DATA")
            else:
                self.report.add_warn_cell("UNKNOWN ERROR", "TYPE")

            cell_index += 1

    @staticmethod
    def _get_value_as_str(cell):

        try:
            value = str(cell.value)
        except UnicodeEncodeError:
            value = "UNICODE_ERROR"

        return value

    @staticmethod
    def _get_value_as_float(cell, nb_of_digit_after_decimal):

        try:
            if nb_of_digit_after_decimal > 0:
                value = number_truncate(repr(cell.value),nb_of_digit_after_decimal )
            elif nb_of_digit_after_decimal == 0:
                value = int(cell.value)
        except UnicodeEncodeError:
            value = "UNICODE_ERROR"
        return value

    def _get_value_as_datetime(self, cell):

        value = cell.value

        if cell.ctype == xlrd.XL_CELL_DATE:
            value_as_datetime = datetime.date(*xlrd.xldate_as_tuple(value, self.baseline_book.book.datemode)[:3])
        else:
            value_as_datetime = "DATE_ERROR"

        return value, value_as_datetime

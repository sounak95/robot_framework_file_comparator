from abc import ABCMeta, abstractmethod
from itertools import zip_longest
from Libraries.Common.BaselineComparator.table_report_generator import HTMLComparator, ComparisonErros
from Libraries.Utilities import ReportBuilder
from Libraries.Utilities.LXMLWrapper import HTMLTableBuilder


class HTMLTBodyComparatorABC(object, metaclass=ABCMeta):
    def __init__(self):
        self.success = True
        self.error_msgs = set()
        self.report_builder = ReportBuilder()

    @staticmethod
    def __get_style(td):
        return td.attrib.get('style')

    @staticmethod
    def __get_rowspan(td):
        return td.attrib.get('rowspan', "")

    @staticmethod
    def __get_colspan(td):
        return td.attrib.get('colspan', "")

    @staticmethod
    def __get_cell_value(td):
        try:
            value = td.text_content()
        except:
            value = 'No Data'
        return value

    def _compare_tbody(self, baseline, app, skip_columns_indexes=None, key_columns_indexes=None, is_header=False):
        rows = zip_longest(
            baseline.xpath('.//tr'),
            app.xpath('.//tr'),
        )
        for baseline_tr, app_tr in rows:
            row = self.report_builder.create_row()
            if baseline_tr is None:
                self.create_as_extra_line(app_tr, row)
            elif app_tr is None:
                self._create_as_missing_line(baseline_tr, row)
            else:
                cells = zip_longest(
                    baseline_tr.xpath('.//td[not(@id)]'),
                    app_tr.xpath('.//td[not(@id)]'),
                )
                if key_columns_indexes is None :
                    cells = zip_longest(
                        baseline_tr.xpath('.//td[not(@id)]'),
                        app_tr.xpath('.//td[not(@id)]'),
                    )
                    self._compare_cells(cells, row, skip_columns_indexes)
                else:
                    if self._compare_key(cells,key_columns_indexes):
                        cells = zip_longest(
                            baseline_tr.xpath('.//td[not(@id)]'),
                            app_tr.xpath('.//td[not(@id)]'),
                        )
                        self._compare_cells(cells, row, skip_columns_indexes, key_columns_indexes, is_header=is_header)
                    else:
                        self._create_as_missing_line(baseline_tr, row)
                        yield row
                        row = self.report_builder.create_row()
                        self.create_as_extra_line(app_tr, row)
            yield row

    def _compare_key(self,cells, key_columns_indexes):
        c = [cells for index, cells in enumerate(cells)]
        for k in key_columns_indexes:
            baseline_td, app_td = c[k]
            baseline_value = self.__get_cell_value(baseline_td)
            app_value = self.__get_cell_value(app_td)
            if baseline_value != app_value:
                return False
        return True

    def _compare_cells(self, cells, row, skip_columns_indexes, key_columns_indexes=[], is_header=False):
        for index, cells in enumerate(cells):
            baseline_td, app_td = cells
            baseline_value = self.__get_cell_value(baseline_td)
            app_value = self.__get_cell_value(app_td)
            if index in skip_columns_indexes:
                self._create_as_skip_cell(app_td, app_value, baseline_value, row)
            elif baseline_value == "missed_or_extra_cell":
                self._create_as_extra_cell(app_td, app_value, row)
                self.success = False
                self.error_msgs.add(ComparisonErros.extra_lines)
            elif app_value == "missed_or_extra_cell":
                self._create_as_missing_cell(baseline_td, baseline_value, row)
                self.success = False
                self.error_msgs.add(ComparisonErros.missing_lines )
            elif baseline_value == app_value:
                if index in key_columns_indexes:
                    self._create_as_key_header_cell(app_td, baseline_value, row)
                else:
                    self._create_as_pass_cell(app_td, baseline_value, row)
            else:
                cell = self._create_as_fail_cell(app_td, app_value, baseline_td, baseline_value)
                row.append(cell)
                self.success = False
                self.error_msgs.add(ComparisonErros.fail_cell)

    def _create_as_key_header_cell(self, app_td, baseline_value, row):
        cell = self.report_builder.create_key_td(baseline_value)
        HTMLTableBuilder.append_style_to_element(cell, self.__get_style(app_td))
        HTMLTableBuilder.add_attrib_to_element(cell, 'colspan', self.__get_colspan(app_td))
        HTMLTableBuilder.add_attrib_to_element(cell, 'rowspan', self.__get_rowspan(app_td))
        row.append(cell)

    def _create_as_fail_cell(self, app_td, app_value, baseline_td, baseline_value):
        cell = self.report_builder.create_fail_td(baseline_value, app_value)
        if app_td is not None:
            HTMLTableBuilder.append_style_to_element(cell, self.__get_style(app_td))
            HTMLTableBuilder.add_attrib_to_element(cell, 'colspan', self.__get_colspan(app_td))
            HTMLTableBuilder.add_attrib_to_element(cell, 'rowspan', self.__get_rowspan(app_td))
        elif baseline_td is not None:
            HTMLTableBuilder.append_style_to_element(cell, self.__get_style(baseline_td))
            HTMLTableBuilder.add_attrib_to_element(cell, 'colspan', self.__get_colspan(baseline_td))
            HTMLTableBuilder.add_attrib_to_element(cell, 'rowspan', self.__get_rowspan(baseline_td))
        return cell

    def _create_as_pass_cell(self, app_td, baseline_value, row):
        cell = self.report_builder.create_pass_td(baseline_value)
        HTMLTableBuilder.append_style_to_element(cell, self.__get_style(app_td))
        HTMLTableBuilder.add_attrib_to_element(cell, 'colspan', self.__get_colspan(app_td))
        HTMLTableBuilder.add_attrib_to_element(cell, 'rowspan', self.__get_rowspan(app_td))
        row.append(cell)

    def _create_as_skip_cell(self, app_td, app_value, baseline_value, row):
        cell = self.report_builder.create_skip_td(baseline_value, app_value)
        HTMLTableBuilder.append_style_to_element(cell, self.__get_style(app_td))
        HTMLTableBuilder.add_attrib_to_element(cell, 'colspan', self.__get_colspan(app_td))
        HTMLTableBuilder.add_attrib_to_element(cell, 'rowspan', self.__get_rowspan(app_td))
        row.append(cell)

    def _create_as_missing_cell(self, baseline_td, baseline_value, row):
        cell = self.report_builder.create_missing_td(baseline_value)
        HTMLTableBuilder.append_style_to_element(cell, self.__get_style(baseline_td))
        HTMLTableBuilder.add_attrib_to_element(cell, 'colspan', self.__get_colspan(baseline_td))
        HTMLTableBuilder.add_attrib_to_element(cell, 'rowspan', self.__get_rowspan(baseline_td))
        row.append(cell)

    def _create_as_extra_cell(self, app_td, app_value, row):
        cell = self.report_builder.create_extra_td(app_value)
        HTMLTableBuilder.append_style_to_element(cell, self.__get_style(app_td))
        HTMLTableBuilder.add_attrib_to_element(cell, 'colspan', self.__get_colspan(app_td))
        HTMLTableBuilder.add_attrib_to_element(cell, 'rowspan', self.__get_rowspan(app_td))
        row.append(cell)

    def create_as_extra_line(self, baseline_tr, row):
        HTMLTableBuilder.append_style_to_element(row, self.__get_style(baseline_tr))
        self.error_msgs.add(ComparisonErros.extra_lines)
        for baseline_td in baseline_tr.xpath('.//td[not(@id)]'):
            cell_value = self.__get_cell_value(baseline_td)
            if cell_value == "missed_or_extra_cell":
                cell_value = ""
            cell = self.report_builder.create_extra_td(cell_value)
            HTMLTableBuilder.append_style_to_element(cell, self.__get_style(baseline_td))
            HTMLTableBuilder.add_attrib_to_element(cell, 'colspan', self.__get_colspan(baseline_td))
            HTMLTableBuilder.add_attrib_to_element(cell, 'rowspan', self.__get_rowspan(baseline_td))
            row.append(cell)
            self.success = False

    def _create_as_missing_line(self, app_tr, row):
        HTMLTableBuilder.append_style_to_element(row, self.__get_style(app_tr))
        self.error_msgs.add(ComparisonErros.missing_lines)
        for app_td in app_tr.xpath('.//td[not(@id)]'):
            cell_value = self.__get_cell_value(app_td)
            if cell_value == "missed_or_extra_cell":
                cell_value = ""
            cell = self.report_builder.create_missing_td(cell_value)
            HTMLTableBuilder.append_style_to_element(cell, self.__get_style(app_td))
            HTMLTableBuilder.add_attrib_to_element(cell, 'colspan', self.__get_colspan(app_td))
            HTMLTableBuilder.add_attrib_to_element(cell, 'rowspan', self.__get_rowspan(app_td))
            row.append(cell)
            self.success = False

    @abstractmethod
    def compare(self):
        """Required method"""

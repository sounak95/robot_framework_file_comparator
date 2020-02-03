
from Libraries.Common.BaselineComparator.HTMLTBodyComparator import HTMLBodyComparator
from Libraries.Common.BaselineComparator.HTMLTBodyComparator import HTMLFooterComparator
from Libraries.Common.BaselineComparator.HTMLTBodyComparator import HTMLHeaderComparator
from Libraries.Utilities import ReportBuilder
from itertools import zip_longest
import lxml.html

class HTMLBaseline(object):
    def __init__(self):
        self.success = True
        self.error_msgs = set()

    @staticmethod
    def convert_csv_to_html(header, body):
        table = lxml.html.fromstring('<table>')

        header_lxml = HTMLBaseline._list_to_tbody(header)
        body_lxml = HTMLBaseline._list_to_tbody(body)

        table.append(header_lxml)
        table.append(body_lxml)
        return lxml.html.tostring(table, encoding='unicode')

    @staticmethod
    def _list_to_tbody(list_of_rows):
        tbody = lxml.html.fromstring('<tbody>')
        for row in list_of_rows:
            tr = lxml.html.fromstring('<tr>')
            for cell_text in row:
                td = lxml.html.fromstring('<td>')
                if cell_text is None:
                    td.text = "missed_or_extra_cell"
                else:
                    td.text = cell_text.strip()
                tr.append(td)
            tbody.append(tr)
        return tbody

    def _open_file(self, baseline_file):
        with open(baseline_file, "rb") as f:
            return f.read()

    def compare_html_pivot_baseline_to_application(self, baseline, app):
        self.success = True
        self.error_msgs = set()

        report = ReportBuilder()
        tbody, thead = self._prepare_table_for_pivot(report)

        app, baseline = self._prepere_lxml_baseline_and_app(app, baseline)
        self._compare_pivot_upper_part(app, baseline, report, thead)

        self._compare_pivot_lower_part(app, baseline, report, tbody)

        return self.success, self.error_msgs

    def _compare_pivot_lower_part(self, app, baseline, report, tbody):
        for row_left, row_right in zip_longest(self._compare_pivot_part(app, baseline, report, 3),
                                                self._compare_pivot_part(app, baseline, report, 4)):

            self._merge_pivot_parts(report, row_left, row_right, tbody)

    def _merge_pivot_parts(self, report, row_left, row_right, tbody):
        if row_left is None:
            row_left = report.create_row()
            td = report.create_td()
            row_left.append(td)
        right_tds = row_right.getchildren()
        for td in right_tds:
            row_left.append(td)
        tbody.append(row_left)

    def _compare_pivot_upper_part(self, app, baseline, report, thead):
        for row_left, row_right in zip_longest(self._compare_pivot_part(app, baseline, report, 1),
                                                self._compare_pivot_part(app, baseline, report, 2)):
            self._merge_pivot_parts(report, row_left, row_right, thead)

    def _prepere_lxml_baseline_and_app(self, app, baseline):
        baseline = lxml.html.fromstring(baseline)
        app = lxml.html.fromstring(app)
        for tr in baseline.xpath(r".//tr[not(.//td[text()])]"):
            tr.drop_tree()
        for tr in app.xpath(r".//tr[not(.//td[text()])]"):
            tr.drop_tree()
        return app, baseline

    def _prepare_table_for_pivot(self, report):
        table = report.create_table()
        thead = report.create_thead()
        tbody = report.create_tbody()
        table.append(thead)
        table.append(tbody)
        return tbody, thead

    def _compare_pivot_part(self, app, baseline, report, index):
        baseline_lxml = baseline.xpath('.//td[@id="no-boarder{}"]'.format(index))[0]
        application_lxml = app.xpath('.//td[@id="no-boarder{}"]'.format(index))[0]
        body_comparator = HTMLBodyComparator(baseline_lxml, application_lxml)
        comparison = list(body_comparator.icompare())
        self.success = self.success and body_comparator.success
        self.error_msgs.update(body_comparator.error_msgs)
        return comparison

    def compare_html_baseline_to_app(self, baseline, app, skip_columns_names=None, sort_column_names=None,
                                     key_column_names=None, missing_columns=None):
        table_comparison = self._compare_table_to_baseline(baseline, app, skip_columns_names,
                                                                              sort_column_names, key_column_names, missing_columns)
        print("*HTML* {}".format(table_comparison))
        return self.success, self.messages

    def _compare_table_to_baseline(self, baseline, app, skip_columns_names=None, sort_column_names=None,
                                   key_column_names=None, missing_columns=[]):
        report = ReportBuilder()
        table = report.create_table()
        app, baseline = self._prepere_lxml_baseline_and_app(app, baseline)
        baseline_header = [i.text_content() for i in
                           baseline.xpath(".//tbody")[0].xpath(".//tr")[0].xpath(".//td[not(@id)]")]
        if missing_columns:
            missing_columns_index = [baseline_header.index(i) for i in missing_columns]
        else:
            missing_columns_index = None
        header_comparator = HTMLHeaderComparator(self._get_tbody_by_index(baseline, 0),
                                                 self._get_tbody_by_index(app, 0),
                                                 skip_columns_names,
                                                 key_column_names
                                                 )
        body_comparator = HTMLBodyComparator(self._get_tbody_by_index(baseline, 1),
                                             self._get_tbody_by_index(app, 1),
                                             header_comparator.get_columns_indexes(skip_columns_names),
                                             header_comparator.get_columns_indexes(sort_column_names),
                                             header_comparator.get_columns_indexes(key_column_names),
                                             baseline_header,
                                             missing_columns_index
                                             )

        footer_comparator = HTMLFooterComparator(self._get_tbody_by_index(baseline, 2),
                                                 self._get_tbody_by_index(app, 2),
                                                 header_comparator.get_columns_indexes(skip_columns_names)
                                                 )

        header_comparison = header_comparator.compare()
        body_comparison, unique_key_found = body_comparator.compare()

        if unique_key_found:
            header_comparator = HTMLHeaderComparator(self._get_tbody_by_index(baseline, 0),
                                                     self._get_tbody_by_index(app, 0),
                                                     skip_columns_names,
                                                     key_column_names=unique_key_found
                                                     )
            header_comparison = header_comparator.compare()
        footer_comparison = footer_comparator.compare()
        table.append(header_comparison)
        table.append(body_comparison)
        table.append(footer_comparison)
        self.success = all([header_comparator.success, body_comparator.success, footer_comparator.success])
        self.messages = set()
        self.messages.update(header_comparator.error_msgs, body_comparator.error_msgs, footer_comparator.error_msgs)
        return report

    @staticmethod
    def _get_tbody_by_index(app, index):
        try:
            app_part = app.xpath(".//tbody")[index]
        except IndexError:
            app_part = lxml.html.fromstring("<p></p>")
        return app_part

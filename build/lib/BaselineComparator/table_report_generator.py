
import unicodedata
import copy
from itertools import zip_longest
from html1.html import HTML
import lxml.html

class HTMLTableReportGenerator(object):
    """
    DO NOT USE - OBSOLETE
    """
    def __init__(self):
        h = HTML()
        self._view = h.div
        self._report_table = self._view.div.table()
        self._report_table.caption.b("Baseline Comparison")
        self._view.hr()
        self._legend_table = self._view.div.table()
        self._create_legend()
        self._current_row = None

    def add_row(self):
        self._current_row = self._report_table.tr

    def add_pass_row(self, *args, **kwargs):
        self.add_row()
        self.add_pass_cell(*args, **kwargs)

    def add_fail_row(self, *args, **kwargs):
        self.add_row()
        self.add_fail_cell(*args, **kwargs)

    def add_warn_row(self, *args, **kwargs):
        self.add_row()
        self.add_warn_cell(*args, **kwargs)

    def add_info_row(self, *args, **kwargs):
        self.add_row()
        self.add_info_cell(*args, **kwargs)

    def add_pass_cell(self, *args, **kwargs):  # baseline, application, header=False):
        cell = self._current_row.th if kwargs.get("header", False) else self._current_row.td
        self._add_pass_cell(cell, *args)

    def _add_pass_cell(self, cell, *args):  # baseline, cell):
        cell("\n".join([str(arg) for arg in args]),
             style="background:#5BB75B;text-align:center")

    def add_fail_cell(self, *args, **kwargs):  # baseline, application, header=False):
        cell = self._current_row.th if kwargs.get("header", False) else self._current_row.td
        self._add_fail_cell(cell, *args)

    def _add_fail_cell(self, cell, *args):
        cell("\n".join([str(arg) for arg in args]),  # ''{}<br />{}'.format(baseline, application),
             style="background:#D9534F;text-align:center")

    def add_warn_cell(self, *args, **kwargs):
        cell = self._current_row.th if kwargs.get("header", False) else self._current_row.td
        self._add_warn_cell(cell, *args)

    def _add_warn_cell(self, cell, *args):
        cell("\n".join([str(arg) for arg in args]),
             style="background:#EFAD4F;text-align:center")

    def add_info_cell(self, *args, **kwargs):
        cell = self._current_row.th if kwargs.get("header", False) else self._current_row.td
        self._add_info_cell(cell, *args)

    def _add_info_cell(self, cell, *args):
        cell("\n".join([str(arg) for arg in args]),
             style="background:#5CBFDE;color:#FFFFFF;text-align:center")

    def _create_legend(self):

        self._legend_table.caption.b("Legend")
        header_row = self._legend_table.thead.tr
        header_row.th(style="width:50px").span("Result")
        header_row.th(style="width:150px").span("Cell Format")
        header_row.th(style="width:300px").span("Description")

        body_row = self._legend_table.tbody.tr
        body_row.td(style="text-align:center").span("PASS")
        self._add_pass_cell(body_row.td, "Application value", "Baseline value")
        body_row.td.span("Values are equal.")

        body_row = self._legend_table.tbody.tr
        body_row.td(style="text-align:center").span("FAIL")
        self._add_fail_cell(body_row.td, "Application value", "Baseline value")
        body_row.td.span("Values are not equal.")

        body_row = self._legend_table.tbody.tr
        body_row.td(style="text-align:center").span("FAIL")
        self._add_warn_cell(body_row.td, "Application value", "Baseline value")
        body_row.td.span("Either of values is missing.")

    def get_html_report(self):
        return self._view


legend = """
<table>
    <tbody>
        <tr>
            <th style="background:#5cb85c">PASS</th>
            <th style="background:#d9534f">FAIL</th>
            <th style="background:#b7b7b7">SKIP</th>
            <th style="background:#727fbf">MISSING ROW</th>
            <th style="background:#bfbc72">ADDITIONAL ROW</th>
        </tr>
        <tr>
            <td style="background:#5cb85c">Matched value</td>
            <td style="background:#d9534f">Baseline value\nApplication value</td>
            <td style="background:#b7b7b7">Baseline value\nApplication value</td>
            <td style="background:#727fbf">Baseline value</td>
            <td style="background:#bfbc72">Application value</td>
        </tr>
    </tbody><caption><b>Legend</b></caption>
</table>
        """


class HTMLComparator(object):
    def __init__(self, baseline, application, skip_columns_indexes=None):
        self.error_msgs = set()
        self.skip_columns_indexes = skip_columns_indexes or []

        self.lxml_baseline = lxml.html.fromstring(baseline) if isinstance(baseline, str) else baseline
        self.lxml_application = lxml.html.fromstring(application) if isinstance(application, str) else application

        for tr in self.lxml_baseline.xpath(r".//tr[not(.//td[text()])]"):
            tr.drop_tree()
 
        for tr in self.lxml_application.xpath(r".//tr[not(.//td[text()])]"):
            tr.drop_tree()

        self.application_trs = self.lxml_application.xpath('.//tr')
        self.baseline_trs = self.lxml_baseline.xpath('.//tr')

    def _create_report_holder(self):
        if len(self.baseline_trs) > len(self.application_trs):
            self.lxml_report = copy.deepcopy(self.lxml_baseline)
        else:
            self.lxml_report = copy.deepcopy(self.lxml_application)

    def compare(self):
        self._create_report_holder()

        success = True
        rows = zip_longest(self.lxml_baseline.xpath('.//tr'),
                            self.lxml_application.xpath('.//tr'),
                            self.lxml_report.xpath('.//tr'))

        for baseline_tr, app_tr, report_tr in rows:

            row_success = self._compare_row(app_tr, baseline_tr, report_tr)
            success = success and row_success

        return success, self.error_msgs

    def _compare_row(self, app_tr, baseline_tr, report_tr):
        if baseline_tr is None:
            self.error_msgs.add(ComparisonErros.extra_lines)
            self._format_extra_row(report_tr.xpath('.//td[not(@id)]'))
            return False
        if app_tr is None:
            self.error_msgs.add(ComparisonErros.missing_lines)
            self._format_missing_row(report_tr.xpath('.//td[not(@id)]'))
            return False
        cells = zip_longest(baseline_tr.xpath('.//td[not(@id)]'),
                             app_tr.xpath('.//td[not(@id)]'),
                             report_tr.xpath('.//td[not(@id)]'))
        return self._compare_cells(cells)

    def _compare_cells(self, cells):
        success = True
        for index, cells in enumerate(cells):
            baseline_td, app_td, report_td = cells
            baseline_value = self._get_cell_value(baseline_td)
            app_value = self._get_cell_value(app_td)
            if index in self.skip_columns_indexes:
                self._format_skip_td(baseline_td=baseline_td, application_td=app_td, report_td=report_td)
                continue
            if baseline_value == app_value:
                self._format_pass_td(report_td)
            else:
                self._format_fail_td(baseline_td=baseline_td, application_td=app_td, report_td=report_td)
                success = False
                self.error_msgs.add(ComparisonErros.fail_cell)
        return success

    def _get_cell_value(self, td):
        try:
            value = td.text_content()
        except:
            value = 'No Data'
        return value

    def _format_pass_td(self, report_td):
        report_td.attrib['style'] = "background:#5cb85c"

    def _format_fail_td(self, baseline_td, application_td, report_td):
        self._add_baseline_and_app_text_values(baseline_td=baseline_td, application_td=application_td,
                                               report_td=report_td)
        report_td.attrib['style'] = "background:#d9534f"

    def _format_warn_td(self, report_td):
        report_td.attrib['style'] = "background:#EFAD4F"

    def _format_missing_td(self, report_td):
        report_td.attrib['style'] = "background:#727fbf"

    def _format_extra_td(self, report_td):
        report_td.attrib['style'] = "background:#bfbc72"

    def _format_skip_td(self, baseline_td, application_td, report_td):
        self._add_baseline_and_app_text_values(baseline_td=baseline_td, application_td=application_td,
                                               report_td=report_td)
        report_td.attrib['style'] = "background:#b7b7b7"

    def _format_extra_row(self, cells):
        for cell in cells:
            self._format_extra_td(cell)

    def _format_missing_row(self, cells):
        for cell in cells:
            self._format_missing_td(cell)

    def _add_baseline_and_app_text_values(self, baseline_td, application_td, report_td):
        report_td.text = None
        report_td.append(
            lxml.html.fromstring(
                "<span>{}<br>{}<span>".format(
                    self._get_cell_value(baseline_td),
                    self._get_cell_value(application_td)
                )
            )
        )

    def get_html_report(self):
        return lxml.html.tostring(self.lxml_report) + legend

    def get_raw_html_comparison(self):
        return lxml.html.tostring(self.lxml_report)

    @staticmethod
    def attach_legend(html_string):
        return html_string + legend


class HTMLGenerator(object):
    def __init__(self, template, *tables):

        html_string = template.format(*tables)
        self.lxml_html = lxml.html.fromstring(html_string)
        self._delete_dispensable_tags()
        self._clear_html_from_attributes()

    def _normalize(self, text):
        return unicodedata.normalize("NFKD", text.strip())

    def _clear_html_from_attributes(self):
        raise NotImplementedError

    def _delete_dispensable_tags(self):
        raise NotImplementedError

    def save_to_file(self, table_name):
        html_string = self.get_html_string()
        with open(table_name, 'w') as html_table:
            html_table.write(html_string)

    def get_html_string(self):
        return lxml.html.tostring(self.lxml_html)

    def get_html_report(self):
        return lxml.html.tostring(self.lxml_html)

class HTMLPivotGenerator(HTMLGenerator):

    def __init__(self, header_up, header_left, body):
        template = """
        <table style='white-space: nowrap; font-family: inherit'>
            <tbody>
            <tr>
                <td id='no-boarder1'></td>
                <td id='no-boarder2'>
                {}
                </td>
            </tr>
            <tr>
                <td id='no-boarder3'>
                {}
                </td>
                <td id='no-boarder4'>
                {}
                </td>
            </tr>
            </tbody>
        </table>

        """

        super(HTMLPivotGenerator, self).__init__(
            template,
            header_up,
            header_left,
            body
        )

    def _clear_html_from_attributes(self):
        for tag in self.lxml_html.xpath('//*[@class]'):
            tag.attrib.pop('class')

    def _delete_dispensable_tags(self):
        for td in self.lxml_html.xpath('//td[not(@id)]'):
            for span in td.xpath('.//span'):
                span.drop_tag()
            for div in td.xpath('.//div'):
                div.drop_tag()
            td.text = self._normalize(str(td.text_content()))


class HTMLTableGenerator(HTMLGenerator):
    def __init__(self, header, body, footer):
        template = """
        <table>
            {}
            {}
            {}
        </table>
        """
        self.header_with_id = header
        self.body_with_id = body
        self.footer_with_id = footer if footer else ""

        super(HTMLTableGenerator, self).__init__(
            template,
            self.header_with_id,
            body,
            footer
        )

    def _clear_html_from_attributes(self):
        for tag in self.lxml_html.xpath('//*[@class]'):
            tag.attrib.pop('class')

    def _delete_dispensable_tags(self):
        for td in self.lxml_html.xpath('//td[not(@id)]'):
            for div in td.xpath('./div'):
                div.drop_tag()
            for div in td.xpath('./span'):
                div.drop_tag()
            td.text = self._normalize(str(td.text_content()))


class ComparisonErros:
    default = "Baseline comparison did not succeed!"
    fail_cell = "Found not matching cells."
    extra_lines = "Extra lines or columns found."
    missing_lines = "Missing lines or columns found."


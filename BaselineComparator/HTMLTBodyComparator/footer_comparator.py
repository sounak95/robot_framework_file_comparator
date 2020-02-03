from Libraries.Common.BaselineComparator.HTMLTBodyComparator import HTMLTBodyComparatorABC


class HTMLFooterComparator(HTMLTBodyComparatorABC):
    def __init__(self, baseline, app, skip_column_indexes=None):
        super(HTMLFooterComparator, self).__init__()
        self.baseline = baseline
        self.app = app
        self.skip_column_indexes = skip_column_indexes

    def compare(self):
        tbody = self.report_builder.create_tbody()
        for row in self._compare_tbody(self.baseline,
                                       self.app,
                                       self.skip_column_indexes):
            tbody.append(row)

        return tbody

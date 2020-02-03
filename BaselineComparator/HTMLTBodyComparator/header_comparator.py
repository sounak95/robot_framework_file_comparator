from Libraries.Common.BaselineComparator.HTMLTBodyComparator import HTMLTBodyComparatorABC


class HTMLHeaderComparator(HTMLTBodyComparatorABC):
    def __init__(self, baseline, app, skip_column_names=None, key_column_names=None):
        super(HTMLHeaderComparator, self).__init__()
        self.baseline = baseline
        self.app = app
        self._skip_column_names = skip_column_names
        self.key_column_names = key_column_names



    def compare(self):
        skip_column_indexes = self.get_columns_indexes(self._skip_column_names)
        tbody = self.report_builder.create_tbody()
        if self.key_column_names is not None:
            key_column_indexes = self.get_columns_indexes(self.key_column_names)
            is_header = True
        else:
            key_column_indexes = None
            is_header = False
        for row in self._compare_tbody(self.baseline,
                                       self.app,
                                       skip_column_indexes,
                                       key_column_indexes,
                                       is_header=is_header
                                       ):
            tbody.append(row)

        return tbody

    def compare_and_build_tbody(self):
        tbody = self.report_builder.create_tbody()
        for row in self.compare():
            tbody.append(row)

    def get_columns_indexes(self, column_names):
        if column_names is None:
            return []
        try:
            app_indexes = [[col.text for col in self.app.xpath('.//td')].index(skip_col)
                           for skip_col in column_names]
        except:
            raise AssertionError("Column '{}' is not present in application file".format(skip_col))
        try:
            baseline_indexes = [[col.text for col in self.baseline.xpath('.//td')].index(skip_col)
                                for skip_col in column_names]
        except:
            raise AssertionError("Column '{}' is not present in baseline file".format(skip_col))
        if app_indexes != baseline_indexes:
            raise AssertionError("Columns {} have different indexes in baseline {} and application {}".format(
                column_names,
                baseline_indexes,
                app_indexes))

        return app_indexes



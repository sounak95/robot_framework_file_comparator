import copy
from robot.api import logger
from Libraries.Common.BaselineComparator.HTMLTBodyComparator import HTMLTBodyComparatorABC


class HTMLBodyComparator(HTMLTBodyComparatorABC):
    def __init__(self, baseline, app, skip_columns_indexes=None, sort_column_indexes=None, key_column_indexes=None, baseline_header=None, missing_columns_index=None):
        super(HTMLBodyComparator, self).__init__()
        self.baseline = baseline
        self.app = app
        self.skip_column_indexes = skip_columns_indexes or []
        self.sort_column_indexes = sort_column_indexes or []
        self.key_column_indexes = key_column_indexes or []
        self.unique_key_columns_name = []
        self.missing_columns_index = missing_columns_index or []
        self.baseline_header = baseline_header
        self._sort_body()
        self._check_key_columns()
        self._order_by_key_columns()
        self.length = 0


    def icompare(self):
        return self._compare_tbody(self.baseline,
                                   self.app,
                                   self.skip_column_indexes)

    def compare(self):
        tbody = self.report_builder.create_tbody()
        for row in self._compare_tbody(self.baseline,
                                       self.app,
                                       self.skip_column_indexes,
                                       self.key_column_indexes):
            tbody.append(row)
        return tbody, self.unique_key_columns_name

    def _sort_body(self):
        if not self.sort_column_indexes:
            return
        def key(row):
            return [row.xpath(".//td")[i].text_content() for i in self.sort_column_indexes]

        self.baseline[:] = sorted(list(self.baseline), key=key)
        self.app[:] = sorted(list(self.app), key=key)

    def _check_key_columns(self):
        if not self.key_column_indexes:
            return
        key_columns = [tuple(tr[i].text_content() for i in self.key_column_indexes) for tr in self.baseline]
        key_columns_app = [tuple(tr[i].text_content() for i in self.key_column_indexes) for tr in self.app]
        if not len(set(key_columns)) == len(key_columns):
            logger.warn("Key columns are not unique in baseline!")
            print("Finding unique key columns...")
            self._find_unique_key()
        else:
            print("Your key columns are Unique.")
            self.unique_key_columns_name = None

    def _find_unique_key(self):
        unique_key = False
        key_column_indexes_temp = [i for i in self.key_column_indexes]
        for i in range(0, len(self.baseline[0])):
            if i not in key_column_indexes_temp and i not in self.skip_column_indexes and i not in self.missing_columns_index and \
                            self.baseline_header[i] != 'missed_or_extra_cell':
                key_column_indexes_temp.append(i)
                key_columns = [tuple(tr[i].text_content() for i in key_column_indexes_temp) for tr in self.baseline]
                if len(set(key_columns)) == len(key_columns):
                    self.key_column_indexes.append(i)
                    print(("Unique key columns found : {}".format(
                        [self.baseline_header[i] for i in self.key_column_indexes])))
                    key_column_names_test = [self.baseline_header[i] for i in self.key_column_indexes]
                    self.unique_key_columns_name = key_column_names_test
                    unique_key = True
                    break
        if not unique_key:
            logger.warn("Comparator cannot find any unique key columns in baseline!")
            self.unique_key_columns_name = None

    def _order_by_key_columns(self):
        if not self.key_column_indexes:
            return
        matching_indexes = self._find_matching_columns()
        self._order_by_keys(matching_indexes)

    def _order_by_keys(self, matching_indexes):
        for baseline_index, app_index in matching_indexes:
            self.app.append(copy.deepcopy(self.app[app_index]))
            self.baseline.append(copy.deepcopy(self.baseline[baseline_index]))
        baseline_indexes = sorted([i[0] for i in matching_indexes], reverse=True)
        app_indexes = sorted([i[1] for i in matching_indexes], reverse=True)
        for baseline_index in baseline_indexes:
            self.baseline.remove(self.baseline[baseline_index])
        for app_index in app_indexes:
            self.app.remove(self.app[app_index])
        self.baseline[:] = reversed(self.baseline)
        self.app[:] = reversed(self.app)

    def _find_matching_columns(self):
        baseline_key_columns = self._get_baseline_column_values(self.key_column_indexes)
        app_key_columns = self._get_app_column_values(self.key_column_indexes)
        matching_indexes = []
        matching_app_index = []
        start = -1
        for baseline_index, baseline_key in enumerate(baseline_key_columns):
            try:
                app_index = app_key_columns.index(baseline_key, start+1)
                matching_app_index.append(app_index)
                matching_indexes.append((baseline_index, app_index))
                start = app_index
            except ValueError:
                print(("Baseline key {} is not found in app".format(baseline_key)))
        return matching_indexes

    def _get_column_values(self, body, indexes):
        return [tuple(row[i].text_content() for i in indexes) for row in body]

    def _get_baseline_column_values(self, indexes):
        return self._get_column_values(self.baseline, indexes)

    def _get_app_column_values(self, indexes):
        return self._get_column_values(self.app, indexes)
import os
from robot.libraries.BuiltIn import BuiltIn
try:
    from robot.libraries.BuiltIn import RobotNotRunningError
except ImportError:
    RobotNotRunningError = AttributeError

class GridPath(object):
    _csv_grid_index = 0

    def _get_html_table_path(self, filename=None, filepath=None):
        return self._get_grid_table_path('dx_table', filename, filepath=filepath)

    def get_html_pivot_path(self, filename=None):
        return self._get_grid_table_path('dx_pivot', filename,'html')

    def get_html_pivot_unsorted_HTML_path(self,filename_type, filename=None):
        return self._get_grid_table_path("Unsorted_HTML_"+filename_type, filename, 'html')

    def get_html_pivot_sorted_HTML_path(self,filename_type, filename=None):
        return self._get_grid_table_path("sorted_HTML_"+filename_type, filename, 'html')

    def _get_log_dir(self):
        try:
            variables = BuiltIn().get_variables()

            logfile = variables['${LOG FILE}']
            if logfile != 'NONE':
                return os.path.dirname(logfile)
            return variables['${OUTPUTDIR}']

        except RobotNotRunningError:
            return os.getcwd()

    def _get_grid_table_path(self, grid_type, filename, extension='html', filepath=None):

        if not filepath:
            filepath = ""

        if not filename:
            self._csv_grid_index += 1
            filename = 'mb-csv-%s-%d.%s' % (grid_type, self._csv_grid_index, extension)
        else:
            filename = filename.replace('/', os.sep)

        tableDir = self._get_log_dir()
        path = os.path.join(tableDir, filepath, filename)
        return path

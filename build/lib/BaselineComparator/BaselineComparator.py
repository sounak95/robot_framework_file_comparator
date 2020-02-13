import csv
import json
import shutil
import os.path
from BaselineComparator.html_baseline import HTMLBaseline
from BaselineComparator.table_parser import TableParser
from BaselineComparator.json_comparator import CMF_baseline_compare, compare_jsons
from BaselineComparator.xml_comparator import compare_xml,sort_xml
from robot.libraries.BuiltIn import BuiltIn
from collections import OrderedDict
import sys
from robot.api import logger
import xlrd
import xlwt
import importlib

class BaselineComparator(object):
    """
    Library for comparison of files in different formats.

    This library is part of the ${fusionresource}
    """
    importlib.reload(sys)
    table_parser = TableParser()

    def compare_csv_files(self, baseline_file, app_file, delimiter=',', skip_columns_names=None,
                             sort_columns_names=None, key_columns_names=None, number_of_valid_digits=None, delete_files="False"):
        """
        Compares csv files and copy it to runtime output_dir. By default delimiter is set to ','.
        | Compare Csv Files | ${CURDIR}\\\\baseline.csv  | ${CURDIR}\\\\app.csv |
        | Compare Csv Files | ${CURDIR}\\\\baseline.csv  | ${CURDIR}\\\\app.csv | delimiter=';' |

        To use skip columns or sort functionalities passing list arguments is required.
        | Compare Csv Files | ${CURDIR}/baseline_key_column.csv | ${CURDIR}/app_key_column.csv | sort_columns_names=@{Sort Colums} |
        | Compare Csv Files | ${CURDIR}/baseline_key_column.csv | ${CURDIR}/app_key_column.csv | skip_columns_names=@{Skip Colums} |
        | Compare Csv Files | ${CURDIR}/baseline_key_column.csv | ${CURDIR}/app_key_column.csv | key_columns_names=@{Key Colums} |
        | Compare Csv Files | ${CURDIR}/baseline_key_column.csv | ${CURDIR}/app_key_column.csv | skip_columns_names=@{Skip Colums} | sort_column_names=@{Sort Colums} |
        | Compare Csv Files | ${CURDIR}/baseline_key_column.csv | ${CURDIR}/app_key_column.csv | skip_columns_names=@{Skip Colums} | sort_column_names=@{Sort Colums} |

        To delete csv files for every comparison from runtime output_dir, set argument "delete_files=True". By default delete_files functionality is disabled.
        | Compare Csv Files | ${CURDIR}\\\\baseline.csv  | ${CURDIR}\\\\app.csv |  delete_files=True  |

        For the current version it is possibly to sort values alphabetically only.
        """
        outpur_dir = BuiltIn().get_variable_value("${OUTPUT_DIR}")
        if not os.path.exists(baseline_file):
            raise AssertionError('File \'%s\' does not exists !!' % (baseline_file))
        if not os.path.exists(app_file):
            raise AssertionError('File \'%s\' does not exists !!' % (app_file))
        head, tail = os.path.split(baseline_file)
        if not os.path.isfile(outpur_dir + "\\" + tail):
            shutil.copy(baseline_file, outpur_dir)
            shutil.copy(app_file, outpur_dir)
        html_manager = HTMLBaseline()
        app_headers, app_body = self._csv_file_to_list(app_file, str(delimiter), number_of_valid_digits)
        baseline_headers, baseline_body = self._csv_file_to_list(baseline_file, str(delimiter), number_of_valid_digits)
        baseline_headers, baseline_body, app_headers, app_body, missing_columns = self._arrange_baseline_and_app_file(baseline_headers, baseline_body, app_headers, app_body)
        app_html = html_manager.convert_csv_to_html(app_headers, app_body)
        baseline_html = html_manager.convert_csv_to_html(baseline_headers, baseline_body)
        success, error_msgs = html_manager.compare_html_baseline_to_app(baseline_html, app_html, skip_columns_names, sort_columns_names, key_columns_names, missing_columns)
        if delete_files.lower() == "true":
            head1, tail1 = os.path.split(baseline_file)
            head2, tail2 = os.path.split(app_file)
            if os.path.isfile(outpur_dir + "\\" + tail1):
                os.remove(outpur_dir + "\\" + tail1)
            if os.path.isfile(outpur_dir + "\\" + tail2):
                os.remove(outpur_dir + "\\" + tail2)
        if not success:
            raise AssertionError(" ".join(error_msgs))

    def _arrange_baseline_and_app_file(self, baseline_headers, baseline_body,app_headers, app_body):
        baseline_headers = baseline_headers[0]
        app_headers = app_headers[0]
        missing_columns = list(sorted(set(baseline_headers) - set(app_headers)))
        extra_columns = list(sorted(set(app_headers) - set(baseline_headers)))
        baseline_new = list(baseline_headers)
        app_new = list(app_headers)
        missing_columns_index = []
        extra_column_index = []
        if missing_columns:
            for m in missing_columns:
                missing_columns_index.append(baseline_headers.index(m))
                baseline_new.remove(m)
        if extra_columns:
            for a in extra_columns:
                extra_column_index.append(app_headers.index(a))
                app_new.remove(a)
        baseline_new.sort()
        app_new.sort()
        sorted_baseline_header_index = [baseline_headers.index(d) for d in baseline_new]
        sorted_app_header_index = [app_headers.index(d) for d in app_new]
        baseline_body, missing_columns_data = self._arrange_baseline_body(baseline_body, sorted_baseline_header_index,
                                                                     missing_columns_index)
        app_body, extra_column_data = self._arrange_app_body(app_body, sorted_app_header_index, extra_column_index)
        if missing_columns:
            for m in missing_columns:
                baseline_new.append(m)
                app_new.append(None)
            for d in range(0, len(baseline_body)):
                for m in missing_columns_data[d]:
                    baseline_body[d].append(m)
            for i in range(0, len(missing_columns)):
                for a in app_body:
                    a.append(None)
        if extra_columns:
            for e in extra_columns:
                app_new.append(e)
                baseline_new.append(None)
            for d in range(0, len(app_body)):
                for e in extra_column_data[d]:
                    app_body[d].append(e)
            for i in range(0, len(extra_columns)):
                for a in baseline_body:
                    a.append(None)
        baseline_header = [baseline_new]
        app_header = [app_new]
        return baseline_header, baseline_body, app_header, app_body, missing_columns

    def _arrange_baseline_body(self, baseline_body, sorted_baseline_header_index, missing_columns_index):
        baseline_body_new = []
        missing_columns_data = []
        baseline_body = [i for i in baseline_body if i]
        for data in baseline_body:
            if missing_columns_index:
                missing_columns_data.append([data[i] for i in missing_columns_index])
            baseline_body_new.append([data[i] for i in sorted_baseline_header_index])
        return baseline_body_new, missing_columns_data

    def _arrange_app_body(self, app_body, sorted_app_header_index, extra_column_index):
        app_body_new = []
        extra_column_data = []
        app_body = [i for i in app_body if i]
        for data in app_body:
            if extra_column_index:
                extra_column_data.append([data[i] for i in extra_column_index])
            app_body_new.append([data[i] for i in sorted_app_header_index])
        return app_body_new, extra_column_data

    @staticmethod
    def _csv_file_to_list(baseline_file, delimiter=',', number_of_valid_digits=None):
        with open(baseline_file, "r") as f:
            baseline = list(csv.reader(f, delimiter=delimiter))
        if number_of_valid_digits is not None:
            BaselineComparator._round_floats(baseline, number_of_valid_digits=int(number_of_valid_digits))
        return baseline[:1], baseline[1:]

    def compare_xls_files(self, app_file, baseline_file, app_sheet=None, baseline_sheet=None,
                             skip_columns_names=None, sort_data_in_file=False):
        """
                Compares 2 different xls or xlsx files or one xls with another xlsx file and generates report in html format.

                The features of this keyword are:
                - Comparison of the content of 2 files. First file being the app file and second one is the baseline file.
                - Enabled with skipping of multiple columns while comparison.
                - Data in files could be sorted with parameter 'sort_data_in_file' passed as "True" for comparison.
                - Comparison report will be shown in the log in the form of html table.

                |Arguments|

                 'app_file' = path of the file to be compared.

                 'baseline_file' = path of the baseline file.

                 'app_sheet'[Optional] = Sheet name of the files to be compared. If 'app_sheet' argument value is not provided,
                                by default it will consider the first sheet of the file for comparison.

                 'baseline_sheet'[Optional] = Sheet name of the baseline file to be compared. If 'baseline_sheet' argument value is not provided,
                                by default it will consider the first sheet of the file for comparison.

                 'skip_columns_names'[Optional] = Column names to be skipped while comparision.
                                Needs to be passed in the form of a list, see in example. By default the value is set to None.

                 'sort_data_in_file'[Optional] = Data for both files to be sorted for comparision.
                                Needs to be passed as "True", see in example 5. By default the value is set to "False".

                 |Example|

                 1. Compare two xls files.
                 | Compare Xls Files | D:/testExcel/appfile.xls | D:/testExcel/baselinefile.xls |

                 2. Compare two xlsx files.
                 | Compare Xls Files | D:/testExcel/appfile.xlsx | D:/testExcel/baselinefile.xlsx |

                 3. Compare xls file with xlsx file.
                 | Compare Xls Files | D:/testExcel/appfile.xls | D:/testExcel/baselinefile.xlsx |

                 4. Compare two xlsx files with sheet names.
                 | Compare Xls Files | D:/testExcel/appfile.xlsx | D:/testExcel/baselinefile.xlsx | app_sheet=appsheet | baseline_sheet=baselinesheet |

                 5. Compare two xlsx files with Sorting the data.
                 | Compare Xls Files | D:/testExcel/appfile.xlsx | D:/testExcel/baselinefile.xlsx | app_sheet=appsheet | baseline_sheet=baselinesheet | sort_data_in_file= True |

                 6. Compare two xlsx files with skipped column names.
                 *** Variables ***
                 @{SkipColumns}    Column6    Column7

                 | ***TestCases*** |
                 | Compare Xls Files | D:/testExcel/appfile.xlsx | D:/testExcel/baselinefile.xlsx | skip_columns_names=${SkipColumns} |

                 7. Compare two xlsx files with sheet names and skipped column names.
                 *** Variables ***
                 @{SkipColumns}    Column6    Column7

                 | ***TestCases*** |
                 | Compare Xls Files | D:/testExcel/appfile.xlsx | D:/testExcel/baselinefile.xlsx | app_sheet=appsheet | baseline_sheet=baselinesheet | skip_columns_names=${SkipColumns} |
        """
        output_dir = BuiltIn().get_variable_value("${OUTPUT_DIR}")
        if not os.path.exists(app_file):
            raise AssertionError('app file: {} does not exists !!'.format(app_file))
        if not os.path.exists(baseline_file):
            raise AssertionError('baseline file: {} does not exists !!'.format(baseline_file))
        name1, fileformat1 = os.path.splitext(app_file)
        name2, fileformat2 = os.path.splitext(baseline_file)
        app_fileformat = fileformat1.replace(".", "")
        baseline_fileformat = fileformat2.replace(".", "")
        if app_fileformat not in ['xls', 'xlsx']:
            raise AssertionError('Please provide app file format as xls or xlsx')
        if baseline_fileformat not in ['xls', 'xlsx']:
            raise AssertionError('Please provide baseline file format as xls or xlsx')
        head1, tail1 = os.path.split(app_file)
        head2, tail2 = os.path.split(baseline_file)
        app_file_outputpath = output_dir + "\\" + tail1
        baseline_file_outputpath = output_dir + "\\" + tail2
        if not os.path.isfile(app_file_outputpath):
            shutil.copy(app_file, output_dir)
        if not os.path.isfile(baseline_file_outputpath):
            shutil.copy(baseline_file, output_dir)
        if sort_data_in_file:
            self._sort_xls_file(filepath=app_file, outputpath=app_file_outputpath, sheetname=app_sheet)
            self._sort_xls_file(filepath=baseline_file, outputpath=baseline_file_outputpath, sheetname=baseline_sheet)
        html_manager = HTMLBaseline()
        baseline_headers, baseline_body = self._xls_file_to_list(baseline_file_outputpath, app_sheet)
        app_headers, app_body = self._xls_file_to_list(app_file_outputpath, baseline_sheet)
        baseline_headers, baseline_body, app_headers, app_body, missing_columns = self._arrange_baseline_and_app_file(
            baseline_headers, baseline_body, app_headers, app_body)
        app_html = html_manager.convert_csv_to_html(app_headers, app_body)
        baseline_html = html_manager.convert_csv_to_html(baseline_headers, baseline_body)
        success, error_msgs = html_manager.compare_html_baseline_to_app(baseline_html, app_html, skip_columns_names)
        if os.path.isfile(app_file_outputpath):
            os.remove(app_file_outputpath)
        if os.path.isfile(baseline_file_outputpath):
            os.remove(baseline_file_outputpath)
        if not success:
            raise AssertionError("Excel baseline comparison failed!")

    def _xls_file_to_list(self, filename, sheetname):
        workbook = xlrd.open_workbook(filename)
        if not sheetname:
            currentsheet = workbook.sheets()[0]
        else:
            currentsheet = workbook.sheet_by_name(sheetname)
        rows = []
        for i in range(currentsheet.nrows):
            columns = []
            for j in range(currentsheet.ncols):
                try:  # Updated to handle auto conversion of int to float
                    cell = currentsheet.cell(i, j)
                    if cell.ctype == xlrd.XL_CELL_TEXT:
                        value = cell.value.strip()
                    elif cell.value == int(cell.value):
                        value = str(int(cell.value))
                    else:
                        value = str(cell.value)
                except:
                    value = currentsheet.cell(i, j).value
                columns.append(value)
            rows.append(columns)
        return rows[:1], rows[1:]
        
    def compare_json_data(self, data1, data2, output_file=None, is_data1_file=False, is_data2_file=False, ignored_keys=None,
                              nb_of_valid_decimal_places=100):
        """
        Compares two jsons.
        If is_data1_file=True the contents are loaded from file pointed by 'data1'. Otherwise it's treated as JSON string.
        Same for is_data2_file.
        Keyword raises error if there are differences in files. output_file parameter is obsolete.
        """
        if ignored_keys is None:
            ignored_keys = []
        if is_data1_file:
            with open(data1) as file:
                first_file = file.read()
        else:
            first_file = data1
        if is_data2_file:
            with open(data2) as file:
                second_file = file.read()
        else:
            second_file = data2
        status, text = compare_jsons(first_file, second_file, ignored_keys, nb_of_valid_decimal_places)
        if status == 0:
            logger.info(text, True)
            raise AssertionError("There are differences in files!")
            
    def compare_json_with_baseline_file(self, json_baseline_file, json_data, ignored_keys=None, nb_of_valid_decimal_places=100, nb_of_digit_after_decimal=0, wild_card=None):
        """
        This keyword is used to compare two json files/ API Response with the baseline json file
        :param json_baseline_file: Location of the baseline file
        :param json_data: json content to be compared to baseline file content
        :param ignored_keys: values  of the keys to be ignored in the comparison
        :param nb_of_valid_decimal_places: comparison of digits after decimal by rounding off the digits
        example:
         If the number is 1.567, it will round it off to 1.57
        :param nb_of_digit_after_decimal: comparison of digits after decimal in case of numbers
        :param wild_card: It symbolises the character used in the subset of values to ignore the comparison.
        Example:
        If the value is provided with wildcard *, i.e *test*, it will be ignored
        If the value is not  provided with wildcard *, i.e test, it will be compared
        """
        if ignored_keys is None:
            ignored_keys = []
        with open(json_baseline_file, 'r') as baseline:
            status, text = CMF_baseline_compare(baseline, json_data, ignored_keys, nb_of_valid_decimal_places, nb_of_digit_after_decimal, wild_card)
            print(("*HTML*{}".format(text)))
            if status == 0:
                raise AssertionError("There are differences in files!")            

    def json_inner_list_sort(self, json_file, key_to_sort_by, *path_to_list):
        """
        Sorting a list by a 'key_to_sort_by'. path_to_the list in the 'json_file' should be given as a list.
        Example of usage:
        | ${sorted_out} | json inner list sort | unsorted.json | attributes | rows |
        """
        with open(json_file, 'r') as json_data:
            json_loaded = json.load(json_data)
            list_to_sort = json_loaded
            if type(list_to_sort) == type([]):
                list_to_sort = list_to_sort[0]
            previous = []
            is_list = False
            for pointer in path_to_list:
                previous = list_to_sort
                if type(list_to_sort) == type([]):
                    if pointer == path_to_list[-1]:
                        is_list = True
                        li = []
                        for l in list_to_sort:
                            if pointer in l:
                                li.append(l[pointer])
                        list_to_sort = [i for i in li]
                else:
                    list_to_sort = list_to_sort[pointer]
            if len(path_to_list) > 0:
                if is_list:
                    for i in range(0, len(list_to_sort)):
                        previous[i][path_to_list[-1]] = sorted(list_to_sort[i], key=lambda elem: elem[key_to_sort_by])
                else:
                    previous[path_to_list[-1]] = sorted(list_to_sort, key=lambda elem: elem[key_to_sort_by])
            return json.dumps(json_loaded)

    @staticmethod
    def _round_floats(baseline, number_of_valid_digits=100):
        for idx1, line in enumerate(baseline):
            for idx2, cell_value in enumerate(line):
                try:
                    baseline[idx1][idx2] = str(round(float(cell_value), number_of_valid_digits))
                except:
                    pass

    def compare_xml_with_baseline_file(self, baselinexml, responsexml, ignored_keys=None, nb_of_valid_decimal_places=100):
        """

        comparison of the content of 2 xmls(baselinexml and responsexml), 1 file is given as baseline and the second one is generated during a test
        ignored_keys - keys to be ignored in comparison
        """
        if ignored_keys is None:
            ignored_keys = []
        with open(baselinexml, 'r') as baseline:
            status, text = compare_xml(baselinexml,responsexml,ignored_keys,nb_of_valid_decimal_places)
            print(("*HTML*{}".format(text)))
            if status == 0:
                raise AssertionError("There are differences in files!")

    def xml_sort(self, unsortedxml, sortedxml ,sort_key_tag=None,root_xpath=None,reverse=False):
        """
        Sorting the xml based on the unique tag and root xpath given
        """
        with open(unsortedxml, 'r') as baseline:
            sorted_file = sort_xml(unsortedxml,sortedxml,sort_key_tag,root_xpath,reverse)
        return sorted_file

    def _get_data_from_list(self, locator, filepath):
        d = OrderedDict()
        values = self._get_text_of_all_elements(locator)
        for k in range(0, len(values)):
            d[k+1] = values[k]
        jstr = json.dumps(d)
        with open(filepath, "w") as file:
            file.write(jstr)
        return jstr

    def list_baseline_comparator(self, locator, baseline_filepath):
        """| Usage |
        It compares the list creates from the application with the baseline list.

          | Arguments |

         'locator' = locator of the list

         'baseline_filepath' = Baseline file location

        """
        appfile_dir = BuiltIn().get_variable_value("${OUTPUT_DIR}")
        appfile_loc = "{}/appfile.json".format(appfile_dir)
        jstr = self._get_data_from_list(locator, appfile_loc)
        if not os.path.exists(baseline_filepath):
            raise AssertionError("File not found error: {} file does not exist".format(baseline_filepath))
        with open(baseline_filepath, "r") as f:
            baseline_data = f.read()
        BaselineComparator().compare_json_data(jstr, baseline_data)

    def _sort_xls_file(self, filepath, outputpath, sheetname=None):

        target_column = 0  # This example only has 1 column, and it is 0 indexed
        workbook = xlrd.open_workbook(filepath)
        if not sheetname:
            sheet = workbook.sheets()[0]
        else:
            sheet = workbook.sheet_by_name(sheetname)
        data = [sheet.row_values(i) for i in range(sheet.nrows)]
        labels = data[0]  # Don't sort our headers
        data = data[1:]  # Data begins on the second row
        data.sort(key=lambda x: x[target_column])
        bk = xlwt.Workbook()
        sheet = bk.add_sheet(sheet.name)

        for idx, label in enumerate(labels):
            sheet.write(0, idx, label)

        for idx_r, row in enumerate(data):
            for idx_c, value in enumerate(row):
                sheet.write(idx_r + 1, idx_c, value)
        bk.save(outputpath)
BaselineComparator
Library scope:	test case
Named arguments:	supported
Introduction
Library for comparison of files in different formats.

This library is part of the ${fusionresource}

Shortcuts
Compare Csv Files · Compare Json Data · Compare Json With Baseline File · Compare Xls Files · Compare Xml With Baseline File · Json Inner List Sort · List Baseline Comparator · Xml Sort
Keywords
Keyword	Arguments	Documentation
Compare Csv Files	baseline_file, app_file, delimiter=,, skip_columns_names=None, sort_columns_names=None, key_columns_names=None, number_of_valid_digits=None, delete_files=False	
Compares csv files and copy it to runtime output_dir. By default delimiter is set to ','.

Compare Csv Files	${CURDIR}\\baseline.csv	${CURDIR}\\app.csv	
Compare Csv Files	${CURDIR}\\baseline.csv	${CURDIR}\\app.csv	delimiter=';'
To use skip columns or sort functionalities passing list arguments is required.

Compare Csv Files	${CURDIR}/baseline_key_column.csv	${CURDIR}/app_key_column.csv	sort_columns_names=@{Sort Colums}	
Compare Csv Files	${CURDIR}/baseline_key_column.csv	${CURDIR}/app_key_column.csv	skip_columns_names=@{Skip Colums}	
Compare Csv Files	${CURDIR}/baseline_key_column.csv	${CURDIR}/app_key_column.csv	key_columns_names=@{Key Colums}	
Compare Csv Files	${CURDIR}/baseline_key_column.csv	${CURDIR}/app_key_column.csv	skip_columns_names=@{Skip Colums}	sort_column_names=@{Sort Colums}
Compare Csv Files	${CURDIR}/baseline_key_column.csv	${CURDIR}/app_key_column.csv	skip_columns_names=@{Skip Colums}	sort_column_names=@{Sort Colums}
To delete csv files for every comparison from runtime output_dir, set argument "delete_files=True". By default delete_files functionality is disabled.

Compare Csv Files	${CURDIR}\\baseline.csv	${CURDIR}\\app.csv	delete_files=True
For the current version it is possibly to sort values alphabetically only.

Compare Json Data	data1, data2, output_file=None, is_data1_file=False, is_data2_file=False, ignored_keys=None, nb_of_valid_decimal_places=100	
Compares two jsons. If is_data1_file=True the contents are loaded from file pointed by 'data1'. Otherwise it's treated as JSON string. Same for is_data2_file. Keyword raises error if there are differences in files. output_file parameter is obsolete.

Compare Json With Baseline File	json_baseline_file, json_data, ignored_keys=None, nb_of_valid_decimal_places=100, nb_of_digit_after_decimal=0, wild_card=None	
This keyword is used to compare two json files/ API Response with the baseline json file :param json_baseline_file: Location of the baseline file :param json_data: json content to be compared to baseline file content :param ignored_keys: values of the keys to be ignored in the comparison :param nb_of_valid_decimal_places: comparison of digits after decimal by rounding off the digits example: If the number is 1.567, it will round it off to 1.57 :param nb_of_digit_after_decimal: comparison of digits after decimal in case of numbers :param wild_card: It symbolises the character used in the subset of values to ignore the comparison. Example: If the value is provided with wildcard , i.e *test, it will be ignored If the value is not provided with wildcard *, i.e test, it will be compared

Compare Xls Files	app_file, baseline_file, app_sheet=None, baseline_sheet=None, skip_columns_names=None, sort_data_in_file=False	
Compares 2 different xls or xlsx files or one xls with another xlsx file and generates report in html format.

The features of this keyword are:

Comparison of the content of 2 files. First file being the app file and second one is the baseline file.
Enabled with skipping of multiple columns while comparison.
Data in files could be sorted with parameter 'sort_data_in_file' passed as "True" for comparison.
Comparison report will be shown in the log in the form of html table.
|Arguments|

'app_file' = path of the file to be compared.

'baseline_file' = path of the baseline file.

'app_sheet'[Optional] = Sheet name of the files to be compared. If 'app_sheet' argument value is not provided, by default it will consider the first sheet of the file for comparison.

'baseline_sheet'[Optional] = Sheet name of the baseline file to be compared. If 'baseline_sheet' argument value is not provided, by default it will consider the first sheet of the file for comparison.

'skip_columns_names'[Optional] = Column names to be skipped while comparision. Needs to be passed in the form of a list, see in example. By default the value is set to None.

'sort_data_in_file'[Optional] = Data for both files to be sorted for comparision. Needs to be passed as "True", see in example 5. By default the value is set to "False".

|Example|

1. Compare two xls files.

Compare Xls Files	D:/testExcel/appfile.xls	D:/testExcel/baselinefile.xls
2. Compare two xlsx files.

Compare Xls Files	D:/testExcel/appfile.xlsx	D:/testExcel/baselinefile.xlsx
3. Compare xls file with xlsx file.

Compare Xls Files	D:/testExcel/appfile.xls	D:/testExcel/baselinefile.xlsx
4. Compare two xlsx files with sheet names.

Compare Xls Files	D:/testExcel/appfile.xlsx	D:/testExcel/baselinefile.xlsx	app_sheet=appsheet	baseline_sheet=baselinesheet
5. Compare two xlsx files with Sorting the data.

Compare Xls Files	D:/testExcel/appfile.xlsx	D:/testExcel/baselinefile.xlsx	app_sheet=appsheet	baseline_sheet=baselinesheet	sort_data_in_file= True
6. Compare two xlsx files with skipped column names. * Variables * @{SkipColumns} Column6 Column7

**TestCases**			
Compare Xls Files	D:/testExcel/appfile.xlsx	D:/testExcel/baselinefile.xlsx	skip_columns_names=${SkipColumns}
7. Compare two xlsx files with sheet names and skipped column names. * Variables * @{SkipColumns} Column6 Column7

**TestCases**					
Compare Xls Files	D:/testExcel/appfile.xlsx	D:/testExcel/baselinefile.xlsx	app_sheet=appsheet	baseline_sheet=baselinesheet	skip_columns_names=${SkipColumns}
Compare Xml With Baseline File	baselinexml, responsexml, ignored_keys=None, nb_of_valid_decimal_places=100	
comparison of the content of 2 xmls(baselinexml and responsexml), 1 file is given as baseline and the second one is generated during a test ignored_keys - keys to be ignored in comparison

Json Inner List Sort	json_file, key_to_sort_by, *path_to_list	
Sorting a list by a 'key_to_sort_by'. path_to_the list in the 'json_file' should be given as a list. Example of usage:

${sorted_out}	json inner list sort	unsorted.json	attributes	rows
List Baseline Comparator	locator, baseline_filepath	
Usage
It compares the list creates from the application with the baseline list.

Arguments
'locator' = locator of the list

'baseline_filepath' = Baseline file location

Xml Sort	unsortedxml, sortedxml, sort_key_tag=None, root_xpath=None, reverse=False	
Sorting the xml based on the unique tag and root xpath given

Altogether 8 keywords.
Generated by Libdoc on 2020-02-13 15:01:39.


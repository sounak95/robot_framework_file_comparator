*** Settings ***
Library  BaselineComparator  
Library  OperatingSystem

*** Variables ***
${xls_app_file}    ${CURDIR}\\SampleData\\Sample1.xlsx
${xls_baseline_file}    ${CURDIR}\\SampleData\\Sample2.xlsx
${app_sheetname}    TI_Env
${baseline_sheetname}    TI_Env
${baseline_file}    ${CURDIR}\\SampleData\\baseline_SAR-Der344.csv       
${app_file}    ${CURDIR}\\SampleData\\G.INSIGHT.insight_SAR-Der_SAR-Der.Insight-SAR-Der_SalesActivity.csv    
${delimiter}    ;
@{colums to ignore}    Line Status    Line Modification    Trade ID    RowId
@{key_columns}    Trade Type    Currency    Deal Status    Counterparty    Folder    Block Number
@{columns_to_ignore}    ***quickSearch     ***blockNumber    ***dealNumber    displayId   id  ***fldAllocheadqt    ***localPivotPair    ***splitPivotPair    ***user   ***dealNumberMsg   ***statuses
${baseline_json_file}    ${CURDIR}/SampleData/baseline.json    
${app_json_file}    ${CURDIR}/SampleData/Deal_119_2.json
${key_to_sort}    marketRiskFactorId                    
@{path_to_list}    tradeData    limits    marketLegs    deltas
@{list}    header    pvTicket    GenerationLogs    pvList
@{skip_columns_names}    TI_Username
*** Test Cases ***
Verify XLS Files
    Compare Xls Files    ${xls_app_file}    ${xls_baseline_file}    ${app_sheetname}    ${baseline_sheetname}    skip_columns_names=${skip_columns_names}    sort_data_in_file=True

Verify CSV file comparison based on key column values
    Compare Csv Files    ${baseline_file}    ${app_file}    ${delimiter}    skip_columns_names=${colums_to_ignore}    key_columns_names=${key_columns}

Verify Json comparison with Basefile file
    ${json_data}    Get File    ${CURDIR}\\SampleData\\test4.json 
    Run Keyword And Expect Error    There are differences in files!    Compare Json With Baseline File    ${CURDIR}\\SampleData\\test3.json    ${json_data}    ignored_keys=${columns_to_ignore}    

Verify Json sort and Json Data Comparison
    ${sorted_baseline_json_file}    Json Inner List Sort    ${baseline_json_file}    ${key_to_sort}    @{path_to_list} 
    ${sorted_app_json_file}    Json Inner List Sort    ${app_json_file}    ${key_to_sort}    @{path_to_list} 
    Run Keyword And Expect Error    There are differences in files!    Compare Json Data    ${sorted_baseline_json_file}    ${sorted_app_json_file}  

Verify Xml sort and Xml Comparison
	${newbase}    Xml Sort    ${CURDIR}\\SampleData\\getpv-VAR_BAT_FCP_HS-VAR_BAT_FCP-FCP-1467604965349--4029142841238977192--3101356422395333944.xml    ${CURDIR}\\SampleData\\test1.xml    externalId    .//groups 
	${newoutput}    Xml Sort    ${CURDIR}\\SampleData\\getpv-VAR_BAT_FCP_HS-VAR_BAT_FCP-FCP-1467605361876-8006739874598965733-5313480016454283563.xml    ${CURDIR}\\SampleData\\test2.xml    externalId    .//groups   
	Run Keyword And Expect Error    There are differences in files!    Compare Xml With Baseline File    ${newbase}    ${newoutput}    ignored_keys=${list}
	# Run Keyword And Expect Error    There are differences in files!    Compare Xml With Baseline File    ${newbase}    ${newoutput}    ignored_keys=${list}    nb_of_valid_decimal_places=${0}

Verify Xml Comparison	    
	Run Keyword And Expect Error    There are differences in files!    Compare Xml With Baseline File    ${CURDIR}\\SampleData\\getpv-VAR_BAT_FCP_HS-VAR_BAT_FCP-FCP-1467604965349--4029142841238977192--3101356422395333944.xml    ${CURDIR}\\SampleData\\getpv-VAR_BAT_FCP_HS-VAR_BAT_FCP-FCP-1467605361876-8006739874598965733-5313480016454283563.xml    ignored_keys=${list}    
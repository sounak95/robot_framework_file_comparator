import json
from HttpLibrary import logger
from decimal import Decimal
import HTML_external
import random

def compare_jsons(baseline, result_text, external_ignore_list=None, number_of_valid_decimal_places=100):
    if external_ignore_list is None:
        external_ignore_list = []

    number_of_valid_decimal_places =  int(number_of_valid_decimal_places)

    errors = 0
    ignore_list = []
    ReportHtml = _report_html_update()
    if not valid_json(result_text):
        log_baseline_error("Response content is not a valid JSON document, cannot proceed to with comparison")
        return 0, ""
    result_ref = json.loads(result_text)
    baseline_ref = json.loads(baseline)
    if type(result_ref) is not type(baseline_ref):
        log_baseline_error("JSON structure does not match. Second: ["+str(type(result_ref))+"] - first: ["+str(type(baseline_ref))+"]")
        return 0, ""
    add_to_ignore_list(external_ignore_list, ignore_list)

    if type(result_ref) is list:
        errors = array_compare(result_ref, baseline_ref, "", ignore_list, number_of_valid_decimal_places)
    elif type(result_ref) is dict:
        errors = hash_compare(result_ref, baseline_ref, "", ignore_list, number_of_valid_decimal_places)
    else:
        log_baseline_error("Could not determine JSON base object type, cannot proceed")
        return 0, ""
    json_text = json.dumps(result_ref, indent=1)
    if errors > 0:
        log_baseline_error("number of difference found: "+str(errors))
        logger.info('<font color=red>' + 'Below are the Differences in files:' + '</font>', html=True)
        logger.info(ReportHtml, html=True)
        return 0, json_text
    else:
        log_info("Result matches the baseline")
        return 1, json_text
    
def array_compare(array, baseline, path="", ignore_list=None, number_of_valid_decimal_places=100, number_of_digit_after_decimal=0, baseline_key=None, flag_ignore_character=None):
    if ignore_list is None:
        ignore_list = []
    error = 0
    size_error=0

    for index in range(len(baseline)):
        cur_type = type(baseline[index])
        if index<(len(array)):
            if cur_type is list:
                error = error + array_compare(array[index], baseline[index], path+"["+str(index)+"]", ignore_list, number_of_valid_decimal_places, number_of_digit_after_decimal, baseline_key, flag_ignore_character)

            elif cur_type is dict:
                error = error + hash_compare(array[index], baseline[index], path+"["+str(index)+"]", ignore_list, number_of_valid_decimal_places, number_of_digit_after_decimal, flag_ignore_character)

            else:
                error1, array[index] = txt_value_compare(array[index], baseline[index], path+"["+str(index)+"]", number_of_valid_decimal_places, number_of_digit_after_decimal, baseline_key, flag_ignore_character)
                error = error + error1
        else:
            array.append(baseline[index])
            paint_red(array[-1])
            error +=1
            size_error = -1
    for index in range(len(baseline), len(array)):
        paint_red(array[index])
        error +=1
        size_error = 1
    if size_error == -1:
        randomvalue = random.sample(list(range(1, 10000)), 1)
        value = "<a name=exactplace{}> <font color=red > {} is missing in Test Output Array </font></a>".format(randomvalue, baseline[index])
        array.append(value)
        _update_table(missing=baseline[index], randomvalue=randomvalue)
    elif size_error == 1:
        randomvalue = random.sample(list(range(1, 10000)), 1)
        value = "<a name=exactplace{}> <font color=red > {} is additional in Test Output Array </font></a>".format(randomvalue, array[index])
        array.append(value)
        _update_table(additional=array[index], randomvalue=randomvalue)

    return error

def hash_compare(hash, baseline, path="", ignore_list=None, number_of_valid_decimal_places=100, number_of_digit_after_decimal=0,flag_ignore_character=None):
    if ignore_list is None:
        ignore_list = []
    error = 0
    size_error=0
    already_tested = []
    
    if 'ignoreList' in baseline:
        add_to_ignore_list(baseline['ignoreList'], ignore_list)
        del baseline['ignoreList']

    if 'innerJSON' in baseline:
        extract_inner_JSON(hash, baseline)
        del baseline['innerJSON']
        
    for baseline_key in baseline:
        if baseline_key not in ignore_list and baseline_key != "ignoreList" and baseline_key != "innerJSON":
            if not baseline_key in hash:
                randomvalue = random.sample(list(range(1, 10000)), 1)
                error_key = "<a name=exactplace{}> <font color=red> {} - Not found in test output</font> </a>".format(randomvalue, baseline_key)
                hash[error_key] = baseline[baseline_key]
                paint_red(hash[error_key])
                _update_table(missing=baseline_key, randomvalue=randomvalue)
                already_tested.append(error_key)
                error = error + 1
            elif type(hash[baseline_key]) != type(baseline[baseline_key]) and not (isinstance(hash[baseline_key], (int, float)) and isinstance(baseline[baseline_key], (int, float))):
                randomvalue = random.sample(list(range(1, 10000)), 1)
                error_key = "<a name=exactplace{}> <font color=red> {} - Content mismatch. EXPECTED: {} got {} </font> </a>".format(randomvalue, baseline_key, str(type(hash[baseline_key])), str(type(baseline[baseline_key])))
                hash[error_key] = baseline[baseline_key]
                paint_red(hash[error_key])
                _update_table(missing=baseline_key, randomvalue=randomvalue)
                already_tested.append(error_key)
                error = error + 1
            else:
                c_type = type(baseline[baseline_key])
                if c_type is list:
                    error = error + array_compare(hash[baseline_key], baseline[baseline_key], path+"{"+str(baseline_key)+"}", ignore_list, number_of_valid_decimal_places, number_of_digit_after_decimal, baseline_key, flag_ignore_character)

                elif c_type is dict:
                    error = error + hash_compare(hash[baseline_key], baseline[baseline_key], path+"{"+str(baseline_key)+"}", ignore_list, number_of_valid_decimal_places, number_of_digit_after_decimal, flag_ignore_character)

                else:
                    error1, hash[baseline_key] = txt_value_compare(hash[baseline_key], baseline[baseline_key], path+"{"+str(baseline_key)+"}", number_of_valid_decimal_places, number_of_digit_after_decimal, baseline_key, flag_ignore_character)

                    error = error + error1

        already_tested.append(baseline_key)
    # Also check result hash for keys that might not be in the baseline hash
    # Maybe could be improved
    l = []
    for hash_key in hash:
        if hash_key not in already_tested and hash_key not in ignore_list and hash_key not in l:
            randomvalue = random.sample(list(range(1, 10000)), 1)
            k = "<a name=exactplace{}> <font color=red> {} - Not in the baseline</font> </a>".format(randomvalue, hash_key)
            hash[k] = hash[hash_key]
            _update_table(additional=hash_key, randomvalue=randomvalue)
            paint_red(hash[k])
            l.append(k)
            del hash[hash_key]
            error = error + 1
    return error

def extract_inner_JSON(hash, baseline):
    for key in baseline['innerJSON']:
        if key in baseline and key in hash:
            if type(baseline[key]) is not list and type(baseline[key]) is not dict:
                if not valid_json(baseline[key]):
                    log_error("baseline inner json is not valid")
                    return 0
                baseline[key]=json.loads(baseline[key])
                log_info("Content of ["+key+"] field in the baseline has been converted from text to JSON for comparison purpose")

            if type(hash[key]) is list or type(hash[key]) is dict:
                log_warning("Content of ["+key+"] in the response seems to be json data already, do nothing")
            else:
                if not valid_json(hash[key]):
                    log_error("test output inner json is not valid")
                    return 0
                hash[key]=json.loads(hash[key])
                log_info("Content of ["+key+"] field in the response as been converted from text to JSON for comparison purpose")
        else:
            log_error("["+key+"] field was given to be treated as JSON data for comparison but is missing from either the baseline or the result file")


def add_to_ignore_list(new_items, ignore_list):
    if type(new_items) is list:
        for item in new_items:
            if not item in ignore_list:
                ignore_list.append(item)
                log_info("["+str(item)+"] was added to the list of fields to be ignored during comparison")
    else:
        ignore_list.append(new_items)


def paint_red(obj):    
    if type(obj) is dict:
        for key in obj:
            if not obj[key]:
                obj[key]=""
            error_key = '<font color=red>'+str(key)+'</font>'
            obj[error_key] = obj[key]
            
            if type(obj[error_key]) is dict: 
                paint_red(obj[error_key])
            elif type(obj[error_key]) is list:
                paint_red(obj[error_key])
            else:
                obj[error_key] = '<font color=red>'+str(obj[error_key])+'</font>'
            del obj[key]
    elif type(obj) is list:
        for index in range(len(obj)):
            if type(obj[index]) is dict: 
                paint_red(obj[index])
            elif type(obj[index]) is list:
                paint_red(obj[index])
            else:
                obj[index] = '<font color=red>'+str(obj[index])+'</font>'
    return 1

def CMF_baseline_compare(baseline, result_text, external_ignore_list=None, number_of_valid_decimal_places=100, number_of_digit_after_decimal=0, wild_card=None):
    global wild_card_character
    global flag_ignore_character
    wild_card_character = wild_card
    if wild_card_character!=None:
        flag_ignore_character = wild_card_character
    else:
        flag_ignore_character = None
    if external_ignore_list is None:
        external_ignore_list = []
    number_of_valid_decimal_places = int(number_of_valid_decimal_places)
    number_of_digit_after_decimal = int(number_of_digit_after_decimal)
    errors = 0
    ignore_list = []
    
    log_info("Comparing testcase output to the baseline")
    
    if not valid_json(result_text):
        log_baseline_error("Response content is not a valid JSON document, cannot proceed to baseline comparison")
        log_baseline_error("Response content: " + str(result_text))
        return 0, ""
    ReportHtml = _report_html_update()

    result_ref = json.loads(result_text)
    baseline_ref = json.load(baseline)
    if type(result_ref) is not type(baseline_ref):
        log_baseline_error("JSON structure does not match. result: ["+str(type(result_ref))+"] - baseline: ["+str(type(baseline_ref))+"]")
        return 0, ""
    add_to_ignore_list(external_ignore_list, ignore_list)


    if type(result_ref) is list:
        errors = array_compare(result_ref, baseline_ref, "", ignore_list, number_of_valid_decimal_places, number_of_digit_after_decimal, flag_ignore_character)
    elif type(result_ref) is dict:
        errors = hash_compare(result_ref, baseline_ref, "", ignore_list, number_of_valid_decimal_places, number_of_digit_after_decimal, flag_ignore_character)
    else:
        log_baseline_error("Could not determine JSON base object type, cannot proceed")
        return 0, ""
    json_text = json.dumps(result_ref, indent=1)
    if errors > 0:
        logger.error("number of difference found: "+ str(errors))
        logger.info('<font color=red>' + 'Below are the Differences in files:' + '</font>', html=True)
        logger.info(ReportHtml, html=True)
        return 0, json_text
    else:
        log_info("Result matches the baseline")
        return 1, json_text

def log_error(error):
    logger.error(error)
    
def log_baseline_error(error):
    logger.error(error)
    
def log_info(info):
    logger.write(info)


def log_warning(warning):
    logger.warn(warning)


def valid_json(my_json):
    try:
        json.loads(my_json)
    except:
        log_error(str(my_json) + ' is not a valid json')
        return False
    return True

def _is_number(s):
    try:
        float(str(s))
        return True
    except ValueError:
        return False


def txt_value_compare(value, baseline, path, number_of_valid_digits=100, number_of_digit_after_decimal=0, somekey=None, flag_ignore_character=None):
    if _is_number(value) and _is_number(baseline):
        return numeric_value_compare(value, baseline, path, number_of_valid_digits, number_of_digit_after_decimal, somekey)
    elif flag_ignore_character!=None:
        if wild_card_character in baseline and value != baseline:
            return 0, value
        elif value != baseline:
            randomvalue = random.sample(range(1, 10000), 1)
            _update_table(somekey=somekey, value=value, baseline=baseline, randomvalue=randomvalue)
            value = "<a name=exactplace{}><font color=red > {}  - EXPECTED:  {} </font></a>".format(randomvalue, repr(value), repr(baseline))
            return 1, value
    elif value != baseline:
        randomvalue = random.sample(list(range(1, 10000)), 1)
        _update_table(somekey=somekey, value=value, baseline=baseline, randomvalue=randomvalue)
        value = "<a name=exactplace{}><font color=red > {}  - EXPECTED:  {} </font></a>".format(randomvalue, repr(value), repr(baseline))
        return 1, value
    return 0, value


def numeric_value_compare(value, baseline, path, number_of_valid_digits=100, number_of_digit_after_decimal=0, somekey=None):
    not_equal = False
    if value != baseline:
        if number_of_digit_after_decimal > 0:
            if type(value) is float and type(baseline) is float:
                if number_truncate(repr(value), number_of_digit_after_decimal) != number_truncate(repr(baseline), number_of_digit_after_decimal):
                    not_equal = True
        elif str(round(float(value), number_of_valid_digits) - round(float(baseline), number_of_valid_digits)) == "nan":
            not_equal = True
        else:
            if abs(round(float(value), number_of_valid_digits)-round(float(baseline), number_of_valid_digits)) > 0:
                not_equal = True
        if not_equal:
            randomvalue = random.sample(list(range(1, 10000)), 1)
            _update_table(somekey=somekey, value=value, baseline=baseline, randomvalue=randomvalue)
            value = "<a name=exactplace{}><font color=red > {}  - EXPECTED:  {} </font></a>".format(randomvalue, repr(value), repr(baseline))
            return 1, value
        else:
            return 0, value
    else:
        return 0, value

def _update_table(somekey=" - ", value=" - ", baseline=" - ", missing=" - ", additional=" - ", randomvalue=" - "):
    ReportHtml.rows.append(
        [HTML_external.HTML_external.TableCell(str(somekey), bgcolor=cellcolor),
         HTML_external.HTML_external.TableCell(str(baseline), bgcolor=cellcolor),
         HTML_external.HTML_external.TableCell(str(value), bgcolor=cellcolor),
         HTML_external.HTML_external.TableCell(str(missing), bgcolor=cellcolor),
         HTML_external.HTML_external.TableCell(str(additional), bgcolor=cellcolor),
         HTML_external.HTML_external.TableCell('<a href="#exactplace{}">{}</a>'.format(randomvalue, 'ErrorMessage'), bgcolor=cellcolor)])

def number_truncate(number, number_of_digit_after_decimal):
    # work fine upto 9th point after decimal
    point = abs(Decimal(number).as_tuple().exponent)
    if point >= number_of_digit_after_decimal:
        s = repr(number)
        i, p, d = s.partition('.')
        return ('.'.join([i, (d+'0'*number_of_digit_after_decimal)[:number_of_digit_after_decimal]])).replace("'","")
    else:
        return number

def _report_html_update():
    TableHeaderColor = "LightCoral"
    global cellcolor
    cellcolor = "white"
    global ReportHtml
    ReportHtml = HTML_external.HTML_external.Table()
    ReportHtml.rows.append([HTML_external.HTML_external.TableCell('Field Name', bgcolor=TableHeaderColor, header=True),
                            HTML_external.HTML_external.TableCell('Expected Value', bgcolor=TableHeaderColor, header=True),
                            HTML_external.HTML_external.TableCell('Actual Value', bgcolor=TableHeaderColor, header=True),
                            HTML_external.HTML_external.TableCell('Missing Value', bgcolor=TableHeaderColor, header=True),
                            HTML_external.HTML_external.TableCell('Additional Value', bgcolor=TableHeaderColor, header=True),
                            HTML_external.HTML_external.TableCell('Error Link', bgcolor=TableHeaderColor, header=True)])
    return ReportHtml

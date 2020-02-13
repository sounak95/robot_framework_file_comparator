import re
import json
import xml.etree.ElementTree as ET
from Libraries.Common.BaselineComparator.json_comparator import hash_compare,array_compare,log_baseline_error,log_info,add_to_ignore_list, _report_html_update
from lxml import etree
from HttpLibrary import logger
class XmlDictObject(dict):
    """
    Adds object like functionality to the standard dictionary.
    """

    def __init__(self, initdict=None):
        if initdict is None:
            initdict = {}
        dict.__init__(self, initdict)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __setattr__(self, item, value):
        self.__setitem__(item, value)

    def __str__(self):
        if '_text' in self:
            return self.__getitem__('_text')
        else:
            return ''

    @staticmethod
    def Wrap(x):
        """
        Static method to wrap a dictionary recursively as an XmlDictObject
        """

        if isinstance(x, dict):
            return XmlDictObject((k, XmlDictObject.Wrap(v)) for (k, v) in list(x.items()))
        elif isinstance(x, list):
            return [XmlDictObject.Wrap(v) for v in x]
        else:
            return x

    @staticmethod
    def _UnWrap(x):
        if isinstance(x, dict):
            return dict((k, XmlDictObject._UnWrap(v)) for (k, v) in list(x.items()))
        elif isinstance(x, list):
            return [XmlDictObject._UnWrap(v) for v in x]
        else:
            return x

    def UnWrap(self):
        """
        Recursively converts an XmlDictObject to a standard dictionary and returns the result.
        """

        return XmlDictObject._UnWrap(self)

def _ConvertXmlToDictRecurse(node, dictclass):
    nodedict = dictclass()

    if len(list(node.items())) > 0:
        # if we have attributes, set them
        nodedict.update(dict(list(node.items())))

    for child in node:
        # recursively add the element's children
        newitem = _ConvertXmlToDictRecurse(child, dictclass)
        if child.tag in nodedict:
            # found duplicate tag, force a list
            if type(nodedict[child.tag]) is type([]):
                # append to existing list
                nodedict[child.tag].append(newitem)
            else:
                # convert to list
                nodedict[child.tag] = [nodedict[child.tag], newitem]
        else:
            # only one, directly set the dictionary
            nodedict[child.tag] = newitem

    if node.text is None:
        text = ''
    else:
        text = node.text.strip()

    if len(nodedict) > 0:
        # if we have a dictionary add the text as a dictionary value (if there is any)
        if len(text) > 0:
            nodedict['_text'] = text
    else:
        # if we don't have child nodes or attributes, just set the text
        nodedict = text

    return nodedict

def ConvertXmlToDict(root, dictclass=XmlDictObject):
    """
    Converts an XML file or ElementTree Element to a dictionary
    """

    # If a string is passed in, try to open it as a file
    if type(root) == type(''):
        root = ET.parse(root).getroot()
    elif not isinstance(root, ET.Element):
        raise TypeError('Expected ElementTree.Element or file path string')

    return dictclass({root.tag: _ConvertXmlToDictRecurse(root, dictclass)})

def _get_and_print_key(elem,sort_key_tag_name=None):
    return elem.findtext(sort_key_tag_name)

def getkey(elem,sort_key_tag_name=None):
    pattern = ["[","]","/","_","-","\\"]
    checktype = str(elem.findtext(sort_key_tag_name))
    if checktype.isdigit():
        return int(checktype)
    elif _check_pattern(pattern,checktype):
        strlen = re.split("[/_)(]+", checktype)
        if len(strlen)>1:
            for i in strlen:
                if i.isdigit():
                    return int(i.lower())
            return checktype
    else:
        return checktype

def _check_pattern(pattern,data):
    for d in data:
        if d in pattern:
            return True
    return False

def sort_xml(unsorted_file,sorted_file,sort_key_tag=None, xpath=None,reverse=False):
    """Sort unsorted xml file and save to sorted_file"""
    tree = ET.parse(unsorted_file)
    container = tree.find(str.strip(str(xpath)))
    container[:] = sorted(container, key=lambda child: getkey(child, sort_key_tag_name=str(sort_key_tag)), reverse=False)
    tree.write(sorted_file)
    return sorted_file


def sort_HTML(unsorted_file, sorted_file, sort_key_tag_name=None, xpath=None, attr=None):
    """Sort unsorted html file and save to sorted_file"""
    parser = etree.HTMLParser()
    tree = etree.parse(unsorted_file, parser)
    container = tree.find(str.strip(xpath))
    container[:] = sorted(container, key=lambda child: _get_and_print_key(child, sort_key_tag_name=sort_key_tag_name), reverse=False)
    container[:] = sorted(container, key=lambda child: _get_and_print_key(child, sort_key_tag_name=sort_key_tag_name), reverse=False)
    tree.write(sorted_file)
    return container

def compare_xml(baseline_xml, actual_xml, external_ignore_list=None, number_of_valid_decimal_places=100):
    """compares two xmls"""
    if external_ignore_list is None:
        external_ignore_list = []

    number_of_valid_decimal_places =  int(number_of_valid_decimal_places)

    errors = 0
    ignore_list = []
    log_info(baseline_xml)
    log_info(actual_xml)
    log_info("Comparing two xmls")
    baseline_ref = XmlDictObject.UnWrap(ConvertXmlToDict(str(baseline_xml)))
    result_ref = XmlDictObject.UnWrap(ConvertXmlToDict(str(actual_xml)))
    ReportHtml = _report_html_update()
    if type(result_ref) is not type(baseline_ref):
        log_baseline_error("xml structure does not match. Second: ["+str(type(result_ref))+"] - first: ["+str(type(baseline_ref))+"]")
        return 0, ""
    add_to_ignore_list(external_ignore_list, ignore_list)

    if type(baseline_ref) is list:
        errors = array_compare(result_ref, baseline_ref, "", ignore_list, number_of_valid_decimal_places)
    elif type(result_ref) is dict:
        errors = hash_compare(result_ref, baseline_ref, "", ignore_list, number_of_valid_decimal_places)
    else:
        log_baseline_error("Could not determine xml base object type, cannot proceed")
        return 0, ""
    json_text = json.dumps(result_ref, indent=1)
    print(("*HTML*" + json_text))
    if errors > 0:
        log_baseline_error("number of difference found: "+str(errors))
        logger.info('<font color=red>' + 'Below are the Differences in files:' + '</font>', html=True)
        logger.info(ReportHtml, html=True)
        return 0, json_text

    else:
        log_info("Result matches the baseline")
        return 1, json_text
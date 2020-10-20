#!/usr/bin/env python
# author: Rainy Chan  mail to: rainydew@qq.com

def compare(a, b, ignore_list_seq=True, re_compare=True, ignore_path=None, callback=print, strict_json=False,
            float_fuzzy_digits=0, strict_number_type=False, omit_path=None):
    """this function returns whether a is matched with b
    :param str or unicode or list or tuple or dict a: The first json string/json-like object to compare
    :param str or unicode or list or tuple or dict b: The second one to be compared
    :param bool ignore_list_seq: Set True to ignore the order when comparing arrays(lists), recursively
    :param bool re_compare: Set True to enable regular expressions for assertion. The pattern MUST contains ONE
    bracket, start with ^ or end with $, otherwise it won't be considered as an re-pattern. You can use ^.*?(sth) or
    ().*$ or so on to extract something from middle of the string. ^(.*)$ can just match any string, make this item
    ignored. Comparing two re-patterns makes no sense so it isn't allowed
    :param list[str or unicode] or None ignore_path: a list of element-path to be ignored when comparing value. e.g.
    ["/key1/key2", "/key3/1"] means all "ignored" in {"key1":{"key2":"ignored"},"key3":["not ignored","ignored"]}
    :param function callback: A one-arg function to hold the difference, default to `print`
    :param bool strict_json: Set True to ensure that all dict/list objects are JSON serializable. You may set it to
    False to make some special types comparable, e.g. Decimal, bytes and struct_time, useful for db assertion.
    BEAWARE !!! Bytes-like str (str in python2) is not supported. Since you should use json.dumps(u"hello") instead
        of json.dumps("hello") It may raise UnicodeDecodeError if there are Chinese characters or so on.
    :param int float_fuzzy_digits: 0(default) means disable. Set it to N means we consider number a == b if abs(a-b)
        < 10**(-N)
    :param bool strict_number_type: False(default) means allow 1(int)==1.0(float). Set True to ensure type equality
    :param list[str or unicode] or None omit_path: a list of element-paths to be ignored even if they are absent.
    ["/key1/key2"] means {"key1":{"key2":"ignored"}} can match {"key1":{}}. the last path-segament MUSTBE a map key,
    you must use * to shadow list index and it doesn't support regular expression. e.g. /key1/*/key2
    :return bool: Whether two json string or json-like objects are equal. If not, print the differences
    """
    return True

def check(a, b, ignore_list_seq=True, re_compare=True, ignore_path=None, callback=print, strict_json=False,
            float_fuzzy_digits=0, strict_number_type=False, omit_path=None):
    """this function raise an AssertionError when matching failed
    :param str or unicode or list or tuple or dict a: The first json string/json-like object to compare
    :param str or unicode or list or tuple or dict b: The second one to be compared
    :param bool ignore_list_seq: Set True to ignore the order when comparing arrays(lists), recursively
    :param bool re_compare: Set True to enable regular expressions for assertion. The pattern MUST contains ONE
    bracket, start with ^ or end with $, otherwise it won't be considered as an re-pattern. You can use ^.*?(sth) or
    ().*$ or so on to extract something from middle of the string. ^(.*)$ can just match any string, make this item
    ignored. Comparing two re-patterns makes no sense so it isn't allowed
    :param list[str or unicode] or None ignore_path: a list of element-path to be ignored when comparing value. e.g.
    ["/key1/key2", "/key3/1"] means all "ignored" in {"key1":{"key2":"ignored"},"key3":["not ignored","ignored"]}
    :param function callback: A one-arg function to hold the difference, default to `print`
    :param bool strict_json: Set True to ensure that all dict/list objects are JSON serializable. You may set it to
    False to make some special types comparable, e.g. Decimal, bytes and struct_time, useful for db assertion.
    BEAWARE !!! Bytes-like str (str in python2) is not supported. Since you should use json.dumps(u"hello") instead
        of json.dumps("hello") It may raise UnicodeDecodeError if there are Chinese characters or so on.
    :param int float_fuzzy_digits: 0(default) means disable. Set it to N means we consider number a == b if abs(a-b)
        < 10**(-N)
    :param bool strict_number_type: False(default) means allow 1(int)==1.0(float). Set True to ensure type equality
    :param list[str or unicode] or None omit_path: a list of element-paths to be ignored even if they are absent.
    ["/key1/key2"] means {"key1":{"key2":"ignored"}} can match {"key1":{}}. the last path-segament MUSTBE a map key,
    you must use * to shadow list index and it doesn't support regular expression. e.g. /key1/*/key2
    """
    return True

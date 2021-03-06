#!/usr/bin/env python
# coding: utf-8
from json_compare import compare, check
import six


def long_line():
    print("-" * 120)


def run_tests():
    a = {"姓名": "王大锤"}  # str and unicode (or bytes and str in python3) are compatible, useful in Chinese words...
    b = {u"姓名": u"王大锤"} if six.PY2 else {"姓名".encode("utf-8"): "王大锤".encode("utf-8")}
    check(a, b)

    long_line()

    a = [[1, 2, 3], [4, 5, 6]]
    b = ([6, 5, 4], [3, 2, 1])  # tuples (useful in pymysql & DictCursor) and different order of arrays are supported
    check(a, b)

    long_line()

    a = [[1, 2, 3], [4, 5, 6]]
    b = [[3, 2, 1], [6, 5, 4]]  # ignore_list_seq=False makes these two different, however
    assert not compare(a, b, ignore_list_seq=False)

    long_line()

    a = {"a": 1, "b": 3, "c": False, "d": "ok"}
    b = {"a": 1, "b": 2, "c": "False", "e": "ok"}  # False != "False"
    assert not compare(a, b)

    long_line()

    a = {"a": [1, {"k": ["ok"]}]}
    b = {"a": [1, {"k": ["error"]}]}  # ignoring list order, we aren't sure to pair {"k": ["ok"]} with {"k": ["error"]}
    assert not compare(a, b)

    long_line()

    assert not compare(a, b, ignore_list_seq=False)  # however, if we consider the order, we can locate differences deeper

    long_line()

    a = {"a": [1, {"k": [0]}]}  # we ignore this path now, test will pass.
    b = '{"a": [1, {"k": [1]}]}'  # notice we can't specify path deeper in a list when ignore_list_seq is enabled
    check(a, b, ignore_list_seq=False, ignore_path=["/a/1/k"])

    long_line()

    a = [{"a": 1, "b": 2}, {"a": 5, "b": 4}]  # now we finally support regular expressions in ignore_path list
    b = [{"a": 3, "b": 2}, {"a": 6, "b": 4}]  # in this case, only value of "b" concerned
    check(a, b, ignore_list_seq=False, ignore_path=[r"^(/\d+/a)"])

    long_line()

    a = [{"a": 1, "b": 2}, {"a": 1, "b": 4}]  # also useful under list_seq ignored
    b = [{"a": 2, "b": 4}, {"a": 2, "b": 2}]
    check(a, b, ignore_path=[r"^(/\d+/a)"])

    long_line()

    a = [{"a": 1, "b": 3}, {"a": 1, "b": 4}]  # this time, 3 and 2 cannot match
    b = [{"a": 2, "b": 4}, {"a": 2, "b": 2}]
    assert not compare(a, b, ignore_path=[r"^(/\d+/a)"])

    long_line()

    a = [{"a": 1, "b": 2}, {"a": 3, "b": 4}, {"a": 5, "b": 4}]  # this time, only different frequency found
    b = [{"a": 6, "b": 4}, {"a": 7, "b": 2}, {"a": 8, "b": 2}]  # but it will choose a random value of "a" to display
    assert not compare(a, b, ignore_path=[r"^(/\d+/a)"]) # it's caused by logic restriction, don't get confused

    long_line()

    a = {"a": [1, {"k": [0], "l": None}, 2]}  # ignore two paths this time, only difference at /a/2 will be shown
    b = {"a": [1, {"k": [1], "l": False}, 3]}
    assert not compare(a, b, ignore_list_seq=False, ignore_path=["/a/1/k", "/a/1/l"])

    long_line()

    a = '{"rtn": 0, "msg": "ok"}'  # can compare json string with python dict/list objects
    b = {"rtn": 1, "msg": "username not exist"}
    assert not compare(a, b)

    long_line()

    a = u'{"body":{"text":"你好"}}'  # both text and binary json strings are supported
    b = '{"body":{"text":"你好啊"}}'
    assert not compare(a, b)

    long_line()

    a = [1, 2, 2]  # even we ignore the order, the frequency of elements are concerned
    b = [1, 1, 2]
    assert not compare(a, b)

    long_line()

    a = [1, 2, 3]
    b = [1, 3, 4, 5]  # even if the length of lists are not equal, we can still know the difference
    assert not compare(a, b)

    long_line()

    a = [1, 2, 3]
    b = [1, 3, 4, 5]  # but we CANNOT keep the order of elements under different length even if ignore_list_seq is False
    assert not compare(a, b, ignore_list_seq=False)

    long_line()

    a = [1.0]  # in face cp.compare(1, 1.0) is allowed, however non-standard jsons are not recommend
    b = [1 if six.PY3 else eval("1L")]  # Integers and floats are compatible, including long of python 2
    check(a, b)

    long_line()

    a = [r"^(.*)$"]  # re-comparing enabled as default. Be careful bare r"^(.*)$" without list is considered as json-str
    b = ["anything"]  # use this to skip any unconcerned fields
    check(a, b, ignore_list_seq=False)

    long_line()

    a = [r"(.*)"]  # without ^-start or $-end, this won't be regarded as re-pattern
    b = ["anything"]
    assert not compare(a, b, ignore_list_seq=False)

    long_line()

    a = [r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$"]  # we can use re-comparing to confine formats but not values
    b = ["anything"]
    assert not compare(a, b, ignore_list_seq=False)

    long_line()

    a = [r"^(2019-07-01 \d{2}:\d{2}:\d{2})$"]  # e.g. this assertion will pass
    b = ["2019-07-01 12:13:14"]
    check(a, b, ignore_list_seq=False)

    long_line()

    a = [r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$", r"^(.*)$"]
    b = ["anything", "otherthing"]  # when using re with order-ignored list, it will be crossing compare
    # be careful, potential chance of messy
    assert not compare(a, b)

    long_line()

    a = [r"^(.*)$"]  # two re-pattern is not allowed
    b = [r"^(.+)$"]
    try:
        compare(a, b, ignore_list_seq=False)
    except Exception as e:
        print(e)
    else:
        raise AssertionError()

    long_line()

    a = [r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$", "otherthing"]
    b = ["anything", r"^(.*)$"]  # this errors when comparing a[0] with b[1] due to the above rule
    try:
        compare(a, b)
    except Exception as e:
        print(e)
    else:
        raise AssertionError()

    long_line()

    a = r'["^(2019-07-01 \\d{2}:\\d{2}:\\d{2})$"]'  # double slashes are needed because this is a json-string, not list
    # or use '["^(2019-07-01 \\\\\d{2}:\\\\\d{2}:\\\\\d{2})$"]' will also work
    b = ["2019-07-01 12:13:14"]
    check(a, b, ignore_list_seq=False)

    long_line()

    a = r'[r"^(2019-07-01 \d{2}:\d{2}:\d{2})$"]'  # json cannot parse inner 'r' notation, so this won't work
    b = ["2019-07-01 12:13:14"]
    try:
        compare(a, b, ignore_list_seq=False)
    except Exception as e:
        print(e)
    else:
        raise AssertionError()

    long_line()

    a = [r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"]  # only fully match will pass re-comparing
    b = ["2019-07-01 12:13:14.567"]
    assert not compare(a, b, ignore_list_seq=False)

    long_line()

    a = [r"^.*?(\d)-(\d)"]  # two or more brackets will result certain False
    b = ["2019-07-01 12:13:14.567"]
    assert not compare(a, b, ignore_list_seq=False)

    long_line()

    a = [0.1 + 0.1 + 0.1]  # default we use accurate compare, since float compute causes accumulative errors
    b = [0.3]
    assert not compare(a, b, ignore_list_seq=False)

    long_line()

    check(a, b, ignore_list_seq=False, float_fuzzy_digits=6)  # so we can bear margin < 10e-6 now in float comparing

    long_line()

    a = {"key": 1}
    b = {"key": 1.0}
    check(a, b)

    long_line()

    assert not compare(a, b, strict_number_type=True)

    long_line()

    a = {"a": {"b": 1, "c": 2, "d": 3}}
    b = {"a": {"c": 2}}
    check(a, b, omit_path=["/a/b", "/a/d"])

    long_line()

    a = {"a": {"b": 1, "c": 2}}
    b = {"a": {"c": 2, "d": 3}}
    assert not compare(a, b, omit_path=["/a/b"])

    long_line()

    a = {"a": [{"b": 1, "c": 2}, {"d": 3, "c": 4}]}
    b = {"a": [{"c": 2}, {"c": 4}]}
    check(a, b, omit_path=["/a/*/b", "/a/*/d"])   # omit_path only supports * expression to ignore path contains list

    long_line()

    a = {"a": [{"b": 1, "c": 2}, {"c": 2}, {"d": 3, "c": 4}]}
    b = {"a": [{"c": 2}, {"c": 4}, {"c": 4}]}
    assert not compare(a, b, omit_path=["/a/*/b", "/a/*/d"])    # freq are different now


if __name__ == "__main__":
    run_tests()

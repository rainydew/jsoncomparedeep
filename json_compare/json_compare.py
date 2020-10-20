#!/usr/bin/env python
# coding: utf-8
# author: Rainy Chan rainydew@qq.com
# platform: python 2.6-2.7, 3.5-3.8+
# demos are provided in test_json_compare.py
# version: 1.19
from __future__ import print_function
import json
import re
import traceback
import six
import codecs

_NUMBER_TYPES = list(six.integer_types) + [float]


class _Compare(object):
    def __init__(self):
        self._float_fuzzy_digits = None
        self._strict_number_type = None
        self._res = None
        self._ignore_list_seq = None
        self._re_compare = True
        self._ignore_path = None
        self._omit_path = None
        self._handle = None

    @staticmethod
    def _tuple_append(t, i):
        return tuple(list(t) + [six.text_type(i)])

    @staticmethod
    def _to_unicode_if_string(strlike):
        if type(strlike) == six.binary_type:
            try:
                return strlike.decode('utf-8')
            except UnicodeDecodeError:
                raise ValueError("decoding string {} failed, may be local encoded".format(repr(strlike)))
        else:
            return strlike

    @staticmethod
    def _to_list_if_tuple(listlike):
        if type(listlike) == tuple:
            return list(listlike)
        else:
            return listlike

    def _common_warp(self, anylike):
        return self._to_list_if_tuple(self._to_unicode_if_string(anylike))

    def _fuzzy_float_equal(self, a, b):
        if self._float_fuzzy_digits:
            return abs(a - b) < 10 ** (-self._float_fuzzy_digits)
        else:
            return a == b

    @staticmethod
    def _modify_a_key(dic, from_key, to_key):
        assert not any([type(to_key) == type(exist_key) and to_key == exist_key for exist_key in
                        dic.keys()]), 'cannot change the key due to key conflicts'
        # cannot use IN here `to_key in dic.keys()`, because u"a" in ["a"] == True
        dic[to_key] = dic.pop(from_key)

    def _fuzzy_number_type(self, value):
        if not self._strict_number_type:
            type_dict = {x: float for x in six.integer_types}
        else:
            type_dict = {x: int for x in six.integer_types}
        res = type(value)
        return type_dict.get(res, res)

    def _turn_dict_keys_to_unicode(self, dic):
        keys = dic.keys()
        modifiers = []
        for key in keys:  # a.keys() returns a constant, so it is safe because ak won't change
            if type(key) == six.binary_type:
                modifiers.append((key, self._to_unicode_if_string(key)))
            else:
                assert type(key) == six.text_type, 'key {} must be string or unicode in dict {}'.format(key, dic)

        for from_key, to_key in modifiers:
            self._modify_a_key(dic, from_key, to_key)

    def _set_false(self):
        self._res = False

    @staticmethod
    def _escape(s):
        """
        :param s: binary if py2 else unicode
        :return:
        """
        if r'\x' in s:
            s = s.decode('string-escape') if six.PY2 else codecs.escape_decode(s)[0].decode('utf-8')  # no string-escape
        if r'\u' in s:
            s = s.decode('unicode-escape') if six.PY2 else s.encode().decode('unicode-escape')
        if type(s) == six.binary_type:
            s = s.decode('utf-8')  # This often comes from unix servers
        return s

    # difference_print methods
    def _different_type(self, a, b, root):
        self._set_false()
        self._handle("different type at /{}".format("/".join(root)))
        self._handle("a {}: ".format(type(a)) + repr(a))
        self._handle("b {}: ".format(type(b)) + repr(b))

    def _different_value(self, a, b, root):
        self._set_false()
        self._handle("different value at /{}".format("/".join(root)))
        self._handle("a: " + repr(a))
        self._handle("b: " + repr(b))

    def _different_length(self, a, b, root):
        self._set_false()
        self._handle("different length of list at /{}".format("/".join(root)))
        self._handle("len(a)={} : ".format(len(a)) + repr(a))
        self._handle("len(b)={} : ".format(len(b)) + repr(b))

    def _list_item_not_found(self, ele, which, root):
        self._set_false()
        self._handle("list {} at /{}".format(which, "/".join(root)))
        self._handle("has element that another list hasn't :")
        self._handle(repr(ele))

    def _list_freq_not_match(self, root, aplace, bplace, ele, counta, countb):
        self._set_false()
        self._handle(
            "list at /{}, index {}, has different frequency from b at index {}:".format("/".join(root), aplace, bplace))
        self._handle("element is {}".format(ele))
        self._handle("count of list a: {}".format(counta))
        self._handle("count of list b: {}".format(countb))

    def _dict_key_not_found(self, keys, which, root):
        self._set_false()
        self._handle("dict {} at /{}".format(which, "/".join(root)))
        self._handle("has key(s) that another dict hasn't :")
        self._handle(keys)

    # internal compare methods
    def _list_comp(self, a, b, root, printdiff):
        if len(a) != len(b):
            if not printdiff:
                return False
            self._different_length(a, b, root)
            found_b = [False] * len(b)

            for i, a_i in enumerate(a):
                found = False
                for j, b_j in enumerate(b):
                    if self._common_comp(a_i, b_j, printdiff=False):
                        found_b[j] = True
                        found = True
                        break
                if not found:
                    buff = self._tuple_append(root, i)
                    self._list_item_not_found(a_i, "a", buff)

            found_a = [False] * len(a)
            for j, b_j in enumerate(b):
                found = False
                for i, a_i in enumerate(a):
                    if self._common_comp(a_i, b_j, printdiff=False):
                        found_a[i] = True
                        found = True
                        break
                if not found:
                    buff = self._tuple_append(root, j)
                    self._list_item_not_found(b_j, "b", buff)
            return

        if not self._ignore_list_seq:
            for i in range(min(len(a), len(b))):
                buff = self._tuple_append(root, i)
                if not self._common_comp(a[i], b[i], buff, printdiff):
                    if not printdiff:
                        return False
        else:
            counts_a = [[0, None] for _ in range(len(a))]
            counts_b = [[0, None] for _ in range(len(a))]
            need_to_compare_number = True

            for i in range(len(a)):
                for j in range(len(a)):
                    buff = self._tuple_append(root, len(a) * 10)
                    if self._common_comp(a[i], b[j], buff, printdiff=False):
                        counts_a[i][1] = j
                        counts_a[i][0] += 1
                    if self._common_comp(b[i], a[j], buff, printdiff=False):
                        counts_b[i][1] = j
                        counts_b[i][0] += 1

                if not counts_a[i][0]:
                    if not printdiff:
                        return False
                    need_to_compare_number = False
                    buff = self._tuple_append(root, i)
                    self._list_item_not_found(a[i], "a", buff)

                if not counts_b[i][0]:
                    if not printdiff:
                        return False
                    need_to_compare_number = False
                    buff = self._tuple_append(root, i)
                    self._list_item_not_found(b[i], "b", buff)

            if need_to_compare_number:
                for i in range(len(counts_a)):
                    counta, place = counts_a[i]
                    countb = counts_b[place][0]
                    if countb != counta and counts_b[place][1] == i:  # to prevent printing twice
                        if not printdiff:
                            return False
                        self._list_freq_not_match(root, i, place, a[i], countb, counta)  # need to swap counter here:)

        if not printdiff:
            return True

    def _dict_comp(self, a, b, root, printdiff):
        self._turn_dict_keys_to_unicode(a)
        self._turn_dict_keys_to_unicode(b)

        if self._omit_path:
            omit_dict = {}
            for x in self._omit_path:
                pre, tat = x.split(u"/")[1:-1], x.split(u"/")[-1]
                for i, v in enumerate(pre):
                    if v == u"*" and i < len(root):
                        pre[i] = root[i]
                pre = tuple(pre)
                if pre not in omit_dict:
                    omit_dict[pre] = [tat]
                else:
                    omit_dict[pre].append(tat)
            if root in omit_dict:
                a = {k: v for k, v in a.items() if k not in omit_dict[root]}
                b = {k: v for k, v in b.items() if k not in omit_dict[root]}

        ak = a.keys()  # refresh again to make sure it's unicode now
        bk = b.keys()
        diffak = [x for x in ak if x not in bk]
        diffbk = [x for x in bk if x not in ak]
        if diffak:
            if not printdiff:
                return False
            self._dict_key_not_found(diffak, "a", root)
        if diffbk:
            if not printdiff:
                return False
            self._dict_key_not_found(diffbk, "b", root)
        samekeys = [x for x in ak if x in bk]

        for key in samekeys:
            buff = self._tuple_append(root, key)
            if not self._common_comp(a[key], b[key], buff, printdiff):
                if not printdiff:
                    return False

        if not printdiff:
            return True

    def _common_comp(self, a, b, root=(), printdiff=True):
        if self._ignore_path:
            current_path = u"/{}".format(u"/".join(root))

            for ignore_item in self._ignore_path:
                if ignore_item[0] == u"^" or ignore_item[-1] == u"$":
                    find = re.findall(ignore_item, current_path)
                    assert len(find) < 2, "shouldn't be this"
                    if find and find[0] == current_path:
                        return True
                else:
                    if u"/{}".format(u"/".join(root)) == ignore_item:
                        return True

        a = self._common_warp(a)
        b = self._common_warp(b)

        if self._fuzzy_number_type(a) != self._fuzzy_number_type(b):
            if not printdiff:
                return False
            self._different_type(a, b, root)
            return

        if type(a) not in [dict, list]:
            if not self._value_comp(a, b, printdiff):
                if not printdiff:
                    return False
                self._different_value(a, b, root)
            elif not printdiff:
                return True
            return

        if type(a) == list:
            return self._list_comp(a, b, root, printdiff)

        if type(a) == dict:
            return self._dict_comp(a, b, root, printdiff)

        raise TypeError("shouldn't be here")

    def _value_comp(self, a, b, printdiff=True):  # the most base comparison
        if not self._re_compare or type(a) != six.text_type or type(b) != six.text_type:
            if (type(a) == float and type(b) in _NUMBER_TYPES) or (type(b) == float and type(a) in _NUMBER_TYPES):
                return self._fuzzy_float_equal(a, b)
            else:
                return a == b
        else:
            a_is_re = len(a) > 0 and (a[0] == u"^" or a[-1] == u"$")
            b_is_re = len(b) > 0 and (b[0] == u"^" or b[-1] == u"$")  # lazy eval prevents index out of range error
            if not a_is_re and not b_is_re:
                return a == b
            assert not (a_is_re and b_is_re), "can't compare two regular expressions"
            if b_is_re:  # let a be re
                a, b = b, a
            find = re.findall(a, b)
            assert len(find) < 2, "shouldn't be this"
            if not find:
                if printdiff:
                    self._handle("re compare failed, empty match, see next line")
                return False
            if not find[0] == b:
                if printdiff:
                    self._handle("re compare failed, found {}, expect {}, see next line".format(find[0], b))
                return False
            return True

    def compare(self, a, b, ignore_list_seq=True, re_compare=True, ignore_path=None, callback=print, strict_json=False,
                float_fuzzy_digits=0, strict_number_type=False, omit_path=None):
        """
        real compare entrance
        """
        self._handle = callback
        flag = False  # transferred str to object, need recursion

        if type(a) in [six.text_type, six.binary_type]:
            json_loaded_a = json.loads(a)  # json only, should use eval when using python dict/list-like strings instead
            flag = True
        else:
            json_loaded_a = a
        if type(b) in [six.text_type, six.binary_type]:
            json_loaded_b = json.loads(b)
            flag = True
        else:
            json_loaded_b = b
        if flag:
            return self.compare(json_loaded_a, json_loaded_b, ignore_list_seq, re_compare, ignore_path, callback,
                                strict_json, float_fuzzy_digits, strict_number_type, omit_path)

        if strict_json:
            try:
                json.dumps(a, ensure_ascii=False)
                json.dumps(b, ensure_ascii=False)
            except TypeError:
                self._handle(traceback.format_exc())
                raise TypeError("unsupported type found during strict json check")

        self._res = True
        self._ignore_list_seq = ignore_list_seq
        self._re_compare = re_compare
        self._float_fuzzy_digits = float_fuzzy_digits
        self._strict_number_type = strict_number_type
        self._ignore_path = None if ignore_path is None else [self._to_unicode_if_string(path) for path in ignore_path]
        self._omit_path = None if omit_path is None else [self._to_unicode_if_string(path) for path in omit_path]

        if self._ignore_path:
            assert all([path[0] == u"/" or u"(/" in path for path in self._ignore_path]), "invalid ignore path"
        if self._omit_path:
            assert all([path[0] == u"/" and path.split(u"/")[-1] not in (u"", u"*") and not path.split(u"/")[-1].
                       isdigit() for path in self._omit_path]), "invalid omit path"

        self._handle(self._escape("a is {}".format(a)))
        self._handle(self._escape("b is {}".format(b)))
        self._handle("ignore_list_seq = {}, re_compare = {}, ignore_path = {}, omit_path = {}, float_fuzzy_digits = {}"
                     .format(ignore_list_seq, re_compare, ignore_path, omit_path, self._float_fuzzy_digits))

        self._common_comp(a, b)
        return self._res


def compare(a, b, *args, **kwargs):
    return _Compare().compare(a, b, *args, **kwargs)


def check(a, b, *args, **kwargs):
    assert _Compare().compare(a, b, *args, **kwargs)

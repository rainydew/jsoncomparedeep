#!/usr/bin/env python
# coding: utf-8
# author: Rainy Chan rainydew@qq.com
# platform: python 2.7 or 3.6
# demos are provided in test_json_compare.py
import json
import re
import traceback
import six
import codecs

NUMBER_TYPES = list(six.integer_types) + [float]


class Jcompare(object):
    def __init__(self, print_before=True, float_fuzzy_digits=0):
        """
        :param bool print_before:  set True to print the objects or strings to compare first, disable it if printed
        :param int float_fuzzy_digits:  the accuracy (number of digits) required when float compare. 0 disables fuzzy
        """
        self.print_before = print_before
        self.float_fuzzy_digits = float_fuzzy_digits
        self._res = None
        self._ignore_list_seq = None
        self._re_compare = True
        self._ignore_path = None

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
        if self.float_fuzzy_digits:
            return abs(a - b) < 10 ** (-self.float_fuzzy_digits)
        else:
            return a == b

    @staticmethod
    def _modify_a_key(dic, from_key, to_key):
        assert not any([type(to_key) == type(exist_key) and to_key == exist_key for exist_key in
                        dic.keys()]), 'cannot change the key due to key conflicts'
        # cannot use IN here `to_key in dic.keys()`, because u"a" in ["a"] == True
        dic[to_key] = dic.pop(from_key)

    @staticmethod
    def _fuzzy_number_type(value):
        type_dict = {x: float for x in six.integer_types}
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
        print("different type at /{}".format("/".join(root)))
        print("a {}: ".format(type(a)) + repr(a))
        print("b {}: ".format(type(b)) + repr(b))

    def _different_value(self, a, b, root):
        self._set_false()
        print("different value at /{}".format("/".join(root)))
        print("a: " + repr(a))
        print("b: " + repr(b))

    def _different_length(self, a, b, root):
        self._set_false()
        print("different length of list at /{}".format("/".join(root)))
        print("len(a)={} : ".format(len(a)) + repr(a))
        print("len(b)={} : ".format(len(b)) + repr(b))

    def _list_item_not_found(self, ele, which, root):
        self._set_false()
        print("list {} at /{}".format(which, "/".join(root)))
        print("has element that another list hasn't :")
        print(repr(ele))

    def _list_freq_not_match(self, root, aplace, bplace, ele, counta, countb):
        self._set_false()
        print(
            "list at /{}, index {}, has different frequency from b at index {}:".format("/".join(root), aplace, bplace))
        print("element is {}".format(ele))
        print("count of list a: {}".format(counta))
        print("count of list b: {}".format(countb))

    def _dict_key_not_found(self, keys, which, root):
        self._set_false()
        print("dict {} at /{}".format(which, "/".join(root)))
        print("has key(s) that another dict hasn't :")
        print(keys)

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
            for j, b_j in enumerate(b):
                if not found_b[j]:
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
                        self._list_freq_not_match(root, i, place, a[i], counta, countb)

        if not printdiff:
            return True

    def _dict_comp(self, a, b, root, printdiff):
        self._turn_dict_keys_to_unicode(a)
        self._turn_dict_keys_to_unicode(b)

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
            current_path = u"/{}".format("/".join(root))

            for ignore_item in self._ignore_path:
                if ignore_item[0] == "^" or ignore_item[-1] == "$":
                    find = re.findall(ignore_item, current_path)
                    assert len(find) < 2, "shouldn't be this"
                    if find and find[0] == current_path:
                        return True
                else:
                    if u"/{}".format("/".join(root)) == ignore_item:
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
            if (type(a) == float and type(b) in NUMBER_TYPES) or (type(b) == float and type(a) in NUMBER_TYPES):
                return self._fuzzy_float_equal(a, b)
            else:
                return a == b
        else:
            a_is_re = len(a) > 0 and (a[0] == "^" or a[-1] == "$")
            b_is_re = len(b) > 0 and (b[0] == "^" or b[-1] == "$")  # lazy eval prevents index out of range error
            if not a_is_re and not b_is_re:
                return a == b
            assert not (a_is_re and b_is_re), "can't compare two regular expressions"
            if b_is_re:  # let a be re
                a, b = b, a
            find = re.findall(a, b)
            assert len(find) < 2, "shouldn't be this"
            if not find:
                if printdiff:
                    print("re compare failed, empty match, see next line")
                return False
            if not find[0] == b:
                if printdiff:
                    print("re compare failed, found {}, expect {}, see next line".format(find[0], b))
                return False
            return True

    # user methods
    def compare(self, a, b, ignore_list_seq=True, re_compare=True, ignore_path=None):
        """
        real compare entrance
        :param str or unicode or list or tuple or dict a: the first json string/json-like object to compare
        :param str or unicode or list or tuple or dict b: the second one
        :param bool ignore_list_seq: set True to ignore the order when comparing arrays(lists), recursively
        :param bool re_compare: set True to enable regular expressions for assertion. The pattern MUST contains ONE
        bracket, start with ^ or end with $, otherwise it won't be considered as an re-pattern. You can use ^.*?(sth) or
        ().*$ or so on to extract something from middle of the string. ^(.*)$ can just match any string, make this item
        ignored. Comparing two re-patterns makes no sense so it isn't allowed
        :param list[str or unicode] or None ignore_path: a list of element-paths to be ignored when comparing. e.g.
        ["/key1/key2", "/key3/1"] maans all "ignored" in {"key1":{"key2":"ignored"},"key3":["not ignored","ignored"]}
        :return bool: Whether two json string or json-like objects are equal. If not, print the differences
        """
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
            return self.compare(json_loaded_a, json_loaded_b, ignore_list_seq, re_compare, ignore_path)

        try:
            json.dumps(six.text_type(a), ensure_ascii=False)
            json.dumps(six.text_type(b), ensure_ascii=False)
        except TypeError:
            print(traceback.format_exc())
            raise TypeError("unsupported types during json check")

        self._res = True
        self._ignore_list_seq = ignore_list_seq
        self._re_compare = re_compare
        self._ignore_path = None if ignore_path is None else [self._to_unicode_if_string(path) for path in ignore_path]
        if self._ignore_path:
            assert all([path[0] == u"/" or u"(/" in path for path in self._ignore_path]), "invalid ignore path"

        if self.print_before:
            print(self._escape("a is {}".format(a)))
            print(self._escape("b is {}".format(b)))
            print("ignore_list_seq = {}, re_compare = {}, ignore_path = {}, float_fuzzy_digits = {}".format(
                ignore_list_seq, re_compare, ignore_path, self.float_fuzzy_digits))

        self._common_comp(a, b)
        return self._res

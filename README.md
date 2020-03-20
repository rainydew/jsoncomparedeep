# Json_Compare

A library to compare any json string/json-like objects.
Version 1.14 is a quickfix version that fixes the bug of losing ignore_path parameter when handling json-strings.

## Features

* Compare jsons and print the differences (what and where they are, recursion supported). Useful for interface testing.
* Config whether it will ignore the order of items in a list or not, recursively.
* Both python 26+ and 35+ supported.
* Regular expressions supported for string to skip unconcerned keys or just to assert the format.
* Compact **str** and **unicode** (or **bytes** and **str** in python3), they are considered equal. Good for non ascii coding languages.
* Both **json string** (**unicode** or **binary** str) and **json object** (**dict**, **list** or **tuple**) are supported.
* Support tuples, so results from pymysql.cursors.DictCursor can compare with interface response directly.
* Json type legal check.
* Support skipping anywhere using argument like *ignore_path=["/a/1/k", "/a/1/l"]*, dict keys or list indexes. Skipped fields are regarded as match.
* The ignore_path list now support regular expressions too. You can use *[r"^(/\d+/a)"]* as ignore_path to skip all keys named "a" in *[{"a": 1, "b": 2}, {"a": 1, "b": 4}]* but still compare the value of "b". (New)
  * Useful when compare multi records in database query result (dictionary cursor) with some fields unconcerned.
* Fuzzy equal when handling floats. (New)

## QuickStart

install

```shell
pip install jsoncomparedeep
```

or update

```shell
pip install -U jsoncomparedeep
```

a simple example

```python
from json_compare import Jcompare
cp=Jcompare()
print(cp.compare({"key1":["v1","v2"],"key2":{"key3":1}},{"key1":["v2","v1"],"key2":{"key3":2}}))
```

to see

```
a is {'key2': {'key3': 1}, 'key1': ['v1', 'v2']}
b is {'key2': {'key3': 2}, 'key1': ['v2', 'v1']}
ignore_list_seq = True, re_compare = True
different value at /key2/key3
a: 1
b: 2
False
```

For more demos and information, just install it and visit the test file **test_json_compare.py** in **Your_Python_Path/Lib/site-packages/json_compare/**

## Small Hints

* Datetime in SQL result is not JSON serializable type, use something like **CAST(create_time as CHAR) 'create_time'** in SQL statement to solve it.

## Bug report

* Issues and bugs report to rainydew@qq.com.

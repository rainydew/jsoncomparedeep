# json_compare

A library to compare any json string/bytes/json-like-objects.

Version 1.20 is an enhance version that supports *omit_path* to ignore omitted keys in dict, and fixes many bugs, esp counting message inaccurate issue when same length & element collections; and wrong not_found info when different length under *ignore_list_seq*=**True**

Version 1.19 is an enhance version that fixes small bugs with strict_number_type supported to make <int> 1 != <float> 1.0.

Version 1.18 is a quickfix + enhance version that fixes custom handlers cannot be passed recursively bug, and *float_fuzzy_digits* can be passed directly.

Version 1.17 is an enhance version that supports custom handlers to handle outputs.

Version 1.16 is a quickfix version that supports Python 3.8 (and 3.9 as well).

## Features

* Compare jsons and print the differences (what and where they are, recursion supported). Useful for interface testing.
* Config whether it will ignore the order of items in a list or not, recursively.
* Both python 2.6-2.7 and 3.5-3.9 supported.
* Regular expressions supported for string to skip unconcerned keys or just to assert the format.
* Compact **str** and **unicode** (or **bytes** and **str** in python3), they are considered equal. Good for non ascii coding languages.
* Both **json string** (**unicode** or **binary** str) and **json object** (**dict**, **list** or **tuple**) are supported.
* Support tuples, so results from pymysql.cursors.DictCursor can compare with interface response directly.
* Json type legal check.
* Support skipping anywhere using argument like *ignore_path=["/a/1/k", "/a/1/l"]*, dict keys or list indexes. Skipped fields are regarded as match.
* The ignore_path list now support regular expressions too. You can use *[r"^(/\d+/a)"]* as ignore_path to skip all keys named "a" in *[{"a": 1, "b": 2}, {"a": 1, "b": 4}]* but still compare the value of "b". (New)
  * Useful when compare multi records in database query result (dictionary cursor) with some fields unconcerned.
* Fuzzy equal when handling floats. (New)
* Python 3.8 supported. (New)
* Custom handlers supported. (New)
* Strict_number_type option to make int(1) != float(1.0) supported. (New)
* Emit keys in dict compare supported. (New)

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
* Homepage icon leads to my Github project page, issues / PRs / stars are welcomed :)

from __future__ import print_function, unicode_literals

from typing import Union, Tuple, List
import sys
import functools
from html.parser import HTMLParser


def debug(fn):
    def wrapper(*args, **kwargs):
        print(fn.__name__, 'called!')
        print(sorted(args), tuple(sorted(kwargs.items())))
        res = fn(*args, **kwargs)
        print(res)
        return res
    return wrapper


def get_from_attrs(attr_list, target):
    if not target:
        return False
    if isinstance(target, str):
        for attr in attr_list:
            if target == attr[0]:
                return attr[1]
    if isinstance(target, tuple):
        for attr in attr_list:
            if target[0] == attr[0] and target[1] in attr[1]:
                return True
    if isinstance(target, list) and len(target) == 2:
        find = target[0]
        fetch = target[1]
        got = False
        temp = None
        for attr in attr_list:
            if find[0] == attr[0] and find[1] in attr[1]:
                got = True
            if fetch[0] == attr[0]:
                temp = attr[1]
            if temp and got:
                return temp
    return False


class SimpleInnerParser(HTMLParser):
    def __init__(
        self,
        target_tag='p',
        target_attr: Union[str, Tuple, List[Tuple]] = None,  # type: ignore
        text_context=True
    ):
        super().__init__()
        self.output = []
        self.open_write = False
        self.target_tag = target_tag
        self.target_attr = target_attr
        self.text_context = text_context

    def handle_starttag(self, tag, attrs):
        if tag == self.target_tag or not self.target_tag:
            checker = get_from_attrs(
                attrs, self.target_attr) if self.target_attr else True
            self.open_write = True and checker
        if value := get_from_attrs(attrs, self.target_attr):
            if not self.text_context:
                self.output.append(str(value).strip())
                self.open_write = False

    def handle_endtag(self, tag):
        if tag == self.target_tag:
            self.open_write = False

    def handle_data(self, data: str):
        if self.open_write and self.text_context and data.strip():
            self.output.append(data.strip())


class cache(object):

    def __init__(self, fn):
        self.fn = fn
        self._cache = {}
        functools.update_wrapper(self, fn)

    def __call__(self, *args, **kwargs):
        key = str(args) + str(kwargs)
        if key in self._cache:
            ret = self._cache[key]
        else:
            ret = self._cache[key] = self.fn(*args, **kwargs)

        return ret

    def clear_cache(self):
        self._cache = {}


# from http://stackoverflow.com/questions/3627793/best-output-type-and-encoding-practices-for-repr-functions
def stdout_encode(u, default='UTF8'):
    encoding = sys.stdout.encoding or default
    if sys.version_info > (3, 0):
        return u.encode(encoding).decode(encoding)
    return u.encode(encoding)

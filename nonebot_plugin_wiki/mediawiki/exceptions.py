"""
Global wikipedia exception and warning classes.
"""

import sys


ODD_ERROR_MESSAGE = "This shouldn't happen. Please report on GitHub: github.com/goldsmith/Wikipedia"


class WikipediaException(Exception):
    """Base Wikipedia exception class."""

    def __init__(self, error):
        self.error = error

    def __unicode__(self):
        return "An unknown error occured: \"{0}\". Please report it on GitHub!".format(self.error)

    if sys.version_info > (3, 0):
        def __str__(self):
            return self.__unicode__()

    else:
        def __str__(self):
            return self.__unicode__().encode('utf8')


class PageError(WikipediaException):
    """Exception raised when no Wikipedia matched a query."""

    def __init__(self, pageid=None, *args):
        if pageid:
            self.pageid = pageid
        else:
            self.title = args[0]

    def __unicode__(self):
        if hasattr(self, 'title'):
            return u"\"{0}\" does not match any pages. Try another query!".format(self.title)
        else:
            return u"Page id \"{0}\" does not match any pages. Try another id!".format(self.pageid)

    def __str__(self):
        return "目标页面不存在"


class DisambiguationError(WikipediaException):
    """
    Exception raised when a page resolves to a Disambiguation page.

    The `options` property contains a list of titles
    of Wikipedia pages that the query may refer to.

    .. note:: `options` does not include titles that do not link to a valid Wikipedia page.
    """

    def __init__(self, title, may_refer_to):
        self.title = title
        self.options = may_refer_to

    def __unicode__(self):
        return u"\"{0}\" may refer to: \n{1}".format(self.title, '\n'.join(self.options))


class RedirectError(WikipediaException):
    """Exception raised when a page title unexpectedly resolves to a redirect."""

    def __init__(self, title):
        self.title = title

    def __unicode__(self):
        return u"\"{0}\" resulted in a redirect. Set the redirect property to True to allow automatic redirects.".format(self.title)


class HTTPTimeoutError(WikipediaException):
    """Exception raised when a request to the Mediawiki servers times out."""

    def __init__(self, query):
        self.query = query

    def __unicode__(self):
        return u"Searching for \"{0}\" resulted in a timeout. Try again in a few seconds, and make sure you have rate limiting set to True.".format(self.query)


class NoExtractError(WikipediaException):
    """当响应的内容中不含'extract'键时抛出的异常"""

    def __init__(self):
        self.message = '响应内容中不含”extract“键,请确定api是否返回摘要'

    def __str__(self):
        return self.message


class ApiReturnError(WikipediaException):
    """api返回报错"""

    def __init__(self, times):
        self.message = f"在连续尝试{times}次请求后，api方面仍返回错误"

    def __str__(self):
        return self.message


class ApiFormatError(WikipediaException):
    """api返回非json报错"""

    def __init__(self):
        self.message = "api返回非json格式，请检查目标 mediawiki api 是否正常工作"

    def __str__(self):
        return self.message

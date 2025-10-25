##############################
# Author: P. Christeas <xrg@pefnos.com> , 2025

import logging
import contextvars

from collections.abc import Callable
from typing import Any, Optional


class AddLogContext(logging.Filter):
    """ Add a context var's value as extra information to a log record

    Add this as a filter to logger handers of any level, in order to pull some
    context var and insert it as extra attributes to the LogRecord being emitted.

    :param ctx_var: reference to ContextVar that should be used
    :param var_name: in simple mode, the attribute name on the LogRecord to set
    :param setter: a function, that sets one or more LogRecord attributes after
                    the value of context var


    Hint: use the 'setter' if the context var content would be too detailed to
    use directly into log formatting or journald structure.

    Example::

        cur_request = contextvars.ContextVar("request")

        def init_logging():
            app_log = logging.getLogger("app")
            app_hander = logging.StreamHandler()
            app_handler.addFilter(AddLogContext(cur_request, 'request'))


        ...

        def handle_some_stuff():
            # here, if 'cur_request' has a value, it will be set to the LogRecord
            # as 'record.request = ...'

            log.info("I got some stuff")


    Example 2 (with setter) ::

        from requests import Request

        cur_request: ContextVar[Request] = ContextVar("request")

        def _record_decorator(record, req_value):
            record.req_method = req_value.method
            record.req_url = req_value.url

        def init_logging():
            app_log = logging.getLogger("app")
            app_hander = logging.StreamHandler()
            app_handler.addFilter(AddLogContext(cur_request, setter=_record_decorator))

        # now, each log record may have:
        # record.req_method = "GET"
        # record.req_url = "https://example.com/foo?..."
    """

    def __init__(self, ctx_var: contextvars.ContextVar,
                 var_name: Optional[str] = None,
                 setter: Optional[Callable[[logging.LogRecord, Any], None]] = None):
        super().__init__()
        self._ctx_var = ctx_var
        if setter:
           self._setter = setter
        else:
            if not var_name:
                var_name = ctx_var.name
            def _setter(record, value):
                setattr(record, var_name, value)

            self._setter = _setter

    def filter(self, record: logging.LogRecord):
        try:
            val = self._ctx_var.get()
            self._setter(record, val)
        except LookupError:
            pass
        return True


class MultiCtxHandler(logging.Handler):
    """Handler that redirects the LogRecord to another handler in context

    Usage::

        cur_logger: ContextVar[logging.Handler] = ContextVar('cur_logger')

        hnd = MultiCtxHandler(cur_logger)

        logging.getLogger("foo").addHandler(hnd)

        ...
        # somewhere deep inside the code:
        logging.getLogger("foo.bar").info('Test test')

    """

    def __init__(self, ctxvar: contextvars.ContextVar[logging.Handler],
                 level=logging.NOTSET):
        super().__init__(level)
        self._ctx_var = ctxvar

    def createLock(self):
        # override Handler, we don't want a lock here
        self.lock = None

    def emit(self, record: logging.LogRecord):
        try:
            cur_handler = self._ctx_var.get()
        except LookupError:
            return
        cur_handler.handle(record)

# eof

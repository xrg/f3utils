##############################
# Author: P. Christeas <xrg@pefnos.com> , 2025

import logging
import contextvars
from typing import Optional


class AddLogContext(logging.Filter):
    """ Add a context var's value as extra information to a log record

    Add this as a filter to logger handers of any level, in order to pull some
    context var and insert it as extra attributes to the LogRecord being emitted.

    Example:

        request = contextvars.ContextVar("request")

        def init_logging():
            app_log = logging.getLogger("app")
            app_hander = logging.StreamHandler()
            app_handler.addFilter(AddLogContext(request))


        ...

        def handle_some_stuff():
            # here, if 'request' has a value, it will be set to the LogRecord
            log.info("I got some stuff")

    """

    def __init__(self, ctx_var: contextvars.ContextVar, var_name: Optional[str] = None):
        super().__init__()
        self._var_name = var_name or ctx_var.name
        self._ctx_var = ctx_var

    def filter(self, record: logging.LogRecord):
        try:
            val = self._ctx_var.get()
            setattr(record, self._var_name, val)
        except LookupError:
            pass
        return True


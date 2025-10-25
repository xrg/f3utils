import logging
import logging.handlers
import queue
import unittest

from contextvars import ContextVar, copy_context
from f3utils.context_logging import AddLogContext, MultiCtxHandler


rovar = ContextVar('rovar')
mehvar = ContextVar('mahvar')


class TestCtxLogging(unittest.TestCase):
    logger = logging.getLogger("test.logging.context")

    def setUp(self):
        self.log_queue = queue.Queue()
        h = logging.handlers.QueueHandler(self.log_queue)
        h.addFilter(AddLogContext(rovar))
        h.addFilter(AddLogContext(mehvar, 'mehvar'))
        h.setLevel(logging.INFO)
        self.logger.addHandler(h)
        self.logger.setLevel(logging.INFO)

    def tearDown(self):
        self.logger.handlers.clear()

    def test_one(self):
        self.logger.info("Test one ...")
        rec = self.log_queue.get(block=False)
        self.assertEqual(rec.msg, "Test one ...")
        self.assertFalse(hasattr(rec, 'rovar'))
        self.assertFalse(hasattr(rec, 'mehvar'))

    def _log_foo(self, msg: str):
        self.logger.info("%s", msg)

    def test_with_context(self):
        ctx2 = copy_context()
        ctx2.run(rovar.set, "test_rovar")
        ctx2.run(self._log_foo, "with context")

        rec = self.log_queue.get(block=False)
        self.assertEqual(rec.msg, "with context")
        self.assertEqual(rec.rovar, "test_rovar")
        self.assertFalse(hasattr(rec, 'mehvar'))


ctx_handler: ContextVar[logging.Handler] = ContextVar('ctx_handler')

class TestMultiCtxLogging(unittest.TestCase):
    logger = logging.getLogger("test.logging.context2")

    def setUp(self):
        self.logger.addHandler(MultiCtxHandler(ctx_handler))
        self.logger.setLevel(logging.INFO)

    def tearDown(self):
        self.logger.handlers.clear()

    def test_ten_jobs(self):

        def _worker(num):
            log = logging.getLogger("test.logging.context2.worker")
            log.info("Test %s", num)

        all_queues = {}
        for i in range(10):
            log_queue = queue.Queue()
            h = logging.handlers.QueueHandler(log_queue)
            h.setLevel(logging.INFO)

            all_queues[i] = log_queue
            ctx2 = copy_context()
            ctx2.run(ctx_handler.set, h)
            ctx2.run(_worker, i)

        self.assertEqual(len(all_queues), 10)
        for n, qq in all_queues.items():
            rec = qq.get(block=False)
            self.assertEqual(rec.msg, f"Test {n}")


if __name__ == '__main__':
    unittest.main()

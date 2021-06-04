from io import StringIO
from unittest import TestLoader, TextTestRunner

from django.test import TestCase
from django.test.runner import DiscoverRunner

from test_query_counter.manager import HttpInteractionManager


class TestRunnerTest(TestCase):

    def setUp(self):
        # Simple class that doesn't output to the standard output
        class StringIOTextRunner(TextTestRunner):
            def __init__(self, *args, **kwargs):
                kwargs['stream'] = StringIO()
                super().__init__(*args, **kwargs)

        self.test_runner = DiscoverRunner()
        self.test_runner.test_runner = StringIOTextRunner

    @classmethod
    def get_id(cls, test_class, method_name):
        return "{}.{}.{}".format(test_class.__module__,
                                 test_class.__qualname__,
                                 method_name)

    def test_custom_setup_teardown(self):
        class Test(TestCase):
            def setUp(self):
                pass

            def tearDown(self):
                pass

            def test_foo(self):
                self.client.get('/url-1')

        self.test_runner.run_suite(
            TestLoader().loadTestsFromTestCase(testCaseClass=Test)
        )
        self.assertIn(
            self.get_id(Test, 'test_foo'),
            HttpInteractionManager.test_result_container.interactions_by_testcase
        )
        self.assertEqual(
            len(HttpInteractionManager.test_result_container.interactions_by_testcase[
                    self.get_id(Test, 'test_foo')].http_interactions),
            1
        )

from unittest import TestLoader, mock
from unittest.mock import MagicMock

from django.core.exceptions import MiddlewareNotUsed
from django.test import TestCase, override_settings
from django.test.runner import DiscoverRunner

from test_query_counter.manager import HttpInteractionManager
from test_query_counter.middleware import Middleware


class TestMiddleWare(TestCase):

    def setUp(self):
        self.test_runner = DiscoverRunner()

    def test_middleware_called(self):
        with mock.patch('test_query_counter.middleware.Middleware',
                        new=MagicMock(wraps=Middleware)) as mocked:
            self.client.get('/url-1')
            self.assertEqual(mocked.call_count, 1)

    def test_testcase_container_one_test(self):
        class Test(TestCase):
            def test_foo(self):
                self.client.get('/url-1')

        self.test_runner.run_suite(TestLoader().loadTestsFromTestCase(
            testCaseClass=Test))

        self.assertEqual(len(HttpInteractionManager.get_testcase_container().http_interactions), 1)

    def test_case_injected_one_test(self):
        class Test(TestCase):
            def test_foo(self):
                self.client.get('/url-1')

        self.test_runner.run_suite(TestLoader().loadTestsFromTestCase(
            testCaseClass=Test))

        self.assertEqual(len(HttpInteractionManager.test_result_container.interactions_by_testcase.keys()), 1)

    def test_case_injected_two_tests(self):
        class Test(TestCase):
            def test_foo(self):
                self.client.get('/url-1')

            def test_bar(self):
                self.client.get('/url-2')

        self.test_runner.run_suite(
            TestLoader().loadTestsFromTestCase(testCaseClass=Test)
        )

        self.assertEqual(len(HttpInteractionManager.test_result_container.interactions_by_testcase.keys()), 2)

    @override_settings(TEST_QUERY_COUNTER={'ENABLE': False})
    def test_case_disable_setting(self):
        class Test(TestCase):
            def test_foo(self):
                self.client.get('/url-1')

            def test_bar(self):
                self.client.get('/url-2')

        self.test_runner.run_tests(
            None,
            TestLoader().loadTestsFromTestCase(testCaseClass=Test)
        )
        self.assertIsNone(HttpInteractionManager.test_result_container)

    @override_settings(TEST_QUERY_COUNTER={'ENABLE': False})
    def test_disabled(self):
        mock_get_response = object()
        with self.assertRaises(MiddlewareNotUsed):
            Middleware(mock_get_response)

    def test_testcase_container_multiple_api_test(self):
        class Test(TestCase):
            def test_foo(self):
                self.client.get('/url-1')
                self.client.get('/url-2')

        self.test_runner.run_suite(TestLoader().loadTestsFromTestCase(
            testCaseClass=Test))

        self.assertEqual(len(HttpInteractionManager.get_testcase_container().http_interactions), 2)

    def test_testcase_container_same_api_multiple_call_test(self):
        class Test(TestCase):
            def test_foo(self):
                self.client.get('/url-1')
                self.client.get('/url-1')

        self.test_runner.run_suite(TestLoader().loadTestsFromTestCase(
            testCaseClass=Test))

        self.assertEqual(len(HttpInteractionManager.get_testcase_container().http_interactions), 2)

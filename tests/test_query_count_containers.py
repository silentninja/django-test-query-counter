
from test_query_counter.models import IHttpInteraction
from test_query_counter.query_count import (TestCaseInteractionContainer,
                                            TestResultInteractionContainer)
from django.test import RequestFactory, TestCase

from tests.views import view1, view2


class MockRequest(object):

    def __init__(self, method, path):
        self.method = method
        self.path = path

class HttpInteractionCountContainersTestCase(TestCase):

    def test_case_container_empty(self):
        container = TestCaseInteractionContainer()
        self.assertEqual(len(container.http_interactions), 0)


    def test_case_add_different_path(self):
        container = TestCaseInteractionContainer()
        self.assertEqual(len(container.http_interactions), 0)

        rf = RequestFactory()
        request = rf.get('/url-1/')
        response = view1(request)
        container.add(request, response)
        self.assertEqual(len(container.http_interactions), 1)
        self.assertEqual(container.http_interactions,
                         [IHttpInteraction("", None, None, None)])

        rf = RequestFactory()
        request = rf.get('/url-2/')
        response = view2(request)
        container.add(request, response)

        self.assertEqual(len(container.http_interactions), 2)

        self.assertEqual(container.http_interactions,
                         [IHttpInteraction("", None, None, None), IHttpInteraction("", None, None, None)])
    def test_case_add_same_path(self):
        container = TestCaseInteractionContainer()
        self.assertEqual(len(container.http_interactions), 0)

        rf = RequestFactory()
        request = rf.get('/url-1/')
        response = view1(request)
        container.add(request, response)
        self.assertEqual(len(container.http_interactions), 1)
        self.assertEqual(container.http_interactions,
                         [IHttpInteraction("", None, None, None)])

        rf = RequestFactory()
        request = rf.get('/url-1/')
        response = view1(request)
        container.add(request, response)

        self.assertEqual(len(container.http_interactions), 2)

        self.assertEqual(container.http_interactions,
                         [IHttpInteraction("", None, None, None), IHttpInteraction("", None, None, None)])

    def test_case_merge(self):
        container = TestCaseInteractionContainer()
        rf = RequestFactory()
        request = rf.get('/url-1/')
        response = view1(request)
        container.add(request, response)

        container_2 = TestCaseInteractionContainer()
        rf = RequestFactory()
        request = rf.get('/url-1/')
        response = view1(request)
        container_2.add(request, response)

        container.merge(container_2)
        self.assertEqual(len(container.http_interactions), 2)

    def test_result_empty(self):
        container = TestResultInteractionContainer()
        self.assertEqual(len(container.interactions_by_testcase.keys()), 0)

    def test_result_add(self):
        result_container = TestResultInteractionContainer()
        rf = RequestFactory()
        request = rf.get('/url-1/')
        response = view1(request)

        test_case_container = TestCaseInteractionContainer()
        test_case_container.add(request, response)

        result_container.add('some.test.test_function', test_case_container)
        self.assertEqual(len(result_container.interactions_by_testcase.keys()), 1)

        rf = RequestFactory()
        request = rf.get('/url-1/')
        response = view1(request)
        test_case_container = TestCaseInteractionContainer()
        test_case_container.add(request, response)
        result_container.add('some.test.test_other', test_case_container)
        self.assertEqual(len(result_container.interactions_by_testcase.keys()), 2)

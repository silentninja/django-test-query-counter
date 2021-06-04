from __future__ import annotations

from test_query_counter.models import IHttpInteraction


class TestResultInteractionContainer(object):
    """Stores all the http interactions from a Test Run, aggregated by Test Case"""

    def __init__(self):
        self.interactions_by_testcase = dict()

    def add(self, test_case_id, http_interaction_container):
        """
        Merge the http_interactions from a test case
        :param test_case_id: identifier for test case (This is usually the
            full name of the test method, including the module and class name)
        :param http_interaction_container: TestCaseInteractionContainer for this test case
        """
        existing_interaction_container = self.interactions_by_testcase.get(
            test_case_id,
            TestCaseInteractionContainer()
        )
        existing_interaction_container.merge(http_interaction_container)
        self.interactions_by_testcase[test_case_id] = existing_interaction_container

class TestCaseInteractionContainer(object):
    """Stores http interactions by API for a particular test case"""
    http_interactions: list

    def __init__(self, http_interactions: list = None):
        """

        @param http_interactions: List of http interactions aggregated by api
        """
        self.http_interactions = http_interactions or list()

    def add(self, request, response):
        """Aggregates the http_interaction to the captured http_interaction dict"""
        http_interaction = IHttpInteraction.generate_from(request, response)
        self.http_interactions.append(http_interaction)

    def merge(self, test_case_container: TestCaseInteractionContainer):
        """
        Merges the http interactions from another test case container in this object
        :param test_case_container: an existing test Container
        """
        self.http_interactions += test_case_container.http_interactions

from test_query_counter.manager import HttpInteractionManager

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:  # Django < 1.10
    # Works perfectly for everyone using MIDDLEWARE_CLASSES
    MiddlewareMixin = object


class Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        query_container = HttpInteractionManager.get_testcase_container()
        if query_container:
            query_container.add(request, response)

        return response

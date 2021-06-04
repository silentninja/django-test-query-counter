# -*- coding: utf-8
import inspect
import os.path
import threading
from enum import Enum
from unittest import TestResult, TestCase

from django.conf import settings
from django.test import SimpleTestCase
from django.test.utils import get_runner
from django.utils.module_loading import import_string

from test_query_counter.apps import RequestQueryCountConfig
from test_query_counter.query_count import (TestCaseInteractionContainer,
                                            TestResultInteractionContainer)

local = threading.local()


class Workflow(Enum):
    YODA = 1
    RAIDEN = 2


class HttpInteractionManager(object):
    LOCAL_TESTCASE_CONTAINER_NAME = 'interaction_test_case_container'
    test_result_container: TestResultInteractionContainer = None
    mode = os.environ.get('mode', Workflow.YODA.value)

    @classmethod
    def get_testcase_container(cls) -> TestCaseInteractionContainer:
        return getattr(local, cls.LOCAL_TESTCASE_CONTAINER_NAME, None)

    @classmethod
    def is_middleware_class(cls, middleware_path):
        from test_query_counter.middleware import Middleware

        try:
            middleware_cls = import_string(middleware_path)
        except ImportError:
            return
        return (
            inspect.isclass(middleware_cls) and
            issubclass(middleware_cls, Middleware)
        )

    @classmethod
    def add_middleware(cls):
        middleware_class_name = 'test_query_counter.middleware.Middleware'
        middleware_setting = getattr(settings, 'MIDDLEWARE', None)
        setting_name = 'MIDDLEWARE'
        if middleware_setting is None:
            middleware_setting = settings.MIDDLEWARE_CLASSES
            setting_name = 'MIDDLEWARE_CLASSES'

        # add the middleware only if it was not added before
        if not any(map(cls.is_middleware_class, middleware_setting)):
            if isinstance(middleware_setting, list):
                new_middleware_setting = (
                    middleware_setting +
                    [middleware_class_name]
                )
            elif isinstance(middleware_setting, tuple):
                new_middleware_setting = (
                    middleware_setting +
                    (middleware_class_name,)
                )
            else:
                err_msg = "{} is missing from {}.".format(
                    middleware_class_name,
                    setting_name
                )
                raise TypeError(err_msg)

            setattr(settings, setting_name, new_middleware_setting)

    @classmethod
    def wrap_pre_set_up(cls, set_up):
        def wrapped(self, *args, **kwargs):
            result = set_up(self, *args, **kwargs)
            if RequestQueryCountConfig.enabled():
                setattr(local, cls.LOCAL_TESTCASE_CONTAINER_NAME,
                        TestCaseInteractionContainer())
            return result

        return wrapped

    @classmethod
    def patch_test_case(cls):
        SimpleTestCase._pre_setup = cls.wrap_pre_set_up(
            SimpleTestCase._pre_setup
        )

    @classmethod
    def wrap_setup_test_environment(cls, func):
        def wrapped(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if not RequestQueryCountConfig.enabled():
                return result
            cls.test_result_container = TestResultInteractionContainer()
            return result

        return wrapped

    @classmethod
    def wrap_teardown_test_environment(cls, func):
        def wrapped(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if not RequestQueryCountConfig.enabled():
                return result
            # Todo Convert to list and pass it to logging server
            cls.test_result_container = None
            return result

        return wrapped

    @classmethod
    def patch_runner(cls):
        # FIXME: this is incompatible with --parallel and --test-runner
        # command arguments
        test_runner = get_runner(settings)

        if (not hasattr(test_runner, 'setup_test_environment') or not
        hasattr(test_runner, 'teardown_test_environment')):
            return

        test_runner.setup_test_environment = cls.wrap_setup_test_environment(
            test_runner.setup_test_environment
        )
        test_runner.teardown_test_environment = \
            cls.wrap_teardown_test_environment(
                test_runner.teardown_test_environment
            )

    @classmethod
    def set_up(cls):
        cls.add_middleware()
        cls.patch_test_case()
        cls.patch_result()
        if cls.mode == Workflow.YODA.value:
            cls.patch_runner()

    @classmethod
    def patch_result(cls):
        TestResult.addSuccess = cls.wrap_add_success(
            TestResult.addSuccess
        )

    @classmethod
    def wrap_add_success(cls, addSuccess):
        def wrapped(self, test: TestCase, *args, **kwargs):
            if not hasattr(cls, 'test_result_container') or not RequestQueryCountConfig.enabled():
                return addSuccess(self, test, *args, **kwargs)
            if cls.mode != Workflow.RAIDEN.value:
                container = cls.get_testcase_container()
                all_interactions = cls.test_result_container
                all_interactions.add(test.id(), container)
                result = addSuccess(self, test, *args, **kwargs)
            else:
                # Todo Compare the http interactions with api spec and change result accordingly
                result = addSuccess(self, test, *args, **kwargs)
            return result

        return wrapped

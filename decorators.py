from spider_errors import *


def login_check(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print('error: {}'.format(e))
            raise LoginError()

    return inner


def request_check(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
            raise RequestError()

    return inner


def analyze_check(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
            raise AnalyzeError()

    return inner


def detection_check(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            raise DetectionError()

    return inner

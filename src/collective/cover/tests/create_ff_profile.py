# -*- coding: utf-8 -*-
"""Create a custom Firefox profile for robot testing."""
from selenium import webdriver


def create_ff_profile():
    fp = webdriver.FirefoxProfile()
    # dom.disable_beforeunload default is True in Selenium profile. We need to change
    # it to False so that the beforeunload popup is shown in the robots tests.
    fp.set_preference("dom.disable_beforeunload", False)
    fp.update_preferences()
    return fp.path

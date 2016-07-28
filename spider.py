#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2016/7/27 23:26
"""

from selenium import webdriver



if __name__ == '__main__':
    phantom = webdriver.PhantomJS()
    phantom.get('http://www.baidu.com')
    phantom.execute_script()
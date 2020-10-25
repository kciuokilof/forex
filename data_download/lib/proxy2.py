from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType

options = webdriver.ChromeOptions()

proxy = Proxy()
proxy.proxyType = ProxyType.MANUAL
proxy.autodetect = False
from random_proxies import random_proxy

PROXY = '66.97.120.123:3128'

proxy.httpProxy = proxy.sslProxy = proxy.socksProxy = PROXY
options.Proxy = proxy
options.add_argument("ignore-certificate-errors")
driver = webdriver.Chrome('../../data/chromedriver.exe', chrome_options=options)

driver.get('https://lumtest.com/myip.json')


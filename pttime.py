import os
import re
import time
import traceback

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service as FirefoxService

browser = 'firefox'  # 'firefox' or 'chrome'

def get_driver(browser):
    if browser == "chrome":
        options = webdriver.ChromeOptions()
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--remote-debugging-port=9223")
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--shm-size 2g")
    if not options:
        return
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")

    # options.add_argument(
    #     "User-Agent=Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36"
    # )


    if browser == "chrome":
        # driver = webdriver.Chrome(
        #     service=ChromiumService(
        #         ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        #     ),
        #     options=options,
        # )
        # hub_url = "http://127.0.0.1:4444"
        hub_url = "http://10.160.34.251:4444"
        driver = webdriver.Remote(
            command_executor=hub_url,
            options=options,
        )
        # driver = webdriver.Chrome(
        #     service=ChromiumService(executable_path="./chromedriver"),
        #     options=options,
        # )
    elif browser == "firefox":
        # driver = webdriver.Firefox(
        #     service=FirefoxService(GeckoDriverManager().install()),
        #     options=options,
        # )
        driver = webdriver.Firefox(
            service=FirefoxService(executable_path="./geckodriver", log_output='./geckodriver.log'),
            options=options,
        )
    return driver

def old_get_driver(browser):
    if browser == 'chrome':
        options = webdriver.ChromeOptions()
        options.add_argument('--remote-debugging-port=9222')
    elif browser == 'firefox':
        options = webdriver.FirefoxOptions()
        options.add_argument('--shm-size 2g')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    if browser == 'chrome':
        service = Service(current_dir + '/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
    elif browser == 'firefox':
        service = Service(current_dir + '/geckodriver')
        driver = webdriver.Firefox(service=service, options=options)

def do_checkin(driver):
    url = 'https://www.pttime.org/login.php?returnto=attendance.php'
    driver.get(url)
    driver.find_element('xpath', '//*[@id="nav_block"]/form/table/tbody/tr[1]/td[2]/input').send_keys(username)
    driver.find_element('xpath', '//*[@id="nav_block"]/form/table/tbody/tr[2]/td[2]/input').send_keys(password)
    driver.find_element('xpath', '//*[@id="nav_block"]/form/table/tbody/tr[4]/td[2]/input').click()
    driver.find_element('xpath', '//*[@id="nav_block"]/form/table/tbody/tr[7]/td/input[1]').click()

    #time.sleep(3)
    #driver.refresh()
    time.sleep(1)
    days = driver.find_element('xpath', '/html/body/table[4]/tbody/tr/td/table/tbody/tr/td/span[3]/b').text
    share_ratio = driver.find_element('xpath', '/html/body/table[2]/tbody/tr/td/table[2]/tbody/tr[2]/td/div[1]/span[1]').text
    upload_amount = driver.find_element('xpath', '/html/body/table[2]/tbody/tr/td/table[2]/tbody/tr[2]/td/div[1]/span[2]').text
    download_amount = driver.find_element('xpath', '/html/body/table[2]/tbody/tr/td/table[2]/tbody/tr[2]/td/div[1]/span[3]').text
    magic_points_long = driver.find_element('xpath', '/html/body/table[2]/tbody/tr/td/table[2]/tbody/tr[2]/td/div[1]/span[7]').text
    driver.close()

    print(magic_points_long)
    str1 = '魔力值 \((.*?)魔力/小时\) \[使用\&说明\]: (.*?) 签到领魔力\['
    str2 = '魔力值 \((.*?)魔力/小时\) \[使用\&说明\]: (.*?)\[详情\]'
    match = re.match(str1, magic_points_long) or re.match(str2, magic_points_long)
    magic_points = match.groups()
    return days, magic_points


current_dir = os.path.dirname(__file__)
print(current_dir)
with open(current_dir + '/.env') as f:
    username, password, push_url = f.read().split('\n')[:3]

try_count = 2

if __name__ == '__main__':
    driver = get_driver(browser)
    for i in range(try_count):
        try:
            days, magic_points = do_checkin(driver)
        except Exception as e:
            traceback.print_exc()
        else:
            requests.post(push_url,
                          data=f'[PTTime] succeeded, {username} has continuously checked in for {days} days, possessing {magic_points[1]} magic points')
            break
    else:
        requests.post(push_url, data=f'[PTTime] failed, {username}')

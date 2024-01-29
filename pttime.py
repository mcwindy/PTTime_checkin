import os
import re
import time
import traceback

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

browser = 'firefox'  # 'firefox' or 'chrome'


def do_checkin(browser):
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

try_count = 3

if __name__ == '__main__':
    for i in range(try_count):
        try:
            days, magic_points = do_checkin(browser)
        except Exception as e:
            traceback.print_exc()
        else:
            requests.post(push_url,
                          data=f'[PTTime] succeeded, {username} has continuously checked in for {days} days, possessing {magic_points[1]} magic points')
            break
    else:
        requests.post(push_url, data=f'[PTTime] failed, {username}')

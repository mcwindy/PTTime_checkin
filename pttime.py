import os
import re
import time

import requests
from selenium import webdriver

with open(os.path.dirname(__file__) + '/.env') as f:
    username, password, push_url = f.read().split('\n')[:3]
try:
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(executable_path='./geckodriver', options=options)
    url = 'https://www.pttime.org/login.php?returnto=attendance.php'
    driver.get(url)
    driver.find_element('xpath', '//*[@id="nav_block"]/form[2]/table/tbody/tr[1]/td[2]/input').send_keys(username)
    driver.find_element('xpath', '//*[@id="nav_block"]/form[2]/table/tbody/tr[2]/td[2]/input').send_keys(password)
    driver.find_element('xpath', '//*[@id="nav_block"]/form[2]/table/tbody/tr[4]/td[2]/input').click()
    driver.find_element('xpath', '//*[@id="nav_block"]/form[2]/table/tbody/tr[7]/td/input[1]').click()

    time.sleep(3)
    driver.refresh()
    time.sleep(3)
    days = driver.find_element('xpath', '/html/body/table[4]/tbody/tr/td/table/tbody/tr/td/span[3]/b').text
    share_ratio = driver.find_element('xpath', '/html/body/table[2]/tbody/tr/td/table[2]/tbody/tr[2]/td/div[1]/span[1]').text
    upload_amount = driver.find_element('xpath', '/html/body/table[2]/tbody/tr/td/table[2]/tbody/tr[2]/td/div[1]/span[2]').text
    download_amount = driver.find_element('xpath', '/html/body/table[2]/tbody/tr/td/table[2]/tbody/tr[2]/td/div[1]/span[3]').text
    magic_points_long = driver.find_element('xpath', '/html/body/table[2]/tbody/tr/td/table[2]/tbody/tr[2]/td/div[1]/span[7]').text
    driver.close()

    magic_points = re.match('魔力值 \((.*?)魔力/小时\) \[使用\&说明\]: (.*?)\(获得(.*?),详情\)', magic_points_long).groups()
except:
    requests.post(push_url, data=f'[PTTime] failed, {username}')
else:
    requests.post(
        push_url,
        data=
        f'[PTTime] succeeded, get {magic_points[2]} magic points, {username} has continuously checked in for {days} days, possessing {magic_points[1]} magic points'
    )

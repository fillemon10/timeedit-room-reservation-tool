import sys
import time
import datetime
import requests
import random
import undetected_chromedriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
import credentials


# Grab logincookie using selenium with chrome webdriver
def generate_login_key(username, password):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome()
    driver.get("https://cloud.timeedit.net/chalmers/web/timeedit/sso/saml2?back=https%3A%2F%2Fcloud.timeedit.net%2Fchalmers%2Fweb%2Fb1%2F")

    search_box = driver.find_element(By.ID, "userNameInput")
    search_box.send_keys(username)

    search_box = driver.find_element(By.ID, "passwordInput")
    search_box.send_keys(password)

    submit_button = driver.find_element(By.ID, "submitButton")
    submit_button.click()

    cookies = driver.get_cookies()

    driver.quit()

    # Return only the key in 'TEchalmersweb' which is used in post requests as authentication
    return cookies[0]['value']
    

# Create data dictionary to pass along with request. First arg is days ahead in time
# @start_time and @end_time is in format MMHH
def create_data_dict(name_reservation, days_ahead, room, start_time, end_time):
    date = datetime.date.today() + datetime.timedelta(days=days_ahead)
    date = '20' + str(date.strftime('%y%m%d'))
    data = {
    'kind': 'reserve',
    'nocache': '4',
    'l': 'sv_SE',
    'o': '214726.186',
    'o': '203460.192',
    'aos': '',
    'dates': date,
    'starttime': start_time,
    'endtime': end_time,
    'url': 'https%3A%2F%2Fcloud.timeedit.net%2Fchalmers%2Fweb%2Fb1%2Fri1Q5008.html%2300214726',
    'fe2': '',
    'fe8': '',
    'CSTT': '-5267498248312575220'
    }
    return data


username = credentials.username
password = credentials.password

room = sys.argv[1]
start_time = sys.argv[2]
end_time = sys.argv[3]
# Days ahead to book the room. You should always use 15
days_ahead = 15

cookie = generate_login_key(username, password)

print(cookie)
# Get the room id from arg1

# Create the data field of the request
url = 'https://cloud.timeedit.net/chalmers/web/b1/ri1Q5008.html'

headers = {
    'authority': 'cloud.timeedit.net',
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.9,sv;q=0.8',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'cookie': 'sso-parameters=back=https%3A%2F%2Fcloud.timeedit.net%2Fchalmers%2Fweb%2Fb1%2Fri1Q5008.html&ssoserver=saml2; TEchalmersweb=' + cookie,
    'dnt': '1',
    'origin': 'https://cloud.timeedit.net',
    'referer': 'https://cloud.timeedit.net/chalmers/web/b1/ri1Q5008.html',
    'sec-ch-ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    'x-requested-with': 'XMLHttpRequest'
}

print(headers.get('cookie'))

data = {
    'kind': 'reserve',
    'nocache': '4',
    'l': 'sv_SE',
    'o': ['214726.186', '203460.192'],
    'dates': '20240209',
    'starttime': '13:45',
    'endtime': '14:45',
    'url': 'https://cloud.timeedit.net/chalmers/web/b1/ri1Q5008.html#00214726',
    'fe2': '',
    'fe8': '',
    'CSTT': '1257603083511417094'
}

r = requests.post(url, headers=headers, data=data)

print(r.text)
answer = r.text.encode('UTF-8')
i = 0
# Writes response to file named according to date of reservation attempted
date_reservation = datetime.date.today() + datetime.timedelta(days=days_ahead)
# Open file for writing log
f = open(str(date_reservation) + "-" + sys.argv[3] + ".log", 'w')
date_of_execution = datetime.datetime.today()
f.write("Date executed: " + str(date_of_execution) + '\n')
# Loop until booking successfull or message about already taken in response
yes = True
while (yes):
    r = requests.post(url=url, headers=headers, data=data)
    answer = r.text.encode('UTF-8')
    print(answer)
    # Write response to file
    f.write(str(datetime.datetime.now()) + '\t' + answer + '\n')
    i += 1
    yes = False
time.sleep(100)
print
'It isnt past midnight yet, trying again...'
print
answer
# Write answer to file in case while loop never runs
f.write("\n" + str(datetime.datetime.now()) + '\t' + answer + '\n')
# Close file before exiting
f.close()

import sys
import time
import datetime
import requests
import random
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
import credentials


# Grab logincookie using selenium with chrome webdriver
def generate_login_key(username, password):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome("chromedriver_mac64/chromedriver", options=options)
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
        'fe49': name_reservation,
        'fe50': name_reservation + '@stud.ntnu.no',
        'id': '-1',
        'dates': date,
        'datesEnd': date,
        'startTime': start_time,
        'endTime': end_time,
        'o': room,
        'url': 'https%3A%2F%2Fno.timeedit.net%2Fweb%2Fhig%2Fdb1%2Fstudent%2Fr.html%3Fh%3Dt%26sid%3D5%26id%3D-1%26step%3D2%26id%3D-'
               + '1%26dates%3D' + date + '%26datesEnd%3D' + date + '%26startTime%3D8%253A00%26endTime%3D22%253A00%26o%3D' +
               room + '%252C10%252C%2BA' + room + '%252C%2Bgrupperom',
        'kind': 'reserve'}
    return data


username = credentials.username
password = credentials.password

login_key = generate_login_key(username, password)



dopfk



room = sys.argv[3]
start_time = sys.argv[4]
end_time = sys.argv[5]
# Days ahead to book the room. You should always use 15
days_ahead = 15
# Create cookie from arg1 (username) and arg2 (password)
cookie = generate_login_key(username, password)
# Get the room id from arg3
room = get_room_ID(room)
# Create the data field of the request
data = create_data_dict(username, days_ahead, room, start_time, end_time)

# URL is static
url = 'https://no.timeedit.net/web/hig/db1/student/r.html?h=t&sid=5&id=-1&step=2&id=-1&dates=20170219&datesEnd=20170219&startTime=11%3A00&endTime=11%3A05&o=162177.185%2C8%2C+A267%2C+grupperom&nocache=3'

# Include cookie in headers along with user agent (dont want the website to think we are a bot)
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'
    ,
    'cookie': 'sso-parameters=back=https%3A%2F%2Fno.timeedit.net%2Fweb%2Fhig%2Fdb1%2Fstudent%2Fr.html%3Fh%3Dt%26sid%3D5%26id%3D-1&ssoserver=feide; TEwebhigdb1=' + cookie}

# Putting it all together in the request
r = requests.post(url=url, headers=headers, data=data)
answer = r.text.encode('UTF-8')
i = 0
# Writes response to file named according to date of reservation attempted
date_reservation = datetime.date.today() + datetime.timedelta(days=days_ahead)
# Open file for writing log
f = open(str(date_reservation) + "-" + sys.argv[3] + ".log", 'w')
date_of_execution = datetime.datetime.today()
f.write("Date executed: " + str(date_of_execution) + '\n')
# Loop until booking successfull or message about already taken in response
while ("innenfor dato- og klokkeslettgrensene" in answer):
    r = requests.post(url=url, headers=headers, data=data)
    answer = r.text.encode('UTF-8')
    # Write response to file
    f.write(str(datetime.datetime.now()) + '\t' + answer + '\n')
    i += 1
time.sleep(100)
print
'It isnt past midnight yet, trying again...'
print
answer
# Write answer to file in case while loop never runs
f.write("\n" + str(datetime.datetime.now()) + '\t' + answer + '\n')
# Close file before exiting
f.close()
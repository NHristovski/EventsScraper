from bs4 import BeautifulSoup
from datetime import datetime
import requests, lxml.html
from datetime import timedelta
from multiprocessing import Queue
import sys

index = sys.argv[1]
pw = sys.argv[2]

s = requests.session()
login = s.get("https://cas.finki.ukim.mk/cas/login?service=http%3A%2F%2Fcourses.finki.ukim.mk%2Flogin%2Findex.php")
if login.status_code != 200:
    sys.exit(-1)

login_html = lxml.html.fromstring(login.text)
hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}

form['username'] = index
form['password'] = pw

response = s.post('https://cas.finki.ukim.mk/cas/login?service=http%3A%2F%2Fcourses.finki.ukim.mk%2Flogin%2Findex.php', data=form)



if len(response.history) == 0:
    sys.exit(-2)

soup = BeautifulSoup(response.content, 'html.parser')

events = soup.find_all(class_="hasevent")

file = open("eventsOutput.txt","w+",encoding = "utf-8")

for event in events:
    event_str = str(event)

    parts = event_str.split("data-day-timestamp=\"")

    if (len(parts) > 0):
        timestamp_parts = parts[1].split('\"')

        if (len(timestamp_parts) > 0):


            ts = int(timestamp_parts[0])
            
            #convert time to GMT + 1
            local_timestamp = datetime.utcfromtimestamp(ts) + timedelta(minutes=60)
            
            print("Due date: " + local_timestamp.strftime('%Y-%m-%d %H:%M:%S'))
            file.write("Due date: " + local_timestamp.strftime('%Y-%m-%d %H:%M:%S'))
            file.write("\r\n")

        event_text = ' '.join(event.getText().split())
        print(event_text)
        print("\n")
        file.write(event_text)
        file.write("\r\n\r\n")

file.close()
sys.exit(0)



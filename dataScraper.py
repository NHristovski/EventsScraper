from bs4 import BeautifulSoup
from datetime import datetime
import requests, lxml.html
from datetime import timedelta
from multiprocessing import Queue
import sys
import time

def log_in():
    s = requests.session()
    login = s.get("https://cas.finki.ukim.mk/cas/login?service=http%3A%2F%2Fcourses.finki.ukim.mk%2Flogin%2Findex.php")
    if login.status_code != 200:
        print('Error getting login page.')
        sys.exit(-1)

    login_html = lxml.html.fromstring(login.text)
    hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
    form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}

    form['username'] = index
    form['password'] = pw

    response = s.post('https://cas.finki.ukim.mk/cas/login?service=http%3A%2F%2Fcourses.finki.ukim.mk%2Flogin%2Findex.php', data=form)

    if len(response.history) == 0:
        print('Error logging in.')
        sys.exit(-2)

    return response


def get_events():       
   
    response = log_in()

    soup = BeautifulSoup(response.content, 'html.parser')

    events = soup.find_all(class_='hasevent')

    return events


def show_events_pretty():
    print("")

    now = datetime.utcfromtimestamp(time.time()) + timedelta(minutes=60)
    print(" Today: " + now.strftime('%d.%m.%Y %H:%M:%S' + "\n"))

    events = get_events()
    for event in events:
        event_str = str(event)

        parts = event_str.split("data-day-timestamp=\"")

        if (len(parts) > 0):
            timestamp_parts = parts[1].split('\"')

            if (len(timestamp_parts) > 0):

                ts = int(timestamp_parts[0])
                
                #convert time to GMT + 1
                local_timestamp = datetime.utcfromtimestamp(ts) + timedelta(hours = 24) + timedelta(minutes = 55)

                if local_timestamp.date() >= now.date():
                    print(' ' + '-'*33  + '  ' + '-'*33)

                    time_left_formated = str(local_timestamp - now).split('.')[0]
                    print(" | DUE DATE: " + local_timestamp.strftime('%d.%m.%Y %H:%M:%S') + " |  | TIME LEFT: " + time_left_formated + ' '*(19-len(time_left_formated)) + "|")
                    print(' ' + '-'*33  + '  ' + '-'*33 + '\n')

                    full_event_text = event.getText()[3:].lstrip()
                    
                    event_counter = 1

                    while not full_event_text.isspace() and len(full_event_text) > 0:
                        spaces_found = 0
                        counter = 0
                        for ch in full_event_text:
                            if ch.isspace():
                                if spaces_found == 10:
                                    break
                                else:
                                    spaces_found = spaces_found + 1
                            else:
                                spaces_found = 0
                            counter += 1

                        single_event = full_event_text[0:counter - 10]

                        if not single_event.isspace():
                            taken_space = len(str(event_counter)) + 3
                            free_space = terminal_width - taken_space
                            if len(single_event) > free_space:
                                
                                next_char_idx = free_space
                                while not single_event[next_char_idx].isspace():
                                    next_char_idx -= 1
                                
                                single_event_line = single_event[:next_char_idx]

                                print(" " + str(event_counter) + "." + ' '.join(single_event_line.split()))

                                single_event = single_event[next_char_idx:]

                                while len(single_event) > free_space:

                                    next_char_idx = free_space
                                    while not single_event[next_char_idx].isspace():
                                        next_char_idx -= 1

                                    single_event_line = single_event[0:next_char_idx]
                                    print(" " * (taken_space - 1) + ' '.join(single_event_line.split()))

                                    single_event = single_event[next_char_idx:]

                                print(" " * (taken_space - 1) + ' '.join(single_event.split()) + "\n")
                            else:
                                print(" " + str(event_counter) + "." + ' '.join(single_event.split()) + "\n")


                            event_counter += 1

                        full_event_text = full_event_text[counter : ].lstrip()
                    print(' ' + '='*(terminal_width-2) + '\n')                           


if __name__ == '__main__':
    
    args = sys.argv

    args_len = len(args)

    if args_len < 3:
        print("Usage: python events index cas_pw [ width of terminal {default = 80} ]")
        quit()

    index = args[1]
    pw = args[2]

    terminal_width = 80

    if args_len >= 4:
        try:
            width = int(args[3])
            if width < 70:
                print('Wrong 3rd argument.')
                print('Setting terminal_width to default')
            else:
                terminal_width = width
        except:
            print('Wrong 3rd argument.')
            print('Setting terminal_width to default')
        
    show_events_pretty()


sys.exit(0)



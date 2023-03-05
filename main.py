# PanAm Bot

import smtplib, ssl
import traceback
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import WebDriverException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Try executing task until it succeeds
def executeTask(b, e, task, s):

    works = False
    ans = ""

    while not works:
        try:
            if task == 'scroll':
                b.execute_script('arguments[0].scrollTo()', b.find_element(By.XPATH, e))
            elif task == 'type':
                b.find_element(By.XPATH, e).send_keys(s)
            elif task == 'get':
                ans = b.find_element(By.XPATH, e).get_attribute(s)
            else:
                b.find_element(By.XPATH, e).click()

            works = True

        except StaleElementReferenceException:
            pass
        except ElementNotInteractableException:
            pass
        except ElementClickInterceptedException:
            pass
        except NoSuchElementException:
            pass
        except NoSuchWindowException:
            pass

        if works and task == 'get':
            return ans

# Reading the txt file
file = open('info.txt', 'r')
data = file.read().split('\n')

# Emailing
port = 465  # For SSL
smtp_server = 'smtp.gmail.com'
sender_email = data[1].split('= ')[1]
password = data[2].split('= ')[1]
error_handling = data[3].split('= ')[1]

try:
    # Initiate the browser
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    # Accounts
    i = 6
    users = []
    passes = []

    while data[i] != '':
        users.append([data[i]])
        i += 1

    i += 2
    while data[i] != '':
        passes.append(data[i])
        i += 1

    i += 2
    count = 0
    while data[i] != '':
        users[count].append(data[i])
        count += 1
        i += 1

    i += 2
    count = 0
    while data[i] != '':
        users[count].append(data[i].split(', '))
        count += 1
        i += 1

    i += 2
    count = 0
    while data[i] != '':
        users[count].append(data[i].split(', '))
        count += 1
        i += 1

    i += 2
    count = 0
    while data[i] != '':
        for j in range(len(users[count][3])):
            users[count][3].insert(j*2+1, data[i].split(', ')[j])
        count += 1
        i += 1

    # Open the Website
    browser.get('https://tpasc.ezfacility.com/Sessions')

    browser.maximize_window()

    # Execute for each user
    for i in range(len(users)):

        # Login
        executeTask(browser, '/html/body/section[1]/aside/div[1]/div/ul/li[9]', 'click', '')

        executeTask(browser, '/html/body/div[1]/div/div/div[3]/div/div/div/form/div[1]/div/div/div/input', 'type', users[i][0])
        executeTask(browser, '/html/body/div[1]/div/div/div[3]/div/div/div/form/div[2]/div/div/div/input', 'type', passes[i])

        executeTask(browser, '/html/body/div[1]/div/div/div[3]/div/div/div/form/div[4]/div[1]/div/button', 'click', '')

        email_text = []
        count = 0

        # Book all available slots
        while count < 3:
            slots = []
            runs = []

            if count:
                date = executeTask(browser, '/html/body/section[2]/section/div/div[3]/div/div[1]/div[1]/h2', 'get', 'innerText')
                if count > 1:
                    day = executeTask(browser, '/html/body/section[2]/section/div/div[3]/div/div[2]/div/div/table/tbody/tr[1]/td/span', 'get', 'innerText')
                else:
                    day = ''

                newDay = day
                while newDay == day:
                    newDay = executeTask(browser, '/html/body/section[2]/section/div/div[3]/div/div[2]/div/div/table/tbody/tr[1]/td/span', 'get', 'innerText')
                runs = browser.find_elements(By.XPATH, '/html/body/section[2]/section/div/div[3]/div/div[2]/div/div/table/tbody/tr/td/a')

            for j in range(len(runs)):
                run = executeTask(browser, '/html/body/section[2]/section/div/div[3]/div/div[2]/div/div/table/tbody/tr['+str(j+2)+']/td[3]/a', 'get', 'innerText')
                t = executeTask(browser, '/html/body/section[2]/section/div/div[3]/div/div[2]/div/div/table/tbody/tr['+str(j+2)+']/td[1]', 'get', 'innerText')

                for k in range(len(users[i][2])):
                    #
                    if run == users[i][2][k] and t not in slots \
                            and ((t.split(' ')[0][-2:] == users[i][3][k*2][-2:]
                                  and int(t.split(':')[0]) >= int(users[i][3][k*2].split(':')[0]))
                                 or (t.split(' ')[0][-2:] == users[i][3][(k*2)+1][-2:] and int(t.split(':')[0]) <= int(users[i][3][(k*2)+1].split(':')[0]))):

                        slots.append(t)
                        executeTask(browser, '/html/body/section[2]/section/div/div[3]/div/div[2]/div/div/table/tbody/tr['+str(j+2)+']', 'scroll', '')
                        executeTask(browser, '/html/body/section[2]/section/div/div[3]/div/div[2]/div/div/table/tbody/tr['+str(j+2)+']', 'click', '')

                        while True:
                            if 'block' in executeTask(browser, '/html/body/section[2]/section/div/div[4]/div/div/form/div[2]/div', 'get', 'style'):
                                break

                        if 'block' in executeTask(browser, '/html/body/section[2]/section/div/div[4]/div/div/div[1]/button[2]', 'get', 'style'):
                            executeTask(browser, '/html/body/section[2]/section/div/div[4]/div/div/div[1]/button[2]', 'click', '')
                            email_text.append(run + ' BOOKED FOR ' + day + ', ' + date + ' AT ' + t)
                        else:
                            executeTask(browser, '/html/body/section[2]/section/div/div[4]/div/div/form/div[1]/ul', 'click', '')

            browser.execute_script('window.scroll(0, 0);')
            executeTask(browser, '/html/body/section[2]/section/div/div[3]/div/div[1]/div[1]/ul/li[2]', 'click', '')
            count += 1

        # Email bookings
        if len(email_text):
            message = MIMEMultipart('alternative')
            message['Subject'] = "New PanAm Bookings"
            message['From'] = "PanAm Booking Bot"
            message['To'] = users[i][1]

            # Creates HTML version of the message
            html = """\
            <html>
                <body>
                    <h2>You have new PanAm bookings:<br></h2>"""

            for booking in email_text:
                html += """
                    <h3>""" + booking + """<br></h3>"""

            html += """
                </body>
            </html> 
            """

            # Adds HTML-text parts to MIMEMultipart message
            message.attach(MIMEText(html, "html"))

            # Creates secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, users[i][1], message.as_string())

        # Logout
        executeTask(browser, '/html/body/section[1]/aside/div[1]/div/ul/li[8]/a', 'click', '')

except Exception:

    print(traceback.format_exc())

    # Email errors
    message = MIMEMultipart('alternative')
    message['Subject'] = "ERROR in PanAm Booking Bot"
    message['From'] = "PanAm Booking Bot"
    message['To'] = 'sayon.mk@gmail.com'

    # Creates HTML version of the message
    html = """\
    <html>
        <body>
            <h2>The following error occured in the PanAm Booking Bot:<br></h2>
            <h3>""" + str(traceback.format_exc()) + """<br></hr>
        </body>
    </html>
    """

    # Adds HTML-text parts to MIMEMultipart message
    message.attach(MIMEText(html, "html"))

    # Creates secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, error_handling, message.as_string())
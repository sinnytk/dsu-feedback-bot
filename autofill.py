import conf
import email
import pprint
from email import policy
from datetime import datetime
from imaplib import IMAP4
from bs4 import BeautifulSoup


FEEDBACK_ADMIN_EMAIL = "survey.admin@dsu.edu.pk"


def get_latest_forms(conn):
    latest_forms = {}
    latest_date = last_form_date(conn)
    print(f'Fetching latest forms dated {latest_date.strftime("%d-%m-%Y")}')
    typ, data = conn.search(
        None, f'FROM "{FEEDBACK_ADMIN_EMAIL}" SINCE "{latest_date.strftime("%d-%b-%Y")}"')
    for num in data[0].split():
        typ, data = conn.fetch(num, '(RFC822)')
        email_message = email.message_from_bytes(
            data[0][1], policy=policy.default)

        teacher_name = email_message['subject'].split('for ')[-1]
        # If the message is an invitation, then we the form is not filled
        if email_message['subject'].startswith('Invitation'):
            form_link = get_survey_link(email_message)
            latest_forms[teacher_name] = {
                'survey_link': form_link, "form_filled": False}
        # Else if message is an confirmation, then make form_filled true
        elif email_message['subject'].startswith('Confirmation'):
            teacher_name = email_message['subject'].split(
                'for ')[-1]
            latest_forms[teacher_name]["form_filled"] = True
    return latest_forms


def last_form_date(conn):
    typ, data = conn.search(
        None, 'FROM', f'"{FEEDBACK_ADMIN_EMAIL}" SUBJECT "Invitation to participate"')
    latest_date = None
    for num in data[0].split():
        typ, data = conn.fetch(num, '(RFC822)')
        email_message = email.message_from_bytes(
            data[0][1], policy=policy.default)
        email_date = datetime.strptime(
            email_message['date'], "%a, %d %b %Y %H:%M:%S %z").date()
        if latest_date is None or latest_date < email_date:
            latest_date = email_date

    return latest_date


def get_survey_link(email_message):
    for part in email_message.walk():
        if part.get_content_type() == "text/html":
            raw_html = part.get_payload(decode=True)
            raw_html = raw_html.decode()
    soup = BeautifulSoup(raw_html, 'lxml')
    survey_link = soup.a['href']
    return survey_link


def main():
    # opening a connection and connecting to mail server with IMAP
    conn = IMAP4('mail.dsu.edu.pk')
    # using credentials defined in conf.py to connect
    print(f'Logging in for {conf.username}')
    conn.login(conf.username, conf.password)
    print(f'Successfully logged in, retrieving emails ')

    # selecting the "inbox" mailbox
    conn.select('inbox')

    # retrieving the latest forms
    latest_forms = get_latest_forms(conn)

    unfilled_forms = []
    filled_forms = []

    for teacher, details in latest_forms.items():
        if details['form_filled']:
            filled_forms.append(teacher)
        else:
            unfilled_forms.append({'teacher_name': teacher, **details})
    print('\n\n')

    print('Forms filled for: ')
    for t in filled_forms:
        print('\t', t)

    print('Forms unfilled for: ')
    for t in unfilled_forms:
        print('\t', t['teacher_name'])

    print('\n\n')

    print('Now filling forms, please insert rate from 1-5?')
    print('1 being excellent, 5 being poor')
    for t in unfilled_forms:
        rating = int(
            input(f'\tWhat do you want to rate {t["teacher_name"]}: '))
        t['rating'] = rating

    print('Opening Chrome to fill the forms according to ratings')
    for t in unfilled_forms:
        print(f"{t['teacher_name']}: \t{t['rating']}")

    conn.logout()


if __name__ == "__main__":
    main()

import conf
import email
from email import policy
from datetime import datetime
from imaplib import IMAP4


FEEDBACK_ADMIN_EMAIL = "survey.admin@dsu.edu.pk"


def get_latest_forms(conn):
    latest_date = last_form_date(conn)
    print(f'Fetching latest forms dated {latest_date.strftime("%d-%m-%Y")}')
    print(f'FROM "{FEEDBACK_ADMIN_EMAIL}" SINCE "{latest_date}"')
    typ, data = conn.search(
        None, f'FROM "{FEEDBACK_ADMIN_EMAIL}" SINCE "{latest_date.strftime("%d-%b-%Y")}"')
    for num in data[0].split():
        typ, data = conn.fetch(num, '(RFC822)')
        email_message = email.message_from_bytes(
            data[0][1], policy=policy.default)
        print(email_message['subject'])


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


def main():
    # opening a connection and connecting to mail server with IMAP
    conn = IMAP4('mail.dsu.edu.pk')
    # using credentials defined in conf.py to connect
    conn.login(conf.username, conf.password)

    # selecting the "inbox" mailbox
    conn.select('inbox')

    # retrieving the latest forms
    latest_forms = get_latest_forms(conn)

    conn.logout()


if __name__ == "__main__":
    main()

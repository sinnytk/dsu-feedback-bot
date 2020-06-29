import conf
import email
from imaplib import IMAP4


def main():
    # opening a connection and connecting to mail server with IMAP
    conn = IMAP4('mail.dsu.edu.pk')
    # using credentials defined in conf.py to connect
    conn.login(conf.username, conf.password)

    # selecting the "inbox" mailbox
    conn.select('inbox')

    conn.logout()


if __name__ == "__main__":
    main()

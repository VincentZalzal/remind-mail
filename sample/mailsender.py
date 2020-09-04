import keyring
from smtplib import SMTP_SSL
from getpass import getpass
from email.message import EmailMessage

class MailSender:
    def __init__(self, from_email, host, port=465, passive=False):
        self.from_email = from_email
        pw = keyring.get_password('remind-mail', from_email) # TODO could raise exception
        
        if pw is None:
            if passive:
                pass # TODO, raise exception?
            else:
                pw = getpass(f"Password for user '{from_email}': ")
                keyring.set_password('remind-mail', from_email, pw) # TODO could raise exception
                
        self.smtp = SMTP_SSL(host, port) # TODO could raise exception
        self.smtp.login(from_email, pw) # TODO could raise exception
        # TODO pw could be wrong; keyring.delete_password, then if not passive, loop and ask for password again

    def send(self, to_email, subject, body=''):
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email
        self.smtp.send_message(msg)

    def quit(self):
        self.smtp.quit() # TODO could raise exception?

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.quit()

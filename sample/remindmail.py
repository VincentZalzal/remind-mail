from mailsender import MailSender

def main():
    with MailSender(from_email='vzalzal@vzalzal.com', host='mail.vzalzal.com') as sender:
        sender.send('vincent.zalzal@gmail.com', '[REM] Test 4')

if __name__ == '__main__':
    main()

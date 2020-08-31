import gmailserv

def main():
    serv = gmailserv.get_service()
    msg = gmailserv.create_message(
        sender='vincent.zalzal@gmail.com',
        to='vincent.zalzal@gmail.com',
        subject='[REM] Test 2',
        message_text=''
        )
    gmailserv.send_message(serv, msg)

if __name__ == '__main__':
    main()

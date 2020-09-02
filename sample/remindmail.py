import gmailserv

def main():
    serv = gmailserv.get_service()
    gmailserv.send_to_self(
        serv,
        "vincent.zalzal@gmail.com",
        '[REM] Test 3')

if __name__ == '__main__':
    main()

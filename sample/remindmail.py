from mailsender import MailSender
from datetime import datetime, timedelta
import calendrical
import re
import argparse
import json
import os.path

_datetime_format = '%Y-%m-%d %H:%M'
_datetime_regex_str = r"\d\d\d\d-\d\d-\d\d \d\d:\d\d"

def get_datetime():
    return datetime.now().replace(second=0, microsecond=0)

def get_last_update_datetime_from_log(logname):
    last_update_regex = re.compile(_datetime_regex_str + r": last updated on (" + _datetime_regex_str + ")")
    last_update_datetime_str = None
    try:
        with open(logname) as f:
            for line in f:
                match = last_update_regex.match(line)
                if match is not None:
                    last_update_datetime_str = match.group(1)
    except FileNotFoundError:
        pass

    if last_update_datetime_str is not None:
        return datetime.strptime(last_update_datetime_str, _datetime_format)
    else:
        return None

def log(logfile, string, verbose=True):
    log_datetime_str = get_datetime().strftime(_datetime_format)
    log_str = f'{log_datetime_str}: ' + string + '\n'
    print(f'log: {log_str}', end='')
    logfile.write(log_str)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['generate', 'check', 'send'], help='action to perform')
    parser.add_argument('config_filename', help='name of the JSON configuration file')
    args = parser.parse_args()
    
    if args.action == 'generate':
        pass #TODO handle generate option to create barebone json file

    with open(args.config_filename) as f:
        config = json.load(f)

    log_filename = os.path.splitext(args.config_filename)[0] + '.log'

    start_datetime = get_last_update_datetime_from_log(log_filename)
    end_datetime = get_datetime()

    with open(log_filename, 'a') as logfile:
        if start_datetime is None:
            start_datetime = end_datetime
            log(logfile, f'last updated on {end_datetime.strftime(_datetime_format)}', verbose=False)

        start_datetime = start_datetime + timedelta(minutes=1)
        calendrical.add_next_dates_and_times(config, start_datetime)

        if args.action == 'check':
            messages = calendrical.next_dates(config)
            print(f'JSON is valid.')
            if messages:
                print('\nNext messages:')
                for message in messages:
                    print(f"  {message['when'].strftime(_datetime_format)}   {message['rule']}")
                print('')
            with MailSender(from_email=config['smtp_email'], host=config['smtp_host']) as sender:
                pass # validate password only
            print(f'SMTP credentials are valid.')

        if args.action == 'send':
            log(logfile, f'starting from {start_datetime.strftime(_datetime_format)}')
            messages = calendrical.messages_before(config, end_datetime)
            if messages:
                log(logfile, f'connecting to SMTP server')
                with MailSender(from_email=config['smtp_email'], host=config['smtp_host'], passive=True) as sender:
                    for message in messages:
                        log(logfile, f"sending {message['subject']} to {config['recipient_email']}")
                        sender.send(config['recipient_email'], message['subject'], message['body'])
            log(logfile, f'last updated on {end_datetime.strftime(_datetime_format)}')

        #TODO add support for enabled=false rules in calendrical
        #TODO smtp port in config
        #TODO send and log everything (passive), don't forget try catch then log
        #TODO check what happens when credentials are not valid (both for check and send)
        #TODO better help message

if __name__ == '__main__':
    main()

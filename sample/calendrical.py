from datetime import datetime, date, timedelta
from calendar import monthrange
import re

def days_in_month(the_date):
    return monthrange(the_date.year, the_date.month)[1]

def replace_signed_day(the_date, day):
    assert -28 <= day <= 28 and day != 0
    if day < 0:
        pos_day = days_in_month(the_date) + 1 + day
        return the_date.replace(day=pos_day)
    else:
        return the_date.replace(day=day)

def to_month_number(the_date):
    return the_date.year * 12 + the_date.month - 1

def from_month_number(month_number, day = 1):
    return date(month_number//12, month_number%12 + 1, day)

def add_months(the_date, months):
    return from_month_number(to_month_number(the_date) + months, the_date.day)

def diff_months(date1, date2):
    '''Returns date1 - date2 in months, ignoring the days of the dates'''
    return to_month_number(date1) - to_month_number(date2)

def first_of_next_month(the_date):
    return add_months(the_date.replace(day=1), 1)

def get_time(config, time_str):
    safe_time_str = time_str if time_str is not None else config['default_time']
    aliases = config.get('time_aliases', {})
    resolved_time_str = aliases.get(safe_time_str, safe_time_str)
    return datetime.strptime(resolved_time_str, '%H:%M').time()

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date() if date_str is not None else None

def next_date_daily(min_date, freq = 1, start_date = None):
    assert freq >= 1
    assert start_date is None or start_date <= min_date
    raise Exception('Not implemented yet') # TODO implement

def next_date_weekly(min_date, days, freq = 1, start_date = None):
    assert len(days) >= 1
    assert sorted(days) == days
    assert freq >= 1
    assert start_date is None or start_date <= min_date
    
    weekday = min_date.weekday()
    days_to_next_weekday = min( (day - weekday) % 7 for day in days)
    next_date = min_date + timedelta(days=days_to_next_weekday)
    
    if freq > 1:
        assert len(days) == 1
        assert start_date is not None
        assert start_date.weekday() == days[0]
        assert start_date <= min_date and min_date <= next_date
        assert next_date.weekday() == start_date.weekday()
        num_elapsed_weeks = (next_date - start_date).days // 7
        weeks_to_add = -num_elapsed_weeks % freq
        next_date = next_date + timedelta(days = weeks_to_add*7)
    
    return next_date

def next_date_monthly_on_day(min_date, day, freq = 1, start_date = None):
    assert freq >= 1
    assert start_date is None or start_date <= min_date
    assert -28 <= day <= 28 and day != 0

    # Assume freq == 1 for now; will it happen this month, or next month?
    next_date = replace_signed_day(min_date, day)
    if next_date < min_date:
        # must call replace_signed_day again, because negative day depends on number of days on the month
        next_date = replace_signed_day(first_of_next_month(min_date), day)
    
    if freq > 1:
        assert start_date is not None
        num_elapsed_months = diff_months(next_date, start_date)
        months_to_add = -num_elapsed_months % freq
        # must call replace_signed_day again, because negative day depends on number of days on the month
        next_date = replace_signed_day(add_months(next_date.replace(day=1), months_to_add), day)

    assert next_date >= min_date
    return next_date

    raise Exception('Not implemented yet') # TODO implement

def next_date_monthly_on_week(min_date, weekday, weeknum, freq = 1, start_date = None):
    assert freq >= 1
    assert start_date is None or start_date <= min_date
    raise Exception('Not implemented yet') # TODO implement

def next_date_yearly(min_date, freq, start_date):
    assert freq >= 1
    assert not (start_date.month == 2 and start_date.day == 29)

    # how many multiple of freq years must I add to start_date so that it is >= min_date?
    next_date = start_date
    while next_date < min_date:
        next_date = next_date.replace(year=next_date.year + freq)
    return next_date

class ReMatcher:
    def __init__(self):
        self.match = None
    def matches(self, regex, text):
        self.match = regex.match(text)
        return self.match is not None

_weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

class RegexList:
    def __init__(self):
        self.daily = re.compile(r"(\d+ )?days?")
        self.weekly = re.compile(r"(\d+ )?weeks? on ([a-z]+)")
        self.monthly_on_day = re.compile(r"(\d+ )?months? on day (-?\d+)")
        self.monthly_on_week = re.compile(r"(\d+ )?months? on ([a-z]+) (-?\d)")
        self.yearly = re.compile(r"(\d+ )?years?")

_regexes = RegexList()

def parse_when(when_str):
    '''Return tuple (func, {args})'''
    when_str_lc = when_str.lower()
    matcher = ReMatcher()
    if matcher.matches(_regexes.daily, when_str_lc):
        freq = int(matcher.match.group(1)) if matcher.match.group(1) is not None else 1
        return (next_date_daily, {'freq': freq})
    elif when_str_lc in _weekdays:
        return (next_date_weekly, {'days': [_weekdays.index(when_str_lc)]})
    elif when_str_lc == 'weekday':
        return (next_date_weekly, {'days': [0,1,2,3,4]})
    elif matcher.matches(_regexes.weekly, when_str_lc):
        freq = int(matcher.match.group(1)) if matcher.match.group(1) is not None else 1
        day = _weekdays.index(matcher.match.group(2))
        return (next_date_weekly, {'freq': freq, 'days': [day]})
    elif matcher.matches(_regexes.monthly_on_day, when_str_lc):
        freq = int(matcher.match.group(1)) if matcher.match.group(1) is not None else 1
        day = int(matcher.match.group(2))
        return (next_date_monthly_on_day, {'freq': freq, 'day': day})
    elif matcher.matches(_regexes.monthly_on_week, when_str_lc):
        freq = int(matcher.match.group(1)) if matcher.match.group(1) is not None else 1
        weekday = _weekdays.index(matcher.match.group(2))
        weeknum = int(matcher.match.group(3))
        return (next_date_monthly_on_week, {'freq': freq, 'weekday': weekday, 'weeknum': weeknum})
    elif matcher.matches(_regexes.yearly, when_str_lc):
        freq = int(matcher.match.group(1)) if matcher.match.group(1) is not None else 1
        return (next_date_yearly, {'freq': freq})
    else:
        raise Exception(f"Unable to parse '{when_str}'") # TODO parse 'every monday, wednesday' (list of days)

def find_next_date(min_date, when_str, rule_start_date = None):
    '''Parse "every" string, then defer to appropriate calendrical method'''
    assert rule_start_date is None or rule_start_date <= min_date
    func, args = parse_when(when_str)
    return func(min_date, start_date=rule_start_date, **args)

def add_next_date(rule, start_datetime):
    min_date = start_datetime.date()
    if start_datetime.time() > rule['_rule_time']:
        min_date = min_date + timedelta(days=1)
    rule_start_date = parse_date(rule.get('start_date'))
    if rule_start_date is not None and rule_start_date > min_date:
        min_date = rule_start_date
    
    next_date = find_next_date(min_date, rule['every'], rule_start_date)

    rule_end_date = parse_date(rule.get('end_date'))
    if rule_end_date is not None and rule_end_date < next_date:
        next_date = None

    rule['_next_date'] = next_date

def add_next_dates_and_times(config, start_datetime):
    for rule in config['rules']:
        rule['_rule_time'] = get_time(config, rule.get('time'))
        add_next_date(rule, start_datetime)

def is_before(rule, end_datetime):
    next_date = rule['_next_date']
    if next_date is None:
        return False
    next_datetime = datetime.combine(next_date, rule['_rule_time'])
    return next_datetime <= end_datetime

def messages_before(config, end_datetime):
    messages = []
    for rule in config['rules']:
        if is_before(rule, end_datetime):
            messages.append({key: rule.get(key, '') for key in ['subject', 'body']})
    return messages

def next_dates(config):
    messages = []
    for rule in config['rules']:
        if rule['_next_date'] is not None:
            messages.append({'rule': rule['subject'], 'when': datetime.combine(rule['_next_date'], rule['_rule_time'])})
    return messages

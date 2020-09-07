from datetime import datetime, timedelta
import re

def get_time(config, time_str):
    safe_time_str = time_str if time_str is not None else config['default_time']
    aliases = config.get('time_aliases', {})
    resolved_time_str = aliases.get(safe_time_str, safe_time_str)
    return datetime.strptime(resolved_time_str, '%H:%M').time()

def get_datetime(date_str, time):
    if date_str is not None:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        return datetime.combine(date, time)
    else:
        return None

def next_time(min_datetime, rule_time):
    '''Return first datetime >= min_datetime where time == rule_time'''
    date = min_datetime.date()
    if min_datetime.time() > rule_time:
        date = date + timedelta(days=1)
    return datetime.combine(date, rule_time)

def next_datetime_weekly(min_datetime, days, freq = 1, start_datetime = None):
    assert len(days) >= 1
    assert sorted(days) == days
    assert freq >= 1
    
    days_to_next_weekday = min( (day - min_datetime.weekday()) % 7 for day in days)
    next_datetime = min_datetime + timedelta(days=days_to_next_weekday)
    
    if freq > 1:
        assert len(days) == 1
        assert start_datetime is not None
        assert start_datetime.weekday() == days[0]
        assert start_datetime <= min_datetime and min_datetime <= next_datetime
        assert next_datetime.weekday() == start_datetime.weekday()
        num_elapsed_weeks = (next_datetime - start_datetime).days // 7
        weeks_to_add = -num_elapsed_weeks % freq
        next_datetime = next_datetime + timedelta(days = weeks_to_add*7)
    
    return next_datetime

def next_datetime_monthly_on_day(min_datetime, day, freq = 1, start_datetime = None):
    raise Exception('Not implemented yet') # TODO implement

def next_datetime_yearly(min_datetime, freq, start_datetime):
    assert freq >= 1
    assert not (start_datetime.month == 2 and start_datetime.day == 29)

    # how many multiple of freq years must I add to start_datetime so that it is >= min_datetime?
    next_datetime = start_datetime
    while next_datetime < min_datetime:
        next_datetime = next_datetime.replace(year=next_datetime.year + freq)
    return next_datetime

class ReMatcher:
    def __init__(self):
        self.match = None
    def matches(self, regex, text):
        self.match = regex.match(text)
        return self.match is not None

_weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

class RegexList:
    def __init__(self):
        self.weekly = re.compile(r"(\d+ )?weeks? on ([a-z]+)")
        self.monthly_on_day = re.compile(r"(\d+ )?months? on day (-?\d+)")
        self.yearly = re.compile(r"(\d+ )?years?")

_regexes = RegexList()

def parse_when(when_str):
    '''Return tuple (func, {args})'''
    when_str_lc = when_str.lower()
    matcher = ReMatcher()
    if when_str_lc in _weekdays:
        return (next_datetime_weekly, {'days': [_weekdays.index(when_str_lc)]})
    elif when_str_lc == 'weekday':
        return (next_datetime_weekly, {'days': [0,1,2,3,4]})
    elif matcher.matches(_regexes.weekly, when_str_lc):
        freq = int(matcher.match.group(1)) if matcher.match.group(1) is not None else 1
        day = _weekdays.index(matcher.match.group(2))
        return (next_datetime_weekly, {'freq': freq, 'days': [day]})
    elif matcher.matches(_regexes.monthly_on_day, when_str_lc):
        freq = int(matcher.match.group(1)) if matcher.match.group(1) is not None else 1
        day = int(matcher.match.group(2))
        return (next_datetime_monthly_on_day, {'freq': freq, 'day': day})
    elif matcher.matches(_regexes.yearly, when_str_lc):
        freq = int(matcher.match.group(1)) if matcher.match.group(1) is not None else 1
        return (next_datetime_yearly, {'freq': freq})
    else:
        raise Exception(f"Unable to parse '{when_str}'") # TODO implement (switch on rule type: 'day N')

def find_next_datetime(min_datetime, when_str, rule_start_datetime = None):
    '''Parse "every" string, then defer to appropriate calendrical method'''
    func, args = parse_when(when_str)
    return func(min_datetime, start_datetime=rule_start_datetime, **args)

def add_next_datetime(rule, start_datetime):
    rule_time = rule['_rule_time']
    rule_start_datetime = get_datetime(rule.get('start_date'), rule_time)
    min_datetime = start_datetime if rule_start_datetime is None else max(start_datetime, rule_start_datetime)
    min_datetime = next_time(min_datetime, rule_time)
    rule['_next_datetime'] = find_next_datetime(min_datetime, rule['every'], rule_start_datetime)

def add_next_dates(config, start_datetime):
    for rule in config['rules']:
        rule['_rule_time'] = get_time(config, rule.get('time'))
        add_next_datetime(rule, start_datetime)

def is_before(rule, end_datetime):
    rule_end_datetime = get_datetime(rule.get('end_date'), rule['_rule_time'])
    max_datetime = end_datetime if rule_end_datetime is None else min(end_datetime, rule_end_datetime)
    next_datetime = rule['_next_datetime']
    return next_datetime <= max_datetime

def messages_before(config, end_datetime):
    messages = []
    for rule in config['rules']:
        if is_before(rule, end_datetime):
            messages.append({key: rule[key] for key in ['subject', 'body']})
    return messages

def next_dates(config):
    messages = []
    for rule in config['rules']:
        messages.append({'rule': rule['subject'], 'date': rule['_next_datetime']})
    # TODO messages sort chronologically
    return messages

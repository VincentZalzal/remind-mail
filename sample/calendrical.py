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

def next_datetime_weekly(min_datetime, day_idx):
    days_to_next_weekday = (day_idx - min_datetime.weekday()) % 7
    return min_datetime + timedelta(days=days_to_next_weekday)

def next_datetime_yearly(min_datetime, when_str):
    date = datetime.strptime(when_str, '%m-%d')
    next_datetime = min_datetime.replace(month=date.month, day=date.day)
    if next_datetime < min_datetime:
        # Add a year safely. In theory, not needed, as strptime('%m-%d') does not allow 02-29
        if next_datetime.month == 2 and next_datetime.day == 29:
            next_datetime = next_datetime.replace(month=3, day=1)
        next_datetime = next_datetime.replace(year = next_datetime.year + 1)
    return next_datetime

class ReMatcher:
    def __init__(self):
        self.last_match = None
    def match(self, regex, text):
        self.last_match = regex.match(text)
        return self.last_match

_weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

class RegexList:
    def __init__(self):
        self.yearly = re.compile(r"\d?\d-\d?\d")

_regexes = RegexList()

def parse_when(when_str):
    '''Return tuple (func, {args})'''
    when_str_lc = when_str.lower()
    matcher = ReMatcher()
    if when_str_lc in _weekdays:
        return (next_datetime_weekly, {'day_idx': _weekdays.index(when_str_lc)})
    elif matcher.match(_regexes.yearly, when_str_lc) is not None:
        return (next_datetime_yearly, {'when_str': when_str})
    else:
        raise Exception(f"Unable to parse '{when_str}'") # TODO implement (switch on rule type: 'day N')

def find_next_datetime(min_datetime, when_str, rule_start_datetime = None):
    '''Parse "every" string, then defer to appropriate calendrical method'''
    func, args = parse_when(when_str)
    return func(min_datetime, **args)

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

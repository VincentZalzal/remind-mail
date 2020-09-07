from datetime import datetime, timedelta
import re

_weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

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

def find_next_datetime(min_datetime, when_str, rule_start_datetime = None):
    '''Parse "every" string, then defer to appropriate calendrical method'''
    if when_str in _weekdays: # TODO make case-insensitive
        return next_datetime_weekly(min_datetime, _weekdays.index(when_str))
    elif re.match(r"\d?\d-\d?\d", when_str) is not None:
        return next_datetime_yearly(min_datetime, when_str)
    else:
        return min_datetime # TODO implement (switch on rule type: 'day N')

def message_to_add(rule, start_datetime, end_datetime):
    rule_time = get_time(config, rule.get('time'))
    rule_start_datetime = get_datetime(rule.get('start_date'), rule_time)
    rule_end_datetime = get_datetime(rule.get('end_date'), rule_time)
    min_datetime = start_datetime if rule_start_datetime is None else max(start_datetime, rule_start_datetime)
    min_datetime = next_time(min_datetime, rule_time)
    max_datetime = end_datetime if rule_end_datetime is None else min(end_datetime, rule_end_datetime)

    next_datetime = find_next_datetime(min_datetime, rule['every'], rule_start_datetime)
    if next_datetime <= max_datetime:
        return {key: rule[key] for key in ['subject', 'body']}
    else:
        return None

def messages_between(config, start_datetime, end_datetime):
    messages = []

    for rule in config['rules']:
        msg = message_to_add(rule, start_datetime, end_datetime)
        if msg is not None:
            messages.append(msg)

    return messages

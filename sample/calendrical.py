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

def find_first_datetime(rule_time, min_datetime):
    first_date = min_datetime.date()
    if min_datetime.time() > rule_time:
        first_date = first_date + timedelta(days=1)
    return datetime.combine(first_date, rule_time)

def find_next_datetime_weekly(day_idx, first_datetime):
    days_to_next_weekday = (day_idx - first_datetime.weekday()) % 7
    return first_datetime + timedelta(days=days_to_next_weekday)

def find_next_datetime_yearly(when_str, first_datetime):
    date = datetime.strptime(when_str, '%m-%d')
    next_datetime = first_datetime.replace(month=date.month, day=date.day)
    if next_datetime < first_datetime:
        # Add a year safely. In theory, not needed, as strptime('%m-%d') does not allow 02-29
        if next_datetime.month == 2 and next_datetime.day == 29:
            next_datetime = next_datetime.replace(month=3, day=1)
        next_datetime = next_datetime.replace(year = next_datetime.year + 1)
    return next_datetime

def find_next_datetime(when_str, rule_start_datetime, rule_time, min_datetime):
    # rule_start_datetime may be None
    first_datetime = find_first_datetime(rule_time, min_datetime)
    if when_str in _weekdays:
        return find_next_datetime_weekly(_weekdays.index(when_str), first_datetime)
    elif re.match(r"\d?\d-\d?\d", when_str) is not None:
        return find_next_datetime_yearly(when_str, first_datetime)
    else:
        return min_datetime # TODO implement (switch on rule type: 'day N')

def message_to_add(rule, start_datetime, end_datetime):
    rule_time = get_time(config, rule.get('time'))
    rule_start_datetime = get_datetime(rule.get('start_date'), rule_time)
    rule_end_datetime = get_datetime(rule.get('end_date'), rule_time)
    min_datetime = start_datetime if rule_start_datetime is None else max(start_datetime, rule_start_datetime)
    max_datetime = end_datetime if rule_end_datetime is None else min(end_datetime, rule_end_datetime)

    next_datetime = find_next_datetime(rule['every'], rule_start_datetime, rule_time, min_datetime)
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

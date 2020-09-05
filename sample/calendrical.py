from datetime import datetime

def get_time(config, time_str):
    safe_time_str = time_str if time_str is not None else config['default_time']
    aliases = config.get('time_aliases', {})
    resolved_time_str = aliases.get(safe_time_str, safe_time_str)
    return datetime.strptime(resolved_time_str, '%H:%M').time()

def get_datetime(rule, date_name, time):
    date_str = rule.get(date_name)
    if date_str is None:
        return None
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    return datetime.combine(date, time)

def find_next_date(rule, start):
    next_date = start # TODO implement (switch on rule type)
    return next_date

def message_to_add(rule, start_datetime, end_datetime):
    time = get_time(config, rule.get('time'))
    rule_start = get_datetime(rule, 'start_date', time)
    rule_end = get_datetime(rule, 'end_date', time)
    start = start_datetime if rule_start is None else max(start_datetime, rule_start)
    end = end_datetime if rule_end is None else min(end_datetime, rule_end)

    next_date = find_next_date(rule, start)
    if next_date <= end:
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

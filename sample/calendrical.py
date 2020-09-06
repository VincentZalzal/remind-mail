from datetime import datetime

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

def find_next_datetime(when_str, rule_start_datetime, rule_time, min_datetime):
    # rule_start_datetime may be None
    next_datetime = min_datetime # TODO implement (switch on rule type)
    return next_datetime

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

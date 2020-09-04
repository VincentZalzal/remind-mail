import datetime

def get_time(config, time_str):
    safe_time_str = time_str if time_str is not None else config['default_time']
    aliases = config.get('time_aliases', {})
    resolved_time_str = aliases.get(safe_time_str, safe_time_str)
    return datetime.datetime.strptime(resolved_time_str, '%H:%M').time()

def messages_between(config, start_datetime, end_datetime):
    for rule in config['rules']:
        time = get_time(config, rule.get('time'))
        #   must add time to the dates in the rule...
        #start = max(start_datetime, rule.get('start_date', start_datetime))
        #end = min(end_datetime, rule.get('end_date', end_datetime))
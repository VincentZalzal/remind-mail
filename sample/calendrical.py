import datetime

def get_time(config, time_str):
    safe_time_str = time_str if time_str is not None else config['default_time']
    aliases = config.get('time_aliases', {})
    resolved_time_str = aliases.get(safe_time_str, safe_time_str)
    return datetime.datetime.strptime(resolved_time_str, '%H:%M').time()

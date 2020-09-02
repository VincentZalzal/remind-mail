import datetime

def get_time(config, time_str):
    aliases = config.get('time_aliases', {})
    resolved_time_str = aliases.get(time_str, time_str)
    return datetime.datetime.strptime(resolved_time_str, '%H:%M').time()

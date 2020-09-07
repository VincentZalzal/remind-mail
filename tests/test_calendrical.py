from .context import sample
import sample.calendrical
from datetime import datetime, time, timedelta

def test_get_time():
    config = {
        'time_aliases': {
            'morning': '8:12',
            'evening': '21:34',
            },
        }

    assert sample.calendrical.get_time({}, '9:31') == time(9, 31)
    assert sample.calendrical.get_time(config, '9:31') == time(9, 31)
    assert sample.calendrical.get_time(config, 'morning') == time(8, 12)
    assert sample.calendrical.get_time(config, 'evening') == time(21, 34)

def test_get_time_default():
    config = {
        'default_time': '10:12',
        'time_aliases': {
            'morning': '8:12',
            'evening': '21:34',
            },
        }
    
    assert sample.calendrical.get_time(config, '9:31') == time(9, 31)
    assert sample.calendrical.get_time(config, None) == time(10, 12)

    config['default_time'] = 'evening'
    assert sample.calendrical.get_time(config, None) == time(21, 34)

def test_get_datetime():
    assert sample.calendrical.get_datetime('2020-09-05', time(10, 12)) == datetime(2020, 9, 5, 10, 12)
    assert sample.calendrical.get_datetime('2021-10-10', time(11, 12)) == datetime(2021, 10, 10, 11, 12)
    assert sample.calendrical.get_datetime(None, time(12, 12)) is None

def test_next_time():
    min_datetime = datetime(2020, 9, 17, 8, 15)
    assert sample.calendrical.next_time(min_datetime, time(8, 15)) == min_datetime
    assert sample.calendrical.next_time(min_datetime, time(7, 20)) == datetime(2020, 9, 18, 7, 20)
    assert sample.calendrical.next_time(min_datetime, time(9, 10)) == datetime(2020, 9, 17, 9, 10)

def test_next_datetime_weekly():
    thursday = datetime(2020, 9, 17, 8, 15) # idx = 3
    assert sample.calendrical.next_datetime_weekly(thursday, [3]) == thursday
    assert sample.calendrical.next_datetime_weekly(thursday, [4]) == thursday + timedelta(days=1)
    assert sample.calendrical.next_datetime_weekly(thursday, [2]) == thursday + timedelta(days=6)

    assert sample.calendrical.next_datetime_weekly(thursday, [3, 4]) == thursday
    assert sample.calendrical.next_datetime_weekly(thursday, [1, 3]) == thursday

    assert sample.calendrical.next_datetime_weekly(thursday, [4, 5]) == thursday + timedelta(days=1)
    assert sample.calendrical.next_datetime_weekly(thursday, [1, 4]) == thursday + timedelta(days=1)
    assert sample.calendrical.next_datetime_weekly(thursday, [1, 2]) == thursday + timedelta(days=5)

    assert sample.calendrical.next_datetime_weekly(thursday, [3], freq=3, start_datetime=thursday) == thursday
    assert sample.calendrical.next_datetime_weekly(thursday, [3], freq=3, start_datetime=thursday - timedelta(days=3*7)) == thursday
    assert sample.calendrical.next_datetime_weekly(thursday, [3], freq=3, start_datetime=thursday - timedelta(days=2*7)) == thursday + timedelta(days=1*7)
    assert sample.calendrical.next_datetime_weekly(thursday, [3], freq=3, start_datetime=thursday - timedelta(days=4*7)) == thursday + timedelta(days=2*7)

    assert sample.calendrical.next_datetime_weekly(thursday - timedelta(days=5), [3], freq=3, start_datetime=thursday - timedelta(days=4*7)) == thursday + timedelta(days=2*7)

def test_next_datetime_yearly():
    rule_datetime = datetime(2020, 9, 17, 8, 15)
    assert sample.calendrical.next_datetime_yearly(rule_datetime, 1, rule_datetime) == rule_datetime
    assert sample.calendrical.next_datetime_yearly(datetime(2020, 6, 20, 8, 15), 1, rule_datetime) == rule_datetime
    assert sample.calendrical.next_datetime_yearly(datetime(2021, 6, 20, 8, 15), 1, rule_datetime) == rule_datetime.replace(year=2021)
    assert sample.calendrical.next_datetime_yearly(datetime(2021, 10, 5, 8, 15), 1, rule_datetime) == rule_datetime.replace(year=2022)

    assert sample.calendrical.next_datetime_yearly(rule_datetime, 3, rule_datetime) == rule_datetime
    assert sample.calendrical.next_datetime_yearly(datetime(2020, 6, 20, 8, 15), 3, rule_datetime) == rule_datetime
    assert sample.calendrical.next_datetime_yearly(datetime(2021, 6, 20, 8, 15), 3, rule_datetime) == rule_datetime.replace(year=2023)
    assert sample.calendrical.next_datetime_yearly(datetime(2021, 10, 5, 8, 15), 3, rule_datetime) == rule_datetime.replace(year=2023)
    assert sample.calendrical.next_datetime_yearly(rule_datetime.replace(year=2023), 3, rule_datetime) == rule_datetime.replace(year=2023)

def test_parse_when():
    assert sample.calendrical.parse_when('tuesday') == (sample.calendrical.next_datetime_weekly, {'days': [1]})
    assert sample.calendrical.parse_when('weekday') == (sample.calendrical.next_datetime_weekly, {'days': [0,1,2,3,4]})
    assert sample.calendrical.parse_when('week on friday') == (sample.calendrical.next_datetime_weekly, {'freq': 1, 'days': [4]})
    assert sample.calendrical.parse_when('3 weeks on friday') == (sample.calendrical.next_datetime_weekly, {'freq': 3, 'days': [4]})
    assert sample.calendrical.parse_when('year') == (sample.calendrical.next_datetime_yearly, {'freq': 1})
    assert sample.calendrical.parse_when('12 years') == (sample.calendrical.next_datetime_yearly, {'freq': 12})

def test_find_next_datetime():
    thursday = datetime(2020, 9, 17, 8, 15)
    assert sample.calendrical.find_next_datetime(thursday, 'Wednesday') == thursday + timedelta(days=6)
    assert sample.calendrical.find_next_datetime(thursday + timedelta(days=2), 'weekday') == thursday + timedelta(days=4)
    assert sample.calendrical.find_next_datetime(thursday, '3 weeks on friday', datetime(2020, 9, 11, 8, 15)) == datetime(2020, 10, 2, 8, 15)
    assert sample.calendrical.find_next_datetime(thursday, '3 years', datetime(2020, 8, 11, 10, 0)) == datetime(2023, 8, 11, 10, 0)
    # TODO more tests here

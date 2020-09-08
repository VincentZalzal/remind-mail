from .context import sample
import sample.calendrical
from datetime import datetime, date, time, timedelta

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

def test_parse_date():
    assert sample.calendrical.parse_date('2020-09-05') == date(2020, 9, 5)
    assert sample.calendrical.parse_date('2021-10-10') == date(2021, 10, 10)
    assert sample.calendrical.parse_date(None) is None

def test_next_date_weekly():
    thursday = date(2020, 9, 17) # idx = 3
    assert sample.calendrical.next_date_weekly(thursday, [3]) == thursday
    assert sample.calendrical.next_date_weekly(thursday, [4]) == thursday + timedelta(days=1)
    assert sample.calendrical.next_date_weekly(thursday, [2]) == thursday + timedelta(days=6)

    assert sample.calendrical.next_date_weekly(thursday, [3, 4]) == thursday
    assert sample.calendrical.next_date_weekly(thursday, [1, 3]) == thursday

    assert sample.calendrical.next_date_weekly(thursday, [4, 5]) == thursday + timedelta(days=1)
    assert sample.calendrical.next_date_weekly(thursday, [1, 4]) == thursday + timedelta(days=1)
    assert sample.calendrical.next_date_weekly(thursday, [1, 2]) == thursday + timedelta(days=5)

    assert sample.calendrical.next_date_weekly(thursday, [3], freq=3, start_date=thursday) == thursday
    assert sample.calendrical.next_date_weekly(thursday, [3], freq=3, start_date=thursday - timedelta(days=3*7)) == thursday
    assert sample.calendrical.next_date_weekly(thursday, [3], freq=3, start_date=thursday - timedelta(days=2*7)) == thursday + timedelta(days=1*7)
    assert sample.calendrical.next_date_weekly(thursday, [3], freq=3, start_date=thursday - timedelta(days=4*7)) == thursday + timedelta(days=2*7)

    assert sample.calendrical.next_date_weekly(thursday - timedelta(days=5), [3], freq=3, start_date=thursday - timedelta(days=4*7)) == thursday + timedelta(days=2*7)

def test_next_date_yearly():
    rule_date = date(2020, 9, 17)
    assert sample.calendrical.next_date_yearly(rule_date, 1, rule_date) == rule_date
    assert sample.calendrical.next_date_yearly(date(2020, 6, 20), 1, rule_date) == rule_date
    assert sample.calendrical.next_date_yearly(date(2021, 6, 20), 1, rule_date) == rule_date.replace(year=2021)
    assert sample.calendrical.next_date_yearly(date(2021, 10, 5), 1, rule_date) == rule_date.replace(year=2022)

    assert sample.calendrical.next_date_yearly(rule_date, 3, rule_date) == rule_date
    assert sample.calendrical.next_date_yearly(date(2020, 6, 20), 3, rule_date) == rule_date
    assert sample.calendrical.next_date_yearly(date(2021, 6, 20), 3, rule_date) == rule_date.replace(year=2023)
    assert sample.calendrical.next_date_yearly(date(2021, 10, 5), 3, rule_date) == rule_date.replace(year=2023)
    assert sample.calendrical.next_date_yearly(rule_date.replace(year=2023), 3, rule_date) == rule_date.replace(year=2023)

def test_parse_when():
    assert sample.calendrical.parse_when('day') == (sample.calendrical.next_date_daily, {'freq': 1})
    assert sample.calendrical.parse_when('12 days') == (sample.calendrical.next_date_daily, {'freq': 12})
    assert sample.calendrical.parse_when('tuesday') == (sample.calendrical.next_date_weekly, {'days': [1]})
    assert sample.calendrical.parse_when('weekday') == (sample.calendrical.next_date_weekly, {'days': [0,1,2,3,4]})
    assert sample.calendrical.parse_when('week on friday') == (sample.calendrical.next_date_weekly, {'freq': 1, 'days': [4]})
    assert sample.calendrical.parse_when('3 weeks on friday') == (sample.calendrical.next_date_weekly, {'freq': 3, 'days': [4]})
    assert sample.calendrical.parse_when('month on day 3') == (sample.calendrical.next_date_monthly_on_day, {'freq': 1, 'day': 3})
    assert sample.calendrical.parse_when('2 months on day 13') == (sample.calendrical.next_date_monthly_on_day, {'freq': 2, 'day': 13})
    assert sample.calendrical.parse_when('3 months on day -1') == (sample.calendrical.next_date_monthly_on_day, {'freq': 3, 'day': -1})
    assert sample.calendrical.parse_when('month on friday 1') == (sample.calendrical.next_date_monthly_on_week, {'freq': 1, 'weeknum': 1, 'weekday': 4})
    assert sample.calendrical.parse_when('2 months on tuesday 2') == (sample.calendrical.next_date_monthly_on_week, {'freq': 2, 'weeknum': 2, 'weekday': 1})
    assert sample.calendrical.parse_when('3 months on monday -1') == (sample.calendrical.next_date_monthly_on_week, {'freq': 3, 'weeknum': -1, 'weekday': 0})
    assert sample.calendrical.parse_when('year') == (sample.calendrical.next_date_yearly, {'freq': 1})
    assert sample.calendrical.parse_when('12 years') == (sample.calendrical.next_date_yearly, {'freq': 12})

def test_find_next_date():
    thursday = date(2020, 9, 17)
    assert sample.calendrical.find_next_date(thursday, 'Wednesday') == thursday + timedelta(days=6)
    assert sample.calendrical.find_next_date(thursday + timedelta(days=2), 'weekday') == thursday + timedelta(days=4)
    assert sample.calendrical.find_next_date(thursday, '3 weeks on friday', date(2020, 9, 11)) == date(2020, 10, 2)
    assert sample.calendrical.find_next_date(thursday, '3 years', date(2020, 8, 11)) == date(2023, 8, 11)
    # TODO more tests here

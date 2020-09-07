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

def test_find_first_datetime():
    min_datetime = datetime(2020, 9, 17, 8, 15)
    assert sample.calendrical.find_first_datetime(time(8, 15), min_datetime) == min_datetime
    assert sample.calendrical.find_first_datetime(time(7, 20), min_datetime) == datetime(2020, 9, 18, 7, 20)
    assert sample.calendrical.find_first_datetime(time(9, 10), min_datetime) == datetime(2020, 9, 17, 9, 10)

def test_find_next_datetime_weekly():
    thursday = datetime(2020, 9, 17, 8, 15) # idx = 3
    assert sample.calendrical.find_next_datetime_weekly(3, thursday) == thursday
    assert sample.calendrical.find_next_datetime_weekly(4, thursday) == thursday + timedelta(days=1)
    assert sample.calendrical.find_next_datetime_weekly(2, thursday) == thursday + timedelta(days=6)

def test_find_next_datetime_yearly():
    first_datetime = datetime(2020, 9, 17, 8, 15)
    assert sample.calendrical.find_next_datetime_yearly('9-17', first_datetime) == first_datetime
    assert sample.calendrical.find_next_datetime_yearly('10-17', first_datetime) == first_datetime.replace(month=10)
    assert sample.calendrical.find_next_datetime_yearly('9-18', first_datetime) == first_datetime.replace(day=18)
    assert sample.calendrical.find_next_datetime_yearly('08-17', first_datetime) == first_datetime.replace(year=2021, month=8)
    assert sample.calendrical.find_next_datetime_yearly('09-16', first_datetime) == first_datetime.replace(year=2021, day=16)

def test_find_next_datetime():
    thursday = datetime(2020, 9, 17, 8, 15)
    assert sample.calendrical.find_next_datetime('Wednesday', None, thursday.time(), thursday) == thursday + timedelta(days=6)
    assert sample.calendrical.find_next_datetime('08-11', None, thursday.time(), thursday) == datetime(2021, 8, 11, 8, 15)
    # TODO more tests here

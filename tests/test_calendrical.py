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
    assert sample.calendrical.next_datetime_weekly(thursday, 3) == thursday
    assert sample.calendrical.next_datetime_weekly(thursday, 4) == thursday + timedelta(days=1)
    assert sample.calendrical.next_datetime_weekly(thursday, 2) == thursday + timedelta(days=6)

def test_next_datetime_yearly():
    first_datetime = datetime(2020, 9, 17, 8, 15)
    assert sample.calendrical.next_datetime_yearly(first_datetime, '9-17') == first_datetime
    assert sample.calendrical.next_datetime_yearly(first_datetime, '10-17') == first_datetime.replace(month=10)
    assert sample.calendrical.next_datetime_yearly(first_datetime, '9-18') == first_datetime.replace(day=18)
    assert sample.calendrical.next_datetime_yearly(first_datetime, '08-17') == first_datetime.replace(year=2021, month=8)
    assert sample.calendrical.next_datetime_yearly(first_datetime, '09-16') == first_datetime.replace(year=2021, day=16)

def test_find_next_datetime():
    thursday = datetime(2020, 9, 17, 8, 15)
    assert sample.calendrical.find_next_datetime(thursday, 'Wednesday') == thursday + timedelta(days=6)
    assert sample.calendrical.find_next_datetime(thursday, '08-11') == datetime(2021, 8, 11, 8, 15)
    # TODO more tests here

from .context import sample
import sample.calendrical
from datetime import datetime, time

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
    rule = {
        'start_date': '2020-09-05',
        'end_date': '2021-10-10',
        }

    assert sample.calendrical.get_datetime(rule, 'start_date', time(10, 12)) == datetime(2020, 9, 5, 10, 12)
    assert sample.calendrical.get_datetime(rule, 'end_date', time(11, 12)) == datetime(2021, 10, 10, 11, 12)
    assert sample.calendrical.get_datetime(rule, 'unknown', time(12, 12)) is None

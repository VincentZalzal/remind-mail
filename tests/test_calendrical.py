from .context import sample
import sample.calendrical
import datetime

def test_get_time():
    config = {
        'time_aliases': {
            'morning': '8:12',
            'evening': '21:34'
            }
        }

    assert sample.calendrical.get_time({}, '9:31') == datetime.time(9, 31)
    assert sample.calendrical.get_time(config, '9:31') == datetime.time(9, 31)
    assert sample.calendrical.get_time(config, 'morning') == datetime.time(8, 12)
    assert sample.calendrical.get_time(config, 'evening') == datetime.time(21, 34)
import datetime
from typing import List, Optional, Union

from osxphotos import PhotoInfo
from osxphotos.datetime_utils import datetime_naive_to_local
from osxphotos.phototemplate import RenderOptions

# Translation dictionary for pluralization and language-specific terms
translations = {
    'de': {
        'and': 'und',
        'minute_singular': 'Minute',
        'minute_plural': 'Minuten',
        'hour_singular': 'Stunde',
        'hour_plural': 'Stunden',
        'day_singular': 'Tag',
        'day_plural': 'Tage',
        'week_singular': 'Woche',
        'week_plural': 'Wochen',
        'month_singular': 'Monat',
        'month_plural': 'Monate',
        'year_singular': 'Jahr',
        'year_plural': 'Jahre'
    },
    'en': {
        'and': 'and',
        'minute_singular': 'minute',
        'minute_plural': 'minutes',
        'hour_singular': 'hour',
        'hour_plural': 'hours',
        'day_singular': 'day',
        'day_plural': 'days',
        'week_singular': 'week',
        'week_plural': 'weeks',
        'month_singular': 'month',
        'month_plural': 'months',
        'year_singular': 'year',
        'year_plural': 'years'
    }
}

def pluralize(value: int, singular: str, plural: str) -> str:
    """Return singular or plural based on the value."""
    return f"{value} {singular}" if value == 1 else f"{value} {plural}"

def time_since(
    photo: PhotoInfo, options: RenderOptions, args: Optional[str] = None, **kwargs
) -> Union[List, str]:
    """
    Return the time difference (years, months, weeks, days, hours, minutes) between 
    the photo's date and the date passed as an argument in format YYYY-MM-DD HH:MM,
    including language-specific output.
    """
    if not args:
        raise ValueError(
            "time_since function requires an argument in the form of a date string in the format YYYY-MM-DD HH:MM"
        )
    
    # Split args into date and language if provided
    date_str, language = args.split(",") if "," in args else (args, "en")

    # Parse the input date argument
    try:
        date_arg = datetime_naive_to_local(datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M"))
    except ValueError:
        raise ValueError(
            "time_since function requires an argument in the form of a date string in the format YYYY-MM-DD HH:MM"
        )
    
    if language not in translations:
        raise ValueError(f"Unsupported language: {language}")

    # Calculate the time difference
    return calculate_time_difference(photo.date, date_arg, language)

def calculate_time_difference(start_date: datetime.datetime, end_date: datetime.datetime, language: str) -> str:
    """Helper function to calculate the time difference based on the requirements."""
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # Reset times for days-based calculations as required by the specifications
    start_of_day = lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    delta = end_date - start_date
    total_seconds = delta.total_seconds()

    lang = translations[language]

    # Case 1: Less than an hour, show only full minutes
    if total_seconds < 3600:
        minutes = int(total_seconds // 60)
        return pluralize(minutes, lang['minute_singular'], lang['minute_plural'])

    # Case 2: Less than until the end of the second day (23:59), show only full hours
    elif total_seconds < 86400 * 2:  # 86400 seconds in a day
        hours = int(total_seconds // 3600)
        return pluralize(hours, lang['hour_singular'], lang['hour_plural'])

    # Case 3: Less than a week, count full days (from day start at 00:00)
    elif total_seconds < 604800:  # 604800 seconds in a week
        start_date = start_of_day(start_date)
        end_date = start_of_day(end_date)
        delta = end_date - start_date
        days = delta.days
        return pluralize(days, lang['day_singular'], lang['day_plural'])

    # Case 4: Less than a month, count full weeks (from day start at 00:00)
    elif total_seconds < 2628000:  # Approx. seconds in a month (30.44 days)
        start_date = start_of_day(start_date)
        end_date = start_of_day(end_date)
        delta = end_date - start_date
        weeks = delta.days // 7
        return pluralize(weeks, lang['week_singular'], lang['week_plural'])

    # Case 5: Less than a year, count full months (from day start at 00:00)
    elif total_seconds < 31536000:  # Approx. seconds in a year
        start_date = start_of_day(start_date)
        end_date = start_of_day(end_date)
        delta = end_date - start_date
        months = delta.days // 30  # Approx. days in a month
        return pluralize(months, lang['month_singular'], lang['month_plural'])

    # Case 6: More than a year, count years and months (from day start at 00:00)
    else:
        start_date = start_of_day(start_date)
        end_date = start_of_day(end_date)
        delta = end_date - start_date

        years = delta.days // 365
        remaining_days = delta.days % 365
        months = remaining_days // 30  # Approx. days in a month

        years_str = pluralize(years, lang['year_singular'], lang['year_plural'])
        months_str = pluralize(months, lang['month_singular'], lang['month_plural'])

        if months > 0:
            return f"{years_str} {lang['and']} {months_str}"
        else:
            return years_str

# Example for osxphotos usage:
# osxphotos query --quiet --print "{function:time_since.py::time_since(2020-01-01 14:00,de)}"

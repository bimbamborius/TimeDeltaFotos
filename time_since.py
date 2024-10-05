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
    Return the time difference (years, months, days, hours, minutes) between 
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
    """Helper function to calculate the difference according to specified rules."""
    # Ensure start_date is earlier than end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # Remove time components to compare dates correctly
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

    delta = end_date - start_date
    total_seconds = delta.total_seconds()
    lang = translations[language]

    # Calculate differences based on specified criteria
    if total_seconds < 3600:  # Less than one hour
        minutes = int((end_date - start_date).total_seconds() // 60)
        return pluralize(minutes, lang['minute_singular'], lang['minute_plural'])
    
    elif total_seconds < 86400:  # Less than one day (but after the first hour)
        hours = int((end_date - start_date).total_seconds() // 3600)
        return pluralize(hours, lang['hour_singular'], lang['hour_plural'])

    elif total_seconds < 604800:  # Less than one week
        days = (end_date - start_date).days
        return pluralize(days, lang['day_singular'], lang['day_plural'])

    # For intervals longer than one week
    # Adjust to midnight of the current day to count full weeks
    start_date = start_date.replace(hour=0, minute=0)
    end_date = end_date.replace(hour=0, minute=0)

    if total_seconds < 2628000:  # Less than one month
        weeks = (end_date - start_date).days // 7
        return pluralize(weeks, lang['week_singular'], lang['week_plural'])

    elif total_seconds < 31536000:  # Less than one year
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        return pluralize(months, lang['month_singular'], lang['month_plural'])

    else:  # More than one year
        years = end_date.year - start_date.year
        months = end_date.month - start_date.month
        if months < 0:
            years -= 1
            months += 12
        years_str = pluralize(years, lang['year_singular'], lang['year_plural'])
        months_str = pluralize(months, lang['month_singular'], lang['month_plural'])
        return f"{years_str} {lang['and']} {months_str}"

# Example for osxphotos usage:
# osxphotos query --quiet --print "{function:time_since.py::time_since(2020-01-01 14:00,de)}"

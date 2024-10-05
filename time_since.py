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
    """Helper function to calculate the difference in years, months, days, hours, and minutes between two dates."""
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    delta = end_date - start_date
    total_seconds = delta.total_seconds()

    lang = translations[language]

    # Calculate years
    years = int(total_seconds // 31536000)
    remaining_seconds = total_seconds % 31536000

    # Calculate months
    months = int(remaining_seconds // 2628000)
    remaining_seconds = remaining_seconds % 2628000

    # Calculate days
    days = int(remaining_seconds // 86400)
    remaining_seconds = remaining_seconds % 86400

    # Calculate hours
    hours = int(remaining_seconds // 3600)
    remaining_seconds = remaining_seconds % 3600

    # Calculate minutes
    minutes = int(remaining_seconds // 60)

    # Build the output string with proper pluralization and conjunctions
    output = []

    if years > 0:
        output.append(pluralize(years, lang['year_singular'], lang['year_plural']))
    if months > 0:
        output.append(pluralize(months, lang['month_singular'], lang['month_plural']))
    if days > 0:
        output.append(pluralize(days, lang['day_singular'], lang['day_plural']))
    if hours > 0:
        output.append(pluralize(hours, lang['hour_singular'], lang['hour_plural']))
    if minutes > 0:
        output.append(pluralize(minutes, lang['minute_singular'], lang['minute_plural']))

    # Join the output with the appropriate conjunction ("and"/"und")
    if len(output) > 1:
        return f" {lang['and']} ".join([', '.join(output[:-1]), output[-1]])
    return output[0] if output else ""

# Example for osxphotos usage:
# osxphotos query --quiet --print "{function:time_since.py::time_since(2022-09-24 16:00,de)}"

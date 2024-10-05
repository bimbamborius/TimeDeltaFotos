import datetime
from typing import List, Optional, Union

from osxphotos import PhotoInfo
from osxphotos.datetime_utils import datetime_naive_to_local
from osxphotos.phototemplate import RenderOptions

# Übersetzungen für die Ausgabe in verschiedenen Sprachen
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

    # Berechnung der Zeitdifferenz
    return calculate_time_difference(photo.date, date_arg, language)

def calculate_time_difference(start_date: datetime.datetime, end_date: datetime.datetime, language: str) -> str:
    """Berechnet die Differenz in vollen Jahren, Monaten, Wochen, Tagen, Stunden, Minuten."""
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    # Gesamtzahl der Sekunden
    delta = end_date - start_date
    total_seconds = delta.total_seconds()
    lang = translations[language]
    
    # Weniger als eine Stunde: Nur volle Minuten
    if total_seconds < 3600:
        minutes = int(total_seconds // 60)
        return pluralize(minutes, lang['minute_singular'], lang['minute_plural'])
    
    # Weniger als ein Tag: Nur volle Stunden
    elif total_seconds < 86400:
        hours = int(total_seconds // 3600)
        return pluralize(hours, lang['hour_singular'], lang['hour_plural'])
    
    # Weniger als eine Woche: Nur volle Tage, ab 00:00 Uhr
    elif total_seconds < 604800:
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        delta = end_date - start_date
        total_seconds = delta.total_seconds()
        days = int(total_seconds // 86400)
        return pluralize(days, lang['day_singular'], lang['day_plural'])
    
    # Weniger als ein Monat: Nur volle Wochen, ab 00:00 Uhr
    elif total_seconds < 2628000:
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        delta = end_date - start_date
        total_seconds = delta.total_seconds()
        weeks = int(total_seconds // 604800)
        return pluralize(weeks, lang['week_singular'], lang['week_plural'])
    
    # Weniger als ein Jahr: Nur volle Monate, ab 00:00 Uhr
    elif total_seconds < 31536000:
        start_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        delta = end_date - start_date
        total_seconds = delta.total_seconds()
        months = int(total_seconds // 2628000)
        return pluralize(months, lang['month_singular'], lang['month_plural'])
    
    # Mehr als ein Jahr: Volle Jahre und Monate, ab 00:00 Uhr
    else:
        start_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        delta = end_date - start_date
        total_seconds = delta.total_seconds()
        
        years = int(total_seconds // 31536000)
        remaining_seconds = total_seconds % 31536000
        months = int(remaining_seconds // 2628000)

        years_str = pluralize(years, lang['year_singular'], lang['year_plural'])
        months_str = pluralize(months, lang['month_singular'], lang['month_plural'])
        
        if months > 0:
            return f"{years_str} {lang['and']} {months_str}"
        return years_str

# Beispiel für die Nutzung in osxphotos:
# osxphotos query --quiet --print "{function:time_since.py::time_since(2020-01-01 14:00,de)}"

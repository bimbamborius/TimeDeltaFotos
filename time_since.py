import datetime
from typing import List, Optional, Union

from osxphotos import PhotoInfo
from osxphotos.datetime_utils import datetime_naive_to_local
from osxphotos.phototemplate import RenderOptions

# Übersetzungswörterbuch für Pluralisierungen und sprachspezifische Begriffe
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
    """Gibt die passende Singular- oder Pluralform zurück, basierend auf dem Wert."""
    return f"{value} {singular}" if value == 1 else f"{value} {plural}"

def time_since(
    photo: PhotoInfo, options: RenderOptions, args: Optional[str] = None, **kwargs
) -> Union[List, str]:
    """
    Gibt die Zeitdifferenz zwischen dem Datum des Fotos und dem angegebenen Datum im Format YYYY-MM-DD HH:MM zurück,
    einschließlich sprachspezifischer Ausgabe.
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
    """Helferfunktion zur Berechnung der Differenz in Jahren, Monaten, Tagen, Stunden und Minuten zwischen zwei Daten."""

    # Berechnung der Gesamtsekunden
    total_seconds = (end_date - start_date).total_seconds()

    # Weniger als eine Stunde: volle Minuten zählen
    if total_seconds < 3600:
        minutes = int(total_seconds // 60)
        return pluralize(minutes, translations[language]['minute_singular'], translations[language]['minute_plural'])

    # Setze das Startdatum auf den Beginn des Tages (00:00 Uhr)
    start_date_day_start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Weniger als ein Monat: volle Wochen zählen
    if total_seconds < 2628000:
        # Berechne die Anzahl der vollen Wochen ab Tagesbeginn
        weeks = (end_date - start_date_day_start).days // 7
        return pluralize(weeks, translations[language]['week_singular'], translations[language]['week_plural'])

    # Weniger als ein Jahr: volle Monate zählen
    elif total_seconds < 31536000:
        # Berechne die Anzahl der vollen Monate ab Tagesbeginn
        months = (end_date.year - start_date_day_start.year) * 12 + (end_date.month - start_date_day_start.month)
        if end_date.day < start_date_day_start.day:
            months -= 1
        return pluralize(months, translations[language]['month_singular'], translations[language]['month_plural'])

    # Mehr als ein Jahr: Jahre und Monate zählen
    else:
        years = end_date.year - start_date_day_start.year
        months = end_date.month - start_date_day_start.month

        if months < 0:
            years -= 1
            months += 12
        
        years_str = pluralize(years, translations[language]['year_singular'], translations[language]['year_plural'])
        months_str = pluralize(months, translations[language]['month_singular'], translations[language]['month_plural'])

        return f"{years_str} {translations[language]['and']} {months_str}"

# Beispiel für die Verwendung in osxphotos:
# osxphotos query --quiet --print "{function:time_since.py::time_since(2020-01-01 14:00,de)}"

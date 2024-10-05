from datetime import datetime

def pluralize(value: int, singular: str, plural: str) -> str:
    """
    Returns the appropriate singular or plural form.
    """
    return f"{value} {singular}" if value == 1 else f"{value} {plural}"

# Translations for different languages
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

def time_difference_output(start_date: datetime, end_date: datetime, language: str = 'de') -> str:
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    delta = end_date - start_date
    total_seconds = delta.total_seconds()
    
    lang = translations[language]
    
    # Less than an hour: in minutes
    if total_seconds < 3600:
        minutes = int(total_seconds // 60)
        return pluralize(minutes, lang['minute_singular'], lang['minute_plural'])
    
    # Less than a day: in hours and minutes
    elif total_seconds < 86400:
        hours = int(total_seconds // 3600)
        remaining_minutes = int((total_seconds % 3600) // 60)
        if remaining_minutes > 0:
            return f"{pluralize(hours, lang['hour_singular'], lang['hour_plural'])} {lang['and']} {pluralize(remaining_minutes, lang['minute_singular'], lang['minute_plural'])}"
        return pluralize(hours, lang['hour_singular'], lang['hour_plural'])
    
    # Less than a week: in days and hours
    elif total_seconds < 604800:
        days = int(total_seconds // 86400)
        remaining_hours = int((total_seconds % 86400) // 3600)
        if remaining_hours > 0:
            return f"{pluralize(days, lang['day_singular'], lang['day_plural'])} {lang['and']} {pluralize(remaining_hours, lang['hour_singular'], lang['hour_plural'])}"
        return pluralize(days, lang['day_singular'], lang['day_plural'])
    
    # More than a week: ignore time, count full days from midnight
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    delta = end_date - start_date
    total_seconds = delta.total_seconds()
    
    # Less than a month: in weeks and days
    if total_seconds < 2628000:
        weeks = int(total_seconds // 604800)
        remaining_days = int((total_seconds % 604800) // 86400)
        if remaining_days > 0:
            return f"{pluralize(weeks, lang['week_singular'], lang['week_plural'])} {lang['and']} {pluralize(remaining_days, lang['day_singular'], lang['day_plural'])}"
        return pluralize(weeks, lang['week_singular'], lang['week_plural'])
    
    # Less than a year: in months and weeks
    elif total_seconds < 31536000:
        months = int(total_seconds // 2628000)
        remaining_weeks = int((total_seconds % 2628000) // 604800)
        if remaining_weeks > 0:
            return f"{pluralize(months, lang['month_singular'], lang['month_plural'])} {lang['and']} {pluralize(remaining_weeks, lang['week_singular'], lang['week_plural'])}"
        return pluralize(months, lang['month_singular'], lang['month_plural'])
    
    # More than a year: in years and months
    else:
        years = int(total_seconds // 31536000)
        remaining_seconds = total_seconds % 31536000
        months = int(remaining_seconds // 2628000)
        
        years_str = pluralize(years, lang['year_singular'], lang['year_plural'])
        months_str = pluralize(months, lang['month_singular'], lang['month_plural'])
        
        if months == 0:
            return years_str
        else:
            return f"{years_str} {lang['and']} {months_str}"

# Example:
start = datetime(2020, 1, 1, 14, 30)  # 1st January 2020, 14:30
end = datetime(2023, 10, 1, 16, 45)   # 1st October 2023, 16:45

# German output
print(time_difference_output(start, end, language='de'))  # Output: "3 Jahre und 9 Monate"

# English output
print(time_difference_output(start, end, language='en'))  # Output: "3 years and 9 months"

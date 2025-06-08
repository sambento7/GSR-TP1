from datetime import datetime

def validate_date_format(date_str: str) -> bool:
    """
    Validates if the date string is in the format 'day:month:year:hour:minute:second:millisecond'.
    Returns True if valid, False otherwise.
    """
    
    try:
        date_part, miliseconds = date_str.rsplit(":", 1)

        # Validate main components of the date string
        datetime.strptime(date_part, "%d:%m:%Y:%H:%M:%S")

        # Validate milliseconds
        if len(miliseconds) != 3 or not miliseconds.isdigit():
            return False

        if not (0 <= int(miliseconds) <= 999):
            return False

        return True
    except Exception:
        return False
    
def is_valid_int(value) -> bool:
    """
    Checks if the provided value can be converted to an integer.
    Returns True if it can be converted, False otherwise.
    """
    try:
        int(value)
        return True
    except ValueError:
        return False
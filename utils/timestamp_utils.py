from datetime import datetime
import time

def generate_date_timestamp() -> str:
    '''
    Generates a timestamp in the format: day:month:year:hour:minute:second:millisecond

    :return: A formatted string representing the current date and time in the specified format.
    '''
    currentDate = datetime.now()

    # Milliseconds are not directly available in datetime, so we calculate them
    miliseconds = int(currentDate.microsecond/1000)

    # Format the date string as required
    # f-string does not support miliseconds directly, so we format it separately
    date = currentDate.strftime(f"%d:%m:%Y:%H:%M:%S:{miliseconds:03d}")

    print("\ncurrent date " + str(currentDate))
    print("\ncurrent date formatted " + date)
    return date

def generate_uptime_timestamp(start_time: float) -> str:
    """
    Generates a timestamp based on the system uptime since the given start time.
    
    :param start_time: The time when the system started, in seconds since the epoch.
    :return: A formatted string representing the uptime in the format: days:hours:minutes:seconds:milliseconds
    """
    #uses time nstead of datetime to calculate uptime since is a timestamp and not a date

    #elapsed_time is the total time in seconds since the start_time
    elapsed_time = time.time() - start_time

    day_seconds = 24 * 60 * 60
    hours_seconds = 60 * 60
    minutes_seconds = 60

    # 1. Days
    days = int(elapsed_time // day_seconds) # calculate total days from elapsed time

    # 2. Hours
    remaining_seconds = elapsed_time % day_seconds # remaining_seconds now contains the seconds left after removing full days
    hours = int(remaining_seconds // hours_seconds) # calculate total hours from remaining seconds 

    # 3. Minutes
    remaining_seconds = remaining_seconds % hours_seconds # remaining_seconds now contains the seconds left after removing full hours
    minutes = int(remaining_seconds // minutes_seconds) # calculate total minutes from remaining seconds

    # 4. Seconds
    remaining_seconds = remaining_seconds % minutes_seconds # remaining_seconds now contains the seconds left after removing full minutes
    seconds = int(remaining_seconds % minutes_seconds) # calculate total seconds from remaining seconds

    # 5. Milliseconds
    milliseconds = int((elapsed_time - int(elapsed_time)) * 1000) # calculate milliseconds from the fractional part of elapsed_time

    uptime_timestamp = f"{days}:{hours}:{minutes}:{seconds}:{milliseconds:03d}"

    print("\nstart_time: " + str(start_time))
    print("\ncurrent time: " + str(time.time()))
    print("\nUptime timestamp: " + uptime_timestamp)

    return uptime_timestamp

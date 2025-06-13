from datetime import datetime, timedelta
from typing import List, Tuple, Union
import ast

def split_time_slots(time_range: Union[str, List[str]], durations: Union[str, List[int]]) -> List[Tuple[str, str]]:
    """
    Splits a time range into sub-slots based on given durations.

    Args:
        time_range (Union[str, List[str]]): ['start_time', 'end_time'] in 'HH:MM' format
        durations (Union[str, List[int]]): Durations in minutes to split the time range

    Returns:
        List[Tuple[str, str]]: List of (start_time, end_time) in 'HH:MM' format
    """
    if isinstance(time_range, str):
        time_range = ast.literal_eval(time_range)
    if isinstance(durations, str):
        durations = ast.literal_eval(durations)

    fmt = '%H:%M'
    start = datetime.strptime(time_range[0], fmt)
    end = datetime.strptime(time_range[1], fmt)

    slots = []
    current = start

    for duration in durations:
        slot_end = current + timedelta(minutes=duration)
        if slot_end > end:
            raise ValueError("Duration exceeds time range")

        slots.append((current.strftime(fmt), slot_end.strftime(fmt)))
        current = slot_end

    return slots

# # Example usage:
# time_range = "['09:00', '10:45']"
# durations = "[60, 45]"
# slots = split_time_slots(time_range, durations)
# print(slots)  # [('09:00', '10:00'), ('10:00', '10:45')]

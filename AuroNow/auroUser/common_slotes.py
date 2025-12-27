from typing import Dict, List, Tuple

def time_to_minutes(time_str: str) -> int:
    """Convert time string to minutes from midnight"""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def minutes_to_time(minutes: int) -> str:
    """Convert minutes from midnight to time string"""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def get_service_duration(barber_id: int, slots: List[Tuple[str, str]]) -> int:
    """Get the service duration for a barber based on their slot pattern"""
    if not slots:
        return 0
    first_slot = slots[0]
    return time_to_minutes(first_slot[1]) - time_to_minutes(first_slot[0])

def get_available_time_blocks(slots: List[Tuple[str, str]]) -> List[Tuple[int, int]]:
    """
    Merge loosely adjacent or consecutive slots (allowing small gaps) into continuous time blocks.
    """
    if not slots:
        return []

    # Convert to minutes and sort
    time_blocks = [(time_to_minutes(start), time_to_minutes(end)) for start, end in slots]
    time_blocks.sort()

    merged_blocks = []
    current_start, current_end = time_blocks[0]

    for next_start, next_end in time_blocks[1:]:
        # Allow up to 15-minute gaps between slots to treat them as continuous
        if next_start <= current_end + 15:
            current_end = next_end  # Extend current block
        else:
            merged_blocks.append((current_start, current_end))
            current_start, current_end = next_start, next_end

    merged_blocks.append((current_start, current_end))
    return merged_blocks

def find_common_continuous_slots(barber_slots: Dict[int, List[Tuple[str, str]]]) -> List[Tuple[str, str]]:
    """
    Find common continuous time slots where all barbers are available,
    and return slots that can accommodate the total combined service duration.
    """
    if not barber_slots:
        return []

    total_duration = 0
    barber_durations = {}
    barber_time_blocks = {}

    for barber_id, slots in barber_slots.items():
        duration = get_service_duration(barber_id, slots)
        barber_durations[barber_id] = duration
        total_duration += duration

        time_blocks = get_available_time_blocks(slots)
        barber_time_blocks[barber_id] = time_blocks

    # Start with first barber's time blocks
    barber_ids = list(barber_slots.keys())
    common_blocks = barber_time_blocks[barber_ids[0]]

    # Intersect with each other barber's blocks
    for barber_id in barber_ids[1:]:
        new_common_blocks = []
        for cb_start, cb_end in common_blocks:
            for bb_start, bb_end in barber_time_blocks[barber_id]:
                # Compute intersection
                start = max(cb_start, bb_start)
                end = min(cb_end, bb_end)
                if start < end:
                    new_common_blocks.append((start, end))
        common_blocks = new_common_blocks

    # Now find all slots in common blocks that can fit total_duration
    available_slots = []
    for block_start, block_end in common_blocks:
        if block_end - block_start >= total_duration:
            current_start = block_start
            latest_start = block_end - total_duration
            while current_start <= latest_start:
                end_time = current_start + total_duration
                available_slots.append((minutes_to_time(current_start), minutes_to_time(end_time)))
                current_start += 20  # Adjust interval step if needed

    return available_slots

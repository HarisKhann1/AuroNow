from datetime import datetime, timedelta
from typing import Dict, List, Tuple

def find_common_continuous_slots(barber_slots: Dict[int, List[Tuple[str, str]]]) -> List[Tuple[str, str]]:
    """
    Find common continuous back-to-back slots from multiple barbers that can accommodate
    the combined duration of all services.
    
    Args:
        barber_slots: Dictionary where key is barber_id and value is list of (start_time, end_time) tuples
    
    Returns:
        List of tuples representing available slots that can fit the combined service duration
    
    Example:
        Input: {3: [('09:00', '10:30')], 4: [('10:30', '11:30')]}
        Output: [('09:00', '12:00')]  # 3-hour slot to accommodate both 1.5h + 1h services
    """
    
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
        
        # Calculate duration of first slot to determine service duration
        first_slot = slots[0]
        duration = time_to_minutes(first_slot[1]) - time_to_minutes(first_slot[0])
        return duration
    
    def get_available_time_blocks(slots: List[Tuple[str, str]]) -> List[Tuple[int, int]]:
        """Convert slots to continuous time blocks in minutes"""
        if not slots:
            return []
        
        # Convert to minutes and sort
        time_blocks = []
        for start, end in slots:
            start_mins = time_to_minutes(start)
            end_mins = time_to_minutes(end)
            time_blocks.append((start_mins, end_mins))
        
        time_blocks.sort()
        
        # Merge overlapping or consecutive blocks
        merged_blocks = [time_blocks[0]]
        
        for current_start, current_end in time_blocks[1:]:
            last_start, last_end = merged_blocks[-1]
            
            # If current block overlaps or is consecutive with the last block
            if current_start <= last_end:
                # Merge by extending the end time
                merged_blocks[-1] = (last_start, max(last_end, current_end))
            else:
                merged_blocks.append((current_start, current_end))
        
        return merged_blocks
    
    if not barber_slots or len(barber_slots) == 0:
        return []
    
    # Calculate total service duration needed
    total_duration = 0
    barber_durations = {}
    barber_time_blocks = {}
    
    for barber_id, slots in barber_slots.items():
        service_duration = get_service_duration(barber_id, slots)
        barber_durations[barber_id] = service_duration
        total_duration += service_duration
        
        # Get available time blocks for this barber
        time_blocks = get_available_time_blocks(slots)
        barber_time_blocks[barber_id] = time_blocks
    
    print(f"Service durations: {barber_durations}")
    print(f"Total duration needed: {total_duration} minutes ({total_duration//60}h {total_duration%60}m)")
    
    # Find common time periods where all barbers are available
    # Start with the first barber's available blocks
    barber_ids = list(barber_slots.keys())
    common_blocks = barber_time_blocks[barber_ids[0]].copy()
    
    # Find intersection with other barbers' availability
    for barber_id in barber_ids[1:]:
        new_common_blocks = []
        
        for common_start, common_end in common_blocks:
            for avail_start, avail_end in barber_time_blocks[barber_id]:
                # Find overlap between common block and this barber's availability
                overlap_start = max(common_start, avail_start)
                overlap_end = min(common_end, avail_end)
                
                if overlap_start < overlap_end:
                    new_common_blocks.append((overlap_start, overlap_end))
        
        common_blocks = new_common_blocks
    
    # Now find slots within common blocks that can accommodate the total duration
    available_slots = []
    
    for block_start, block_end in common_blocks:
        block_duration = block_end - block_start
        
        # Check if this block can accommodate the total service duration
        if block_duration >= total_duration:
            # Create slots within this block
            # We can start the combined service at any point where it fits
            latest_start = block_end - total_duration
            
            # For simplicity, let's create slots at regular intervals
            # You can adjust this logic based on your booking system requirements
            current_start = block_start
            
            while current_start <= latest_start:
                slot_end = current_start + total_duration
                
                # Convert back to time format
                start_time = minutes_to_time(current_start)
                end_time = minutes_to_time(slot_end)
                
                available_slots.append((start_time, end_time))
                
                # Move to next possible start time (e.g., every 30 minutes)
                # You can adjust this interval based on your booking system
                current_start += 30
    
    # Remove duplicates and sort
    available_slots = list(set(available_slots))
    available_slots.sort(key=lambda x: time_to_minutes(x[0]))
    
    return available_slots


# # Example usage and test
# if __name__ == "__main__":
#     # Test with your example data
#     test_data = {
#         3: [('09:00', '10:30'), ('09:30', '11:00'), ('10:00', '11:30'), ('10:30', '12:00'), 
#             ('11:00', '12:30'), ('11:30', '13:00'), ('12:00', '13:30'), ('12:30', '14:00'), 
#             ('13:00', '14:30'), ('13:30', '15:00'), ('14:00', '15:30'), ('14:30', '16:00'), 
#             ('15:00', '16:30'), ('15:30', '17:00')],
#         4: [('09:00', '10:00'), ('09:30', '10:30'), ('10:00', '11:00'), ('10:30', '11:30'), 
#             ('11:00', '12:00'), ('11:30', '12:30'), ('12:00', '13:00'), ('12:30', '13:30'), 
#             ('13:00', '14:00'), ('13:30', '14:30'), ('14:00', '15:00'), ('14:30', '15:30'), 
#             ('15:00', '16:00'), ('15:30', '16:30'), ('16:00', '17:00')]
#     }
    
#     result = find_common_continuous_slots(test_data)
#     print("\nAvailable slots for combined service:")
#     for slot in result:
#         start_mins = time_to_minutes(slot[0])
#         end_mins = time_to_minutes(slot[1])
#         duration = end_mins - start_mins
#         hours = duration // 60
#         minutes = duration % 60
#         print(f"{slot[0]} - {slot[1]} (Duration: {hours}h {minutes}m)")
    
#     print(f"\nTotal slots found: {len(result)}")


# def time_to_minutes(time_str: str) -> int:
#     """Helper function for testing"""
#     hours, minutes = map(int, time_str.split(':'))
#     return hours * 60 + minutes
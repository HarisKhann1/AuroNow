from datetime import datetime, timedelta, time
from django.db.models import Q
from typing import Dict, List, Tuple
from .models import BookAppointment, Staff


def get_available_slots(shop_id: int, staff_services: List[Tuple[int, int]], appointment_date: str) -> Tuple[List[Tuple[str, str]], Dict[int, List[Tuple[str, str]]]]:
    """
    Calculate available time slots for staff members based on their bookings and working hours.
    
    Args:
        shop_id (int): ID of the shop
        staff_services (List[Tuple[int, int]]): List of tuples with (staff_id, service_duration_minutes)
                                               Note: Same staff_id can appear multiple times for combined services
        appointment_date (str): Date in 'YYYY-MM-DD' format
    
    Returns:
        Tuple containing:
        - List of tuples with common available slots (start_time, end_time)
        - Dictionary mapping staff_id to their individual available slots
    """
    
    # Convert string date to date object
    try:
        date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Invalid date format. Use 'YYYY-MM-DD'")
    
    # Handle duplicate staff IDs by summing their service durations
    staff_services_dict = {}
    for staff_id, duration in staff_services:
        if staff_id in staff_services_dict:
            staff_services_dict[staff_id] += duration
        else:
            staff_services_dict[staff_id] = duration
    
    # Get unique staff IDs and validate they belong to the shop
    staff_ids = list(staff_services_dict.keys())
    staff_members = Staff.objects.filter(
        id__in=staff_ids,
        shop_id=shop_id,
        is_active=True
    )
    
    if len(staff_members) != len(staff_ids):
        raise ValueError("Some staff members not found or don't belong to this shop")
    
    # Calculate total service duration
    total_duration = sum(staff_services_dict.values())
    
    # Get existing bookings for all staff on the given date
    existing_bookings = BookAppointment.objects.filter(
        staff_id__in=staff_ids,
        appointment_date=date_obj,
        status__in=['confirmed', 'pending']
    ).exclude(
        start_time__isnull=True,
        end_time__isnull=True
    )
    
    # Store individual staff slots and common slots
    staff_individual_slots = {}
    all_staff_slots = []
    
    print(f"DEBUG: Processing {len(staff_members)} unique staff members")
    print(f"DEBUG: Staff services breakdown: {staff_services_dict}")
    
    for staff in staff_members:
        staff_total_duration = staff_services_dict[staff.id]
        
        # Get staff's working hours
        work_start = staff.work_start_time or time(9, 0)  # Default 9 AM
        work_end = staff.work_end_time or time(18, 0)     # Default 6 PM
        
        # Get bookings for this specific staff member
        staff_bookings = existing_bookings.filter(staff=staff)
        
        # Generate time slots for this staff member based on their total duration
        staff_slots = _generate_time_slots(
            work_start, work_end, staff_total_duration, staff_bookings
        )
        
        print(f"DEBUG: Staff {staff.id} working hours: {work_start} to {work_end}")
        print(f"DEBUG: Staff {staff.id} total duration: {staff_total_duration} minutes")
        print(f"DEBUG: Staff {staff.id} has {len(staff_slots)} slots")
        if staff_slots:
            print(f"DEBUG: Staff {staff.id} first slot: {staff_slots[0]}, last slot: {staff_slots[-1]}")
        
        staff_individual_slots[staff.id] = staff_slots
        all_staff_slots.append(staff_slots)
    
    # Find common available slots - times when ALL staff are free
    if len(all_staff_slots) > 1:
        common_slots = _find_common_availability(all_staff_slots, total_duration)
        print(f"DEBUG: Found {len(common_slots)} common slots for total duration {total_duration} minutes")
        
    elif len(all_staff_slots) == 1:
        # If only one staff member, filter their slots by total duration
        common_slots = _filter_slots_by_duration(all_staff_slots[0], total_duration)
    else:
        common_slots = []
    
    return common_slots, staff_individual_slots


def _generate_time_slots(work_start: time, work_end: time, duration_minutes: int, bookings) -> List[Tuple[str, str]]:
    """
    Generate available time slots for a staff member.
    
    Args:
        work_start (time): Staff's work start time
        work_end (time): Staff's work end time
        duration_minutes (int): Service duration in minutes
        bookings: QuerySet of existing bookings for this staff member
    
    Returns:
        List of available time slots as (start_time, end_time) tuples
    """
    
    # Convert work hours to datetime for easier calculation
    current_time = datetime.combine(datetime.today().date(), work_start)
    work_end_time = datetime.combine(datetime.today().date(), work_end)
    
    # Create list of busy periods from bookings
    busy_periods = []
    for booking in bookings:
        if booking.start_time and booking.end_time:
            busy_start = datetime.combine(datetime.today().date(), booking.start_time)
            busy_end = datetime.combine(datetime.today().date(), booking.end_time)
            busy_periods.append((busy_start, busy_end))
    
    # Sort busy periods by start time
    busy_periods.sort(key=lambda x: x[0])
    
    # Generate available slots
    available_slots = []
    slot_duration = timedelta(minutes=duration_minutes)
    increment = timedelta(minutes=30)  # 30-minute increments
    
    # Calculate the latest start time that allows service to finish before work_end_time
    latest_start_time = work_end_time - slot_duration
    
    print(f"DEBUG: Work start: {work_start}, Work end: {work_end}")
    print(f"DEBUG: Duration: {duration_minutes} minutes")
    print(f"DEBUG: Latest start time: {latest_start_time.time()}")
    print(f"DEBUG: Work end time: {work_end_time.time()}")
    
    while current_time <= latest_start_time:
        slot_end = current_time + slot_duration
        
        # Double check that slot end doesn't exceed work hours
        if slot_end > work_end_time:
            break
        
        # Check if this slot conflicts with any booking
        is_available = True
        for busy_start, busy_end in busy_periods:
            # Check for any overlap between slot and busy period
            if (current_time < busy_end and slot_end > busy_start):
                is_available = False
                # Jump to end of this busy period for next iteration
                current_time = busy_end
                break
        
        if is_available:
            available_slots.append((
                current_time.strftime('%H:%M'),
                slot_end.strftime('%H:%M')
            ))
            current_time += increment
        
        # Safety check to prevent infinite loop
        if current_time > latest_start_time:
            break
    
    return available_slots


def _filter_slots_by_duration(slots: List[Tuple[str, str]], total_duration_minutes: int) -> List[Tuple[str, str]]:
    """
    Filter slots to ensure they can accommodate the total service duration.
    
    Args:
        slots: List of available time slots
        total_duration_minutes: Total duration needed in minutes
    
    Returns:
        Filtered list of slots that can accommodate the total duration
    """
    
    filtered_slots = []
    
    for start_str, end_str in slots:
        start_time = datetime.strptime(start_str, '%H:%M').time()
        end_time = datetime.strptime(end_str, '%H:%M').time()
        
        # Calculate slot duration
        start_dt = datetime.combine(datetime.today().date(), start_time)
        end_dt = datetime.combine(datetime.today().date(), end_time)
        slot_duration = (end_dt - start_dt).total_seconds() / 60  # in minutes
        
        # Only include slots that can fit the total duration
        if slot_duration >= total_duration_minutes:
            filtered_slots.append((start_str, end_str))
    
    return filtered_slots


def _find_common_availability(all_staff_slots: List[List[Tuple[str, str]]], total_duration_minutes: int) -> List[Tuple[str, str]]:
    """
    Find time periods when all staff members are available simultaneously.
    This works by finding overlapping availability periods between all staff.
    """
    if not all_staff_slots or len(all_staff_slots) < 2:
        return []
    
    # Create a simpler approach: check every 30-minute slot from 9 AM to 10 PM
    # and see if ALL staff are available during that time
    
    start_time = datetime.combine(datetime.today().date(), time(9, 0))  # 9 AM
    end_time = datetime.combine(datetime.today().date(), time(22, 0))   # 10 PM
    
    common_slots = []
    current_time = start_time
    increment = timedelta(minutes=30)
    slot_duration = timedelta(minutes=total_duration_minutes)
    
    while current_time + slot_duration <= end_time:
        slot_end = current_time + slot_duration
        
        # Check if this time slot is available for ALL staff
        available_for_all = True
        
        for staff_slots in all_staff_slots:
            staff_available = False
            
            # Check if any of this staff's slots can accommodate this time period
            for staff_start_str, staff_end_str in staff_slots:
                staff_start_time = datetime.strptime(staff_start_str, '%H:%M').time()
                staff_end_time = datetime.strptime(staff_end_str, '%H:%M').time()
                
                staff_start_dt = datetime.combine(datetime.today().date(), staff_start_time)
                staff_end_dt = datetime.combine(datetime.today().date(), staff_end_time)
                
                # Check if staff's slot completely contains our desired slot
                if staff_start_dt <= current_time and staff_end_dt >= slot_end:
                    staff_available = True
                    break
            
            if not staff_available:
                available_for_all = False
                break
        
        if available_for_all:
            common_slots.append((
                current_time.strftime('%H:%M'),
                slot_end.strftime('%H:%M')
            ))
        
        current_time += increment
    
    return common_slots


# Example usage function
def example_usage():
    """
    Example of how to use the get_available_slots function
    """
    
    # Example parameters - now using list of tuples
    shop_id = 1
    
    # Example 1: Different staff members
    staff_services_1 = [
        (101, 60),  # Staff ID 101 provides 60-minute service
        (102, 45),  # Staff ID 102 provides 45-minute service
    ]
    
    # Example 2: Same staff member with multiple services (combined duration)
    staff_services_2 = [
        (4, 45),   # Staff ID 4 provides first service (45 minutes)
        (4, 60),   # Staff ID 4 provides second service (60 minutes)
                   # Total for staff 4: 105 minutes
    ]
    
    # Example 3: Mixed scenario
    staff_services_3 = [
        (4, 45),   # Staff ID 4 - first service
        (4, 60),   # Staff ID 4 - second service (total: 105 minutes)
        (5, 30),   # Staff ID 5 - single service (30 minutes)
    ]
    
    appointment_date = "2024-12-15"
    
    print("=== Example 1: Different Staff Members ===")
    try:
        common_slots, individual_slots = get_available_slots(
            shop_id, staff_services_1, appointment_date
        )
        
        print("Common Available Slots:")
        for slot in common_slots:
            print(f"  {slot[0]} to {slot[1]}")
        
        print("\nIndividual Staff Slots:")
        for staff_id, slots in individual_slots.items():
            print(f"  Staff {staff_id}:")
            for slot in slots:
                print(f"    {slot[0]} to {slot[1]}")
                
    except ValueError as e:
        print(f"Error: {e}")
    
    print("\n=== Example 2: Same Staff with Multiple Services ===")
    try:
        common_slots, individual_slots = get_available_slots(
            shop_id, staff_services_2, appointment_date
        )
        
        print("Available Slots for Staff 4 (Combined 105 minutes):")
        for slot in common_slots:
            print(f"  {slot[0]} to {slot[1]}")
        
        print("\nIndividual Staff Slots:")
        for staff_id, slots in individual_slots.items():
            print(f"  Staff {staff_id} (Total duration: 105 minutes):")
            for slot in slots:
                print(f"    {slot[0]} to {slot[1]}")
                
    except ValueError as e:
        print(f"Error: {e}")
    
    print("\n=== Example 3: Mixed Scenario ===")
    try:
        common_slots, individual_slots = get_available_slots(
            shop_id, staff_services_3, appointment_date
        )
        
        print("Common Available Slots (Staff 4: 105 min + Staff 5: 30 min = 135 min total):")
        for slot in common_slots:
            print(f"  {slot[0]} to {slot[1]}")
        
        print("\nIndividual Staff Slots:")
        for staff_id, slots in individual_slots.items():
            duration = 105 if staff_id == 4 else 30
            print(f"  Staff {staff_id} (Duration: {duration} minutes):")
            for slot in slots:
                print(f"    {slot[0]} to {slot[1]}")
                
    except ValueError as e:
        print(f"Error: {e}")


# Additional utility function to check if a specific time slot is available
def is_slot_available(shop_id: int, staff_id: int, appointment_date: str, 
                     start_time: str, duration_minutes: int) -> bool:
    """
    Check if a specific time slot is available for a staff member.
    
    Args:
        shop_id (int): ID of the shop
        staff_id (int): ID of the staff member
        appointment_date (str): Date in 'YYYY-MM-DD' format
        start_time (str): Start time in 'HH:MM' format
        duration_minutes (int): Duration in minutes
    
    Returns:
        bool: True if slot is available, False otherwise
    """
    
    try:
        date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(start_time, '%H:%M').time()
        end_time_obj = (datetime.combine(date_obj, start_time_obj) + 
                       timedelta(minutes=duration_minutes)).time()
        
        # Check if staff exists and is active
        staff = Staff.objects.get(id=staff_id, shop_id=shop_id, is_active=True)
        
        # Check if within working hours
        work_start = staff.work_start_time or time(9, 0)
        work_end = staff.work_end_time or time(18, 0)
        
        if start_time_obj < work_start or end_time_obj > work_end:
            return False
        
        # Check for conflicts with existing bookings
        conflicting_bookings = BookAppointment.objects.filter(
            staff_id=staff_id,
            appointment_date=date_obj,
            status__in=['confirmed', 'pending']
        ).exclude(
            start_time__isnull=True,
            end_time__isnull=True
        ).filter(
            Q(start_time__lt=end_time_obj, end_time__gt=start_time_obj)
        )
        
        return not conflicting_bookings.exists()
        
    except (ValueError, Staff.DoesNotExist):
        return False
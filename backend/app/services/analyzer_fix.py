import re

def extract_name_from_transcript(transcript):
    """Extract service user name from transcript"""
    
    # Common patterns for names in transcripts
    patterns = [
        r"(?:I am|I'm|this is|my name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?):\s*[\"']?(?:Hi|Hello|Help)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, transcript)
        if match:
            name = match.group(1)
            # Filter out common non-names
            if name.lower() not in ['support', 'worker', 'carer', 'caller', 'user', 'client', 'julie', 'peaterson']:
                return name
    
    # If no name found, return empty string
    return ""

def extract_location_from_transcript(transcript):
    """Extract location from transcript"""
    
    # Common location patterns
    locations = ['bedroom', 'bathroom', 'kitchen', 'living room', 'garden', 'hallway', 'stairs', 'lounge', 'dining room']
    
    transcript_lower = transcript.lower()
    for location in locations:
        if location in transcript_lower:
            # Check if it's in context of being in that location
            if f"in the {location}" in transcript_lower or f"in my {location}" in transcript_lower:
                return location.title()
            elif f"at the {location}" in transcript_lower:
                return location.title()
            elif f"down the {location}" in transcript_lower:
                return location.title()
    
    return ""

def extract_time_duration(transcript):
    """Extract time duration from transcript"""
    
    # Look for time patterns
    time_match = re.search(r'(\d+)\s*(?:minutes?|mins?|hours?|hrs?)', transcript, re.IGNORECASE)
    if time_match:
        return time_match.group(0)
    
    return ""

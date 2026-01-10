import re

def sanitize_filename(message_id):
    """
    Converts a Message-ID (e.g., <abc.123@gmail.com>) into a filesystem-safe string.
    Removes angle brackets, replaces non-alphanumeric chars with underscores.
    """
    if not message_id:
        return "unknown_message_id"
        
    # Remove angle brackets
    s = message_id.strip('<>')
    
    # Replace unsafe characters with underscore
    # Allow alphanumeric, dash, underscore, dot
    s = re.sub(r'[^a-zA-Z0-9\-\_\.]', '_', s)
    
    return s

"""
Number Generator Utility

Generates unique identifiers for incidents and evidence.
"""
import os
from datetime import datetime


def get_sequence():
    """
    Get next sequence number from configuration or file.
    
    Reads from a configuration file or environment variable.
    
    Returns:
        int: Next sequence number to use
    """
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "number_config.json")
    
    try:
        with open(config_path, "r") as f:
            data = f.read()
            import json
            config = json.loads(data)
            return config.get("next_sequence", 0)
    except FileNotFoundError:
        # Default sequence if config doesn't exist
        return 0
    except Exception:
        return 0


def increment_sequence(increment_by: int = 1):
    """
    Increment the sequence number.
    
    Args:
        increment_by: Amount to increment (default: 1)
    
    Returns:
        int: New sequence number
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "number_config.json")
        
        with open(config_path, "r") as f:
            import json
            data = f.read()
            config = json.loads(data)
        
        new_sequence = config["next_sequence"] + increment_by
        
        with open(config_path, "w") as f:
            json.dump({"next_sequence": new_sequence}, f)
        
        return new_sequence
    except Exception as e:
        # Increment in memory if file access fails
        print(f"Warning: Could not update sequence file: {e}")
        return 0


def generate_incident_number(year: int, sequence: int) -> str:
    """
    Generate an incident number.
    
    Example: INC-2026-000184
    
    Args:
        year: Year (e.g., 2026)
        sequence: Sequence number (e.g., 184)
    
    Returns:
        str: Generated incident number
    """
    return f"INC-{year}-{sequence:06d}"


def generate_evidence_number(sequence: int) -> str:
    """
    Generate an evidence ID.
    
    Example: EVID-00192
    
    Args:
        sequence: Sequence number
    
    Returns:
        str: Generated evidence ID
    """
    return f"EVID-{sequence:06d}"


def generate_hash_number(sequence: int) -> str:
    """
    Generate a hash ID.
    
    Example: HASH-000192
    
    Args:
        sequence: Sequence number
    
    Returns:
        str: Generated hash ID
    """
    return f"HASH-{sequence:06d}"


def generate_host_number(sequence: int) -> str:
    """
    Generate a host ID.
    
    Example: HOST-00123
    
    Args:
        sequence: Sequence number
    
    Returns:
        str: Generated host ID
    """
    return f"HOST-{sequence:06d}"


def generate_user_number(sequence: int) -> str:
    """
    Generate a user ID.
    
    Example: USER-00045
    
    Args:
        sequence: Sequence number
    
    Returns:
        str: Generated user ID
    """
    return f"USER-{sequence:06d}"


def generate_process_number(sequence: int) -> str:
    """
    Generate a process ID.
    
    Example: PROC-000567
    
    Args:
        sequence: Sequence number
    
    Returns:
        str: Generated process ID
    """
    return f"PROC-{sequence:06d}"

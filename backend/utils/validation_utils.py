"""
Validation utilities for SOAR Platform.
"""
from typing import Any, Dict, List, Optional
import re


def validate_input(data: Dict, schema: Dict) -> Dict:
    """
    Validate input data against a schema.
    
    Args:
        data: Input data to validate
        schema: Validation schema defining required fields and types
    
    Returns:
        Validation result with errors or success flag
    
    Example schema:
    {
        "required": ["field1"],
        "fields": {
            "field1": {"type": "string", "minLength": 1},
            "field2": {"type": "integer", "minimum": 0}
        }
    }
    """
    errors = []
    
    # Check required fields
    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif data[field] is None:
            errors.append(f"Field {field} cannot be null")
    
    # Validate each field
    for field, constraints in schema.get("fields", {}).items():
        if field in data:
            value = data[field]
            
            # Check type
            field_type = constraints.get("type")
            if field_type:
                if field_type == "string":
                    if not isinstance(value, str):
                        errors.append(f"Field {field} must be a string")
                    elif constraints.get("minLength", 0) > 0:
                        if len(value) < constraints["minLength"]:
                            errors.append(f"Field {field} must be at least {constraints['minLength']} characters")
                elif field_type == "integer":
                    if not isinstance(value, int):
                        errors.append(f"Field {field} must be an integer")
                    elif constraints.get("minimum", float('-inf')) > value:
                        errors.append(f"Field {field} must be at least {constraints['minimum']}")
                elif field_type == "array":
                    if not isinstance(value, list):
                        errors.append(f"Field {field} must be an array")
            
            # Check string pattern
            if isinstance(value, str) and constraints.get("pattern"):
                if not re.match(constraints["pattern"], value):
                    errors.append(f"Field {field} does not match pattern: {constraints['pattern']}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_action(
    action_name: str,
    action_type: str,
    risk_level: str,
    requires_approval: bool
) -> Dict:
    """
    Validate action before execution.
    
    Args:
        action_name: Name of the action
        action_type: Type of action (e.g., "contain_host")
        risk_level: Risk level (READ, ENRICH, MODIFY, CONTAIN, EXECUTE, DESTRUCTIVE)
        requires_approval: Whether approval is required
    
    Returns:
        Validation result
    """
    valid_risk_levels = ["READ", "ENRICH", "MODIFY_LOW", "MODIFY", "CONTAIN", "EXECUTE", "DESTRUCTIVE"]
    valid_action_types = ["get_host", "search_siem", "contain_host", "delete_object", "execute_script"]
    
    errors = []
    
    # Check risk level
    if risk_level not in valid_risk_levels:
        errors.append(f"Invalid risk level: {risk_level}. Must be one of: {', '.join(valid_risk_levels)}")
    
    # Check action type
    if action_type not in valid_action_types:
        errors.append(f"Invalid action type: {action_type}. Must be one of: {', '.join(valid_action_types)}")
    
    # High-risk actions should require approval
    high_risk_actions = ["CONTAIN", "EXECUTE", "DESTRUCTIVE"]
    if risk_level in high_risk_actions and not requires_approval:
        errors.append(f"High-risk action ({risk_level}) requires approval")
    
    # Validate action name format
    name_pattern = r"^[a-zA-Z0-9_]+$"
    if not re.match(name_pattern, action_name):
        errors.append(f"Invalid action name format: {action_name}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_evidence(
    content: str,
    evidence_type: Optional[str],
    format: str = "json",
    classification: str = "untrusted"
) -> Dict:
    """
    Validate evidence before ingestion.
    
    Args:
        content: Evidence content
        evidence_type: Type of evidence (process, file, network, etc.)
        format: Content format (json, text, etc.)
        classification: Trust level (untrusted, internal, public)
    
    Returns:
        Validation result
    """
    errors = []
    
    # Check content length
    if len(content) > 100000:  # 100KB limit
        errors.append("Evidence content exceeds maximum size (100KB)")
    
    # Validate classification
    valid_classifications = ["untrusted", "internal", "public"]
    if classification not in valid_classifications:
        errors.append(f"Invalid classification: {classification}. Must be one of: {', '.join(valid_classifications)}")
    
    # Validate evidence type
    valid_evidence_types = [
        "process", "file", "network", "registry", "command_line",
        "email", "webpage", "log", "artifact"
    ]
    if evidence_type and evidence_type not in valid_evidence_types:
        errors.append(f"Invalid evidence type: {evidence_type}")
    
    # Content must not contain secrets
    secret_patterns = [
        r"[^a-zA-Z0-9_-]{32,}[a-zA-Z0-9_-]{32,}",  # Potential API key
        r"[a-zA-Z0-9]{32,}",  # Potential password
    ]
    for pattern in secret_patterns:
        if re.search(pattern, content):
            errors.append("Evidence may contain secrets")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_observable(
    content: str,
    observable_type: str
) -> Dict:
    """
    Validate observable before indexing.
    
    Args:
        content: Observable content (IP, domain, hash, etc.)
        observable_type: Type of observable
    
    Returns:
        Validation result
    """
    errors = []
    
    # Validate based on type
    if observable_type == "ip":
        # Check IP format
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", content):
            errors.append(f"Invalid IP address format: {content}")
    
    elif observable_type == "domain":
        # Check domain format
        if not re.match(r"^[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}$", content):
            errors.append(f"Invalid domain format: {content}")
    
    elif observable_type == "hash":
        # Validate hash format (SHA256)
        if len(content) != 64:
            errors.append(f"Hash must be 64 characters (SHA256): {content}")
    
    # Check for base64 encoded content that might be malware
    import base64
    try:
        decoded = base64.b64decode(content)
        if decoded and len(decoded) > 100:
            # Large decoded content might be malware
            errors.append("Observable may contain large encoded content")
    except:
        pass
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_incident_data(
    title: str,
    description: str,
    severity: str,
    source_type: Optional[str]
) -> Dict:
    """
    Validate incident creation data.
    
    Args:
        title: Incident title
        description: Incident description
        severity: Incident severity
        source_type: Source type (SIEM, EDR, etc.)
    
    Returns:
        Validation result
    """
    errors = []
    
    # Validate title
    if len(title) < 1:
        errors.append("Title cannot be empty")
    if len(title) > 500:
        errors.append("Title exceeds maximum length (500 characters)")
    
    # Validate severity
    valid_severities = ["low", "medium", "high", "critical"]
    if severity and severity not in valid_severities:
        errors.append(f"Invalid severity: {severity}. Must be one of: {', '.join(valid_severities)}")
    
    # Validate source type
    if source_type:
        if len(source_type) > 50:
            errors.append("Source type exceeds maximum length (50 characters)")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def sanitize_output(data: Any, max_depth: int = 3, max_items: int = 100) -> Any:
    """
    Sanitize output for API responses (prevent credential leakage).
    
    Args:
        data: Data to sanitize
        max_depth: Maximum nesting depth
        max_items: Maximum items in lists/dicts
    
    Returns:
        Sanitized data
    """
    from sqlalchemy.orm import Session
    
    def remove_sensitive(obj):
        """Remove sensitive data from object."""
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if key.lower() in ["password", "secret", "api_key", "apikey", "token"]:
                    result[key] = "[REDACTED]"
                elif key.lower() == "user_password":
                    result[key] = "[REDACTED]"
                else:
                    result[key] = remove_sensitive(value)
            return result
        elif isinstance(obj, list):
            return [remove_sensitive(item) for item in obj[:max_items]]
        else:
            return obj
    
    return remove_sensitive(data)

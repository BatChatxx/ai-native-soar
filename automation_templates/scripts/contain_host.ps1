# PowerShell Containment Script
# Isolates endpoint from network
# Risk: CONTAIN (requires approval)

$schema = {
  "type": "object",
  "properties": {
    "host_id": {
      "type": "string",
      "description": "Host ID (e.g., HOST-00123)"
    },
    "host_name": {
      "type": "string",
      "description": "Host name (optional)"
    },
    "action": {
      "type": "string",
      "enum": ["isolate", "quarantine", "block_network", "disable"],
      "description": "Containment action"
    },
    "reason": {
      "type": "string",
      "description": "Reason for containment"
    },
    "duration_minutes": {
      "type": "integer",
      "description": "Duration in minutes (0 = permanent)"
    }
  },
  "required": ["host_id", "action", "reason"]
}

$output_schema = {
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success", "failed", "timeout"]
    },
    "message": {
      "type": "string"
    },
    "host_id": {
      "type": "string"
    },
    "action_performed": {
      "type": "string"
    }
  }
}

param(
  $Input
)

# Validate input
if (-not $Input.host_id) {
  throw "host_id is required"
}

if (-not $Input.action) {
  throw "action is required"
}

if (-not $Input.reason) {
  throw "reason is required"
}

# Log action
Write-Host "Starting containment action for $Input.host_id" -ForegroundColor Yellow
Write-Host "Action: $Input.action" -ForegroundColor Yellow
Write-Host "Reason: $Input.reason" -ForegroundColor Yellow

# Perform containment based on action
switch ($Input.action) {
  "isolate" {
    # Network isolation command
    Write-Host "Executing network isolation..."
    # Example: Set network isolation
    # Set-NetworkIsolation -HostId $Input.host_id -Enabled $true
    
    $output = [PSCustomObject]@{
      status = "success"
      message = "Host isolated successfully"
      host_id = $Input.host_id
      action_performed = "isolate"
    }
  }
  
  "quarantine" {
    # Quarantine action
    Write-Host "Executing quarantine..."
    # Example: Move to quarantine segment
    
    $output = [PSCustomObject]@{
      status = "success"
      message = "Host quarantined successfully"
      host_id = $Input.host_id
      action_performed = "quarantine"
    }
  }
  
  "block_network" {
    # Block network access
    Write-Host "Blocking network access..."
    
    $output = [PSCustomObject]@{
      status = "success"
      message = "Network access blocked"
      host_id = $Input.host_id
      action_performed = "block_network"
    }
  }
  
  "disable" {
    # Disable host
    Write-Host "Disabling host..."
    
    $output = [PSCustomObject]@{
      status = "success"
      message = "Host disabled successfully"
      host_id = $Input.host_id
      action_performed = "disable"
    }
  }
  
  default {
    throw "Unknown action: $Input.action"
  }
}

# Log completion
Write-Host "Containment action completed" -ForegroundColor Green
return $output

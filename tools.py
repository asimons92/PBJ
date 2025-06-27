# --- Tool definition for behavior record parsing --- #

BEHAVIOR_RECORD_TOOL = {
    "type": "function",
    "function": {
        "name": "parse_behavior_record",
        "description": "Extracts a structured student behavior record from unstructured teacher notes.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_name": {"type": "string"},
                "student_id": {"type": "string"},
                "recording_timestamp": {"type": "string"},
                "behavior_date": {"type": "string"},
                "source": {"type": "string", "enum": ["teacher_note"]},
                "behavior": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["off-task", "disruption", "non-participation", "tardy", "absence",
                                     "peer-disruption", "technology-violation", "prosocial", "defiance",
                                     "aggression", "self-management", "respect", "other"]
                        },
                        "description": {"type": "string"},
                        "severity": {"type": "string", "enum": ["low", "moderate", "high"]},
                        "is_positive": {"type": "boolean"},
                        "needs_followup": {"type": "boolean"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["category", "description", "severity", "is_positive", "needs_followup", "tags"]
                },
                "context": {
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string"},
                        "teacher": {"type": "string"},
                        "activity": {"type": "string"},
                        "group_ids": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "location": {"type": "string"},
                        #"period": {"type": "integer"}
                    }
                },
                "intervention": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["none", "recommended", "in_progress", "completed"]
                        },
                        "type": {"type": "string"},
                        "notes": {"type": "string"},
                        "tier": {
                            "type": "string",
                            "enum": ["universal", "tier_1", "tier_2", "tier_3"]
                        }
                    }
                }
            },
            "required": ["student_name", "recording_timestamp", "source", "behavior"] 
        }
    }
}

# List of tools for OpenAI API
tools = [BEHAVIOR_RECORD_TOOL] 
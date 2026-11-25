DISEASE_INFO_TOOL = {
    "type": "function",
    "function": {
        "name": "get_disease_info",
        "description": "Get detailed information about a specific crop disease including symptoms, causes, and treatment",
        "parameters": {
            "type": "object",
            "properties": {
                "disease_name": {
                    "type": "string",
                    "description": "The name of the disease (e.g., 'Rice___Leaf_Blast', 'Corn___Common_Rust')",
                }
            },
            "required": ["disease_name"],
        },
    },
}

SCAN_HISTORY_TOOL = {
    "type": "function",
    "function": {
        "name": "get_scan_history",
        "description": "Get the user's recent crop scan history to understand their disease patterns",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of recent scans to retrieve (default 5)",
                }
            },
            "required": [],
        },
    },
}

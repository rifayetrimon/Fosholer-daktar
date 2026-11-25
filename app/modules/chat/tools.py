import base64
from dataclasses import dataclass
from typing import Any
from app.modules.knowledge.service import KnowledgeService


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict

TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="classify_crop_disease",
        description="Classify a crop leaf disease from a base64-encoded image.",
        parameters={
            "type": "object",
            "properties": {
                "image_base64": {
                    "type": "string",
                    "description": "Base64-encoded image of the crop leaf",
                }
            },
            "required": ["image_base64"],
        },
    ),
    ToolSpec(
        name="get_disease_knowledge",
        description="Get knowledge base entries for a crop disease using semantic search.",
        parameters={
            "type": "object",
            "properties": {
                "disease_name": {
                    "type": "string",
                    "description": "Disease label e.g. Rice___Leaf_Blast",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 3,
                },
            },
            "required": ["disease_name"],
        },
    ),
]

async def execute_tool(
    knowledge: KnowledgeService,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    if tool_name == "classify_crop_disease":
        from app.ml.classifier import classify_disease

        image_bytes = base64.b64decode(arguments["image_base64"])
        result = await classify_disease(image_bytes)
        label = result["label"]
        parts = label.split("___")
        return {
            "label": label,
            "confidence": round(result["confidence"], 4),
            "crop": parts[0] if len(parts) > 1 else "Unknown",
            "disease": parts[1] if len(parts) > 1 else label,
        }

    if tool_name == "get_disease_knowledge":
        disease_name = arguments["disease_name"]
        limit = arguments.get("limit", 3)
        chunks = await knowledge.search_relevant(disease_name, limit=limit)
        return {
            "results": [
                {"disease": c.disease_name, "crop": c.crop_name, "content": c.content}
                for c in chunks
            ]
        }

    return {"error": f"Unknown tool: {tool_name}"}

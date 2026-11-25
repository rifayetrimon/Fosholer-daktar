import json
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import (
    StreamableHTTPASGIApp,
    StreamableHTTPSessionManager,
)
from mcp.shared.exceptions import MCPError
from app.db.session import session_manager
from app.integrations.embeddings.dependencies import get_embedding_client
from app.modules.chat.tools import TOOLS, execute_tool
from app.modules.knowledge.service import KnowledgeService

DISEASE_CATEGORIES = [
    "Corn___Common_Rust",
    "Corn___Gray_Leaf_Spot",
    "Corn___Healthy",
    "Potato___Early_Blight",
    "Potato___Late_Blight",
    "Potato___Healthy",
    "Rice___Brown_Spot",
    "Rice___Leaf_Blast",
    "Rice___Healthy",
    "Wheat___Brown_Rust",
    "Wheat___Yellow_Rust",
    "Wheat___Healthy",
    "Invalid",
]

CATEGORIES_URI = "disease-knowledge://categories"

DIAGNOSIS_PROMPT = types.Prompt(
    name="crop_diagnosis_prompt",
    description="Generate a structured crop disease diagnosis prompt for Bangladeshi farmers.",
    arguments=[
        types.PromptArgument(name="crop", description="Crop type e.g. Rice, Wheat", required=True),
        types.PromptArgument(name="symptoms", description="Observed symptoms on the plant", required=True),
    ],
)

async def list_tools(ctx, params) -> types.ListToolsResult:
    tools = [
        types.Tool(
            name=spec.name,
            description=spec.description,
            input_schema=spec.parameters,
        )
        for spec in TOOLS
    ]
    return types.ListToolsResult(tools=tools)

async def call_tool(ctx, params: types.CallToolRequestParams) -> types.CallToolResult:
    async with session_manager.session() as db:
        knowledge = KnowledgeService(db, get_embedding_client())
        result = await execute_tool(knowledge, params.name, params.arguments or {})
    return types.CallToolResult(
        content=[types.TextContent(text=json.dumps(result, ensure_ascii=False))],
        is_error="error" in result,
    )

async def list_resources(ctx, params) -> types.ListResourcesResult:
    return types.ListResourcesResult(
        resources=[
            types.Resource(
                uri=CATEGORIES_URI,
                name="Disease Categories",
                description="All supported crop disease categories this model can detect",
                mime_type="text/plain",
            )
        ]
    )

async def list_resource_templates(ctx, params) -> types.ListResourceTemplatesResult:
    return types.ListResourceTemplatesResult(resource_templates=[])

async def read_resource(
    ctx, params: types.ReadResourceRequestParams
) -> types.ReadResourceResult:
    if str(params.uri) != CATEGORIES_URI:
        raise MCPError(-32002, f"Unknown resource: {params.uri}")
    text = "Supported crop disease categories:\n" + "\n".join(
        f"- {c}" for c in DISEASE_CATEGORIES
    )
    return types.ReadResourceResult(
        contents=[
            types.TextResourceContents(
                uri=params.uri, mime_type="text/plain", text=text
            )
        ]
    )

async def list_prompts(ctx, params) -> types.ListPromptsResult:
    return types.ListPromptsResult(prompts=[DIAGNOSIS_PROMPT])

async def get_prompt(
    ctx, params: types.GetPromptRequestParams
) -> types.GetPromptResult:
    if params.name != DIAGNOSIS_PROMPT.name:
        raise MCPError(-32602, f"Unknown prompt: {params.name}")
    args = params.arguments or {}
    if "crop" not in args or "symptoms" not in args:
        raise MCPError(-32602, "Both crop and symptoms are required")
    text = f"""You are Fosholer Daktar, an expert crop disease specialist for Bangladeshi farmers.

A farmer has reported the following:
- Crop: {args['crop']}
- Observed symptoms: {args['symptoms']}

Please provide:
1. Most likely disease(s) based on the symptoms
2. Severity assessment
3. Immediate treatment steps (using locally available products in Bangladesh)
4. Preventive measures for the future
5. When to seek expert help from the Department of Agricultural Extension (DAE)

Answer in simple language that a farmer can understand."""
    return types.GetPromptResult(
        messages=[
            types.PromptMessage(role="user", content=types.TextContent(text=text))
        ]
    )

server = Server(
    "fosholer-daktar",
    on_list_tools=list_tools,
    on_call_tool=call_tool,
    on_list_resources=list_resources,
    on_list_resource_templates=list_resource_templates,
    on_read_resource=read_resource,
    on_list_prompts=list_prompts,
    on_get_prompt=get_prompt,
)

session_manager_mcp = StreamableHTTPSessionManager(app=server)
mcp_asgi_app = StreamableHTTPASGIApp(session_manager_mcp)

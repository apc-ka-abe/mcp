from fastapi import FastAPI, Request, HTTPException
from mcp.server import Server
from databricks.labs.mcp._version import __version__ as VERSION
from databricks.labs.mcp.servers.unity_catalog.cli import get_settings
from databricks.labs.mcp.servers.unity_catalog.server import get_tools_dict
from databricks.labs.mcp.servers.unity_catalog.tools.base_tool import BaseTool
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool as ToolSpec
from contextlib import asynccontextmanager
import os

# Initialize MCP core
mcp_server = Server(name="mcp-unitycatalog", version=VERSION)
settings = get_settings()
tools_dict: dict[str, BaseTool] = get_tools_dict(settings=settings)

# Initialize FastMCP
mcp = FastMCP(name="mcp-unitycatalog")
for tool_name, tool in tools_dict.items():
    mcp.add_tool(
        tool.execute,
        name=tool_name,
        description=tool.tool_spec.description,
        annotations=tool.tool_spec.annotations,
    )

# Lifespan context manager for session lifecycle
@asynccontextmanager
async def lifespan(app):
    try:
        print("Lifespan: starting MCP session manager...")
        async with mcp.session_manager.run():
            print("Lifespan: started successfully")
            yield
    except Exception as e:
        print("Lifespan Error:", e)
        raise

# Authentication function supporting internal + external access
async def authenticate(request: Request):
    # Case 1: Databricks internal user via forwarded header
    email = request.headers.get("x-forwarded-email")
    if email:
        print(f"Authenticated internal user: {email}")
        return email

    # Case 2: External user via Authorization: Bearer
    auth = request.headers.get("authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.removeprefix("Bearer ").strip()
        expected_token = os.getenv("EXTERNAL_ACCESS_TOKEN")
        if token == expected_token:
            print("Authenticated external user via token.")
            return "external-user@databricksapps"
        raise HTTPException(status_code=403, detail="Invalid token")

    # No valid auth provided
    raise HTTPException(status_code=401, detail="Unauthorized")

# Create FastAPI app and mount FastMCP with auth
app = FastAPI(
    title="Databricks MCP Server",
    description="FastAPI MCP with Unity Catalog",
    version=VERSION,
    lifespan=lifespan,
)

# Mount MCP API with authentication
streamable_app = mcp.streamable_http_app(auth=authenticate)
app.mount("/api/mcp", streamable_app)

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}
    

# from fastapi import FastAPI
# from mcp.server import Server
# from databricks.labs.mcp._version import __version__ as VERSION
# from databricks.labs.mcp.servers.unity_catalog.cli import get_settings
# from databricks.labs.mcp.servers.unity_catalog.server import get_tools_dict
# from databricks.labs.mcp.servers.unity_catalog.tools.base_tool import BaseTool
# from mcp.types import Tool as ToolSpec
# from mcp.server.fastmcp import FastMCP
# from contextlib import asynccontextmanager
# import os
# import uvicorn

# # MCP init
# mcp_server = Server(name="mcp-unitycatalog", version=VERSION)
# settings = get_settings()
# tools_dict: dict[str, BaseTool] = get_tools_dict(settings=settings)

# # FastMCP
# mcp = FastMCP(name="mcp-unitycatalog")
# for tool_name, tool in tools_dict.items():
#     mcp.add_tool(
#         tool.execute,
#         name=tool_name,
#         description=tool.tool_spec.description,
#         annotations=tool.tool_spec.annotations,
#     )

# # @asynccontextmanager
# # async def lifespan(app):
# #     async with mcp.session_manager.run():
# #         yield
# @asynccontextmanager
# async def lifespan(app):
#     try:
#         print("Lifespan: starting MCP session manager...")
#         async with mcp.session_manager.run():
#             print("Lifespan: started successfully")
#             yield
#     except Exception as e:
#         print("Lifespan Error:", e)
#         raise

# # FastAPI instance
# app = FastAPI(
#     title="Databricks MCP Server",
#     description="FastAPI MCP with Unity Catalog",
#     version=VERSION,
#     lifespan=lifespan,
# )

# # Mount MCP
# streamable_app = mcp.streamable_http_app()
# app.mount("/api/mcp", streamable_app)

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# if __name__ == "__main__":
#     # port = int(os.getenv("DATABRICKS_APP_PORT", "5000"))
#     # port = 8080
#     uvicorn.run(app, host="0.0.0.0", port=5000)




# from fastapi import FastAPI
# from mcp.server import Server
# from databricks.labs.mcp.servers.unity_catalog.cli import get_settings

# from databricks.labs.mcp._version import __version__ as VERSION
# from databricks.labs.mcp.servers.unity_catalog.server import get_tools_dict
# from databricks.labs.mcp.servers.unity_catalog.tools.base_tool import BaseTool
# from mcp.server.fastmcp import FastMCP

# mcp_server = Server(name="mcp-unitycatalog", version=VERSION)
# tools_dict: dict[str, BaseTool] = get_tools_dict(settings=get_settings())


# mcp = FastMCP(
#     name="mcp-unitycatalog",
# )

# for tool_name, tool in tools_dict.items():
#     mcp.add_tool(
#         tool.execute,
#         name=tool_name,
#         description=tool.tool_spec.description,
#         annotations=tool.tool_spec.annotations,
#     )

# app = FastAPI(
#     lifespan=lambda _: mcp.session_manager.run(),
# )

# streamable_app = mcp.streamable_http_app()

# app.mount("/api", streamable_app)

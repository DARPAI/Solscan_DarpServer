from typing import Any
import asyncio
import httpx
import os
from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
import uvicorn
import logging
from datetime import datetime


load_dotenv()

logging.basicConfig(
    filename='solscan_api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

API_BASE = "pro-api.solscan.io"
API_TOKEN = os.getenv("SOLSCAN_API_TOKEN")

if not API_TOKEN:
    raise ValueError("SOLSCAN_API_TOKEN environment variable is not set")

server = Server("solscan-api")
sse = SseServerTransport("/messages/")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available Solscan API tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="get-sol-token-price",
            description="Get sonala price information from Solscan",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Token address on Solana blockchain",
                    },
                },
                "required": ["address"],
            },
        ),
        # types.Tool(
        #     name="list-sol-tokens",
        #     description="Get a paginated list of tokens from Solscan",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "page": {
        #                 "type": "integer",
        #                 "description": "Page number (1-based)",
        #                 "default": 1,
        #                 "minimum": 1,
        #             },
        #             "page_size": {
        #                 "type": "integer",
        #                 "description": "Number of items per page",
        #                 "default": 10,
        #                 "minimum": 1,
        #                 "maximum": 100,
        #             },
        #         },
        #         "required": [],
        #     },
        # ),
        # types.Tool( 
        #     name="get-token-market",
        #     description="Get token market data from Solscan",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "address": {
        #                 "type": "string",
        #                 "description": "Token address on Solana blockchain",
        #             },
        #         },
        #         "required": ["address"],
        #     },
        # ),
        # types.Tool(
        #     name="get-trending-tokens",
        #     description="Get trending tokens from Solscan",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "limit": {
        #                 "type": "integer",
        #                 "description": "Number of trending tokens to return",
        #                 "default": 10,
        #                 "minimum": 1,
        #                 "maximum": 100,
        #             },
        #         },
        #         "required": [],
        #     },
        # ),
        #
        # types.Tool(  
        #     name="get-top-tokens",
        #     description="Get top tokens by market cap from Solscan",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "limit": {
        #                 "type": "integer",
        #                 "description": "Number of top tokens to return",
        #                 "default": 10,
        #                 "minimum": 1,
        #                 "maximum": 100,
        #             },
        #         },
        #         "required": [],
        #     },
        # ),
        types.Tool(
            name="get-latest-blocks",
            description="Get sonala latest blocks information from Solscan",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of latest blocks to return",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100,
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get-account-info",
            description="Get sonala accounts information for a Solana address",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Solana account address",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (1)",
                        "default": 1,
                        "minimum": 1,
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of items per page",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100,
                    },
                },
                "required": ["address"],
            },
        ),

        # not accurate
        types.Tool(
            name="get-account-activities",
            description="Get DeFi activities for a Solana address",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Solana account address",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (1-based)",
                        "default": 1,
                        "minimum": 1,
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of items per page",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Field to sort by",
                        "default": "block_time",
                        "enum": ["block_time"],
                    },
                    "sort_order": {
                        "type": "string",
                        "description": "Sort order (asc or desc)",
                        "default": "desc",
                        "enum": ["asc", "desc"],
                    },
                },
                "required": ["address"],
            },
        ),
        types.Tool(
            name="get-token-info",
            description="Get  CA address detailed token metadata  information from Solscan",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Token address on Solana blockchain",
                    },
                },
                "required": ["address"],
            },
        ),
    ]

async def make_solscan_request(client: httpx.AsyncClient, url: str) -> dict[str, Any] | None:
    """Make a request to the Solscan API with proper error handling."""
    headers = {
        "token": API_TOKEN
    }
    
    # Log the request
    logging.info(f"Request URL: {url}")
    logging.info(f"Request Headers: {headers}")
    
    try:
        response = await client.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        response_data = response.json()
        
        # Log the response
        logging.info(f"Response Status: {response.status_code}")
        logging.info(f"Response Data: {response_data}")
        
        return response_data
    except Exception as e:
        # Log any errors
        logging.error(f"Request failed: {str(e)}")
        return {"error": str(e)}

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    # Log tool call
    logging.info(f"Tool called: {name}")
    logging.info(f"Arguments: {arguments}")
    if name == "get-sol-token-price":
        if not arguments or "address" not in arguments:
            return [types.TextContent(type="text", text="Address parameter is required")]

        async with httpx.AsyncClient() as client:
            token_price_url = f"https://{API_BASE}/v2.0/token/price?address={arguments['address']}"
            price_data = await make_solscan_request(client, token_price_url)

            if not price_data:
                return [types.TextContent(type="text", text="Failed to retrieve token price data")]

            return [
                types.TextContent(
                    type="text",
                    text=str(price_data)
                )
            ]
    
    elif name == "list-sol-tokens":
        page = arguments.get("page", 1) if arguments else 1
        page_size = arguments.get("page_size", 10) if arguments else 10

        async with httpx.AsyncClient() as client:
            token_list_url = f"https://{API_BASE}/v2.0/token/list?page={page}&page_size={page_size}"
            token_list_data = await make_solscan_request(client, token_list_url)

            if not token_list_data:
                return [types.TextContent(type="text", text="Failed to retrieve token list data")]

            return [
                types.TextContent(
                    type="text",
                    text=str(token_list_data)
                )
            ]
            
    elif name == "get-token-market":
        if not arguments or "address" not in arguments:
            return [types.TextContent(type="text", text="Address parameter is required")]

        async with httpx.AsyncClient() as client:
            market_url = f"https://{API_BASE}/v2.0/token/market?address={arguments['address']}"
            market_data = await make_solscan_request(client, market_url)

            if not market_data:
                return [types.TextContent(type="text", text="Failed to retrieve token market data")]

            return [
                types.TextContent(
                    type="text",
                    text=str(market_data)
                )
            ]
            #not accurate
    # elif name == "get-trending-tokens":
    #     limit = arguments.get("limit", 10) if arguments else 10

    #     async with httpx.AsyncClient() as client:
    #         trending_url = f"https://{API_BASE}/v2.0/token/trending?limit={limit}"
    #         trending_data = await make_solscan_request(client, trending_url)

    #         if not trending_data:
    #             return [types.TextContent(type="text", text="Failed to retrieve trending tokens data")]

    #         return [
    #             types.TextContent(
    #                 type="text",
    #                 text=str(trending_data)
    #             )
    #         ]
            
    elif name == "get-latest-blocks":
        limit = arguments.get("limit", 10) if arguments else 10
        
        async with httpx.AsyncClient() as client:
            blocks_url = f"https://{API_BASE}/v2.0/block/last?limit={limit}"
            blocks_data = await make_solscan_request(client, blocks_url)
            
            if not blocks_data:
                return [types.TextContent(type="text", text="Failed to retrieve latest blocks data")]
                
            return [
                types.TextContent(
                    type="text",
                    text=str(blocks_data)
                )
            ]
            
    elif name == "get-account-info":
        if not arguments or "address" not in arguments:
            return [types.TextContent(type="text", text="Address parameter is required")]
            
        page = arguments.get("page", 1)
        page_size = arguments.get("page_size", 10)
        
        async with httpx.AsyncClient() as client:
            accounts_url = f"https://{API_BASE}/v2.0/account/token-accounts?address={arguments['address']}&type=token&page={page}&page_size={page_size}"
            accounts_data = await make_solscan_request(client, accounts_url)
            
            if not accounts_data:
                return [types.TextContent(type="text", text="Failed to retrieve account tokens data")]
                
            return [
                types.TextContent(
                    type="text",
                    text=str(accounts_data)
                )
            ]
            
    elif name == "get-account-activities":
        if not arguments or "address" not in arguments:
            return [types.TextContent(type="text", text="Address parameter is required")]
            
        page = arguments.get("page", 1)
        page_size = arguments.get("page_size", 10)
        sort_by = arguments.get("sort_by", "block_time")
        sort_order = arguments.get("sort_order", "desc")
        
        async with httpx.AsyncClient() as client:
            activities_url = (
                f"https://{API_BASE}/v2.0/account/defi/activities"
                f"?address={arguments['address']}"
                f"&page={page}"
                f"&page_size={page_size}"
                f"&sort_by={sort_by}"
                f"&sort_order={sort_order}"
            )
            activities_data = await make_solscan_request(client, activities_url)
            
            if not activities_data:
                return [types.TextContent(type="text", text="Failed to retrieve account activities data")]
                
            return [
                types.TextContent(
                    type="text",
                    text=str(activities_data)
                )
            ]
            
    elif name == "get-token-info":
        if not arguments or "address" not in arguments:
            return [types.TextContent(type="text", text="Address parameter is required")]

        async with httpx.AsyncClient() as client:
            metadata_url = f"https://{API_BASE}/v2.0/token/meta?address={arguments['address']}"
            metadata = await make_solscan_request(client, metadata_url)

            if not metadata:
                return [types.TextContent(type="text", text="Failed to retrieve token metadata")]

            return [
                types.TextContent(
                    type="text",
                    text=str(metadata)
                )
            ]
            
    else:
        raise ValueError(f"Unknown tool: {name}")

async def handle_sse(request):
    """Handle SSE connection requests"""
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options()
        )

routes = [
    Route("/sse", endpoint=handle_sse),
    Mount("/messages/", app=sse.handle_post_message),
]

app = Starlette(routes=routes, debug=True)

def start_server(host: str = "0.0.0.0", port: int = 3011):
    """Start the server"""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()

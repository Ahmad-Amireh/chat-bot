import asyncio
from fastmcp import Client

async def test_tools():
    # Connect to your MCP server
    client = Client("http://127.0.0.1:8000/mcp")

    async with client:
        # 1. List products
        result = await client.call_tool("list_products", {})
        print("list_products:", result.data)

        # 2. Add a product
        add_result = await client.call_tool("add_product", {"name": "Shawrma", "price": 2})
        print("add_product:", add_result.data)

        # 3. Update a product (replace 1 with actual product ID)
        update_result = await client.call_tool("update_product", {"product_id": 1, "price": 3})
        print("update_product:", update_result.data)

        # 4. Delete a product
        delete_result = await client.call_tool("delete_product", {"product_id": 1})
        print("delete_product:", delete_result.data)

asyncio.run(test_tools())
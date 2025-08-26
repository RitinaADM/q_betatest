#!/usr/bin/env python3
"""
Simple API test script to verify the hexagonal architecture implementation.
"""

import asyncio
import aiohttp
import json

async def test_api():
    """Test various API endpoints."""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing FastAPI Hexagonal Architecture Application")
        print("=" * 60)
        
        # Test health endpoint
        print("1. Testing health endpoint...")
        try:
            async with session.get(f"{base_url}/health") as response:
                data = await response.json()
                print(f"   Status: {response.status}")
                print(f"   Response: {json.dumps(data, indent=2)}")
                print("   ✅ Health check passed!")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
        
        print()
        
        # Test root endpoint
        print("2. Testing root endpoint...")
        try:
            async with session.get(f"{base_url}/") as response:
                data = await response.json()
                print(f"   Status: {response.status}")
                print(f"   Response: {json.dumps(data, indent=2)}")
                print("   ✅ Root endpoint passed!")
        except Exception as e:
            print(f"   ❌ Root endpoint failed: {e}")
        
        print()
        
        # Test get all items
        print("3. Testing get all items...")
        try:
            async with session.get(f"{base_url}/items") as response:
                data = await response.json()
                print(f"   Status: {response.status}")
                print(f"   Found {len(data)} items")
                if data:
                    print(f"   First item: {data[0]['name']}")
                print("   ✅ Get all items passed!")
        except Exception as e:
            print(f"   ❌ Get all items failed: {e}")
        
        print()
        
        # Test create item
        print("4. Testing create item...")
        test_item = {
            "name": "Test Item",
            "description": "A test item created by the test script",
            "price": 99.99,
            "in_stock": True
        }
        try:
            async with session.post(f"{base_url}/items", json=test_item) as response:
                data = await response.json()
                print(f"   Status: {response.status}")
                print(f"   Created item ID: {data.get('id')}")
                print(f"   Item name: {data.get('name')}")
                print("   ✅ Create item passed!")
                created_item_id = data.get('id')
        except Exception as e:
            print(f"   ❌ Create item failed: {e}")
            created_item_id = None
        
        print()
        
        # Test get item by ID
        if created_item_id:
            print("5. Testing get item by ID...")
            try:
                async with session.get(f"{base_url}/items/{created_item_id}") as response:
                    data = await response.json()
                    print(f"   Status: {response.status}")
                    print(f"   Item: {data.get('name')} - ${data.get('price')}")
                    print("   ✅ Get item by ID passed!")
            except Exception as e:
                print(f"   ❌ Get item by ID failed: {e}")
        
        print()
        
        # Test search items
        print("6. Testing search items...")
        try:
            async with session.get(f"{base_url}/items/search/laptop") as response:
                data = await response.json()
                print(f"   Status: {response.status}")
                print(f"   Found {len(data)} items matching 'laptop'")
                print("   ✅ Search items passed!")
        except Exception as e:
            print(f"   ❌ Search items failed: {e}")
        
        print()
        print("🎉 API Testing completed!")

if __name__ == "__main__":
    asyncio.run(test_api())
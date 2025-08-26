#!/usr/bin/env python3
"""
Debug script to test the new hexagonal architecture setup.
"""

import asyncio
from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka

# Test imports
try:
    from src.domain.ports.inbound.services.item_service_port import ItemServicePort
    print("✅ ItemServicePort import successful")
except ImportError as e:
    print(f"❌ ItemServicePort import failed: {e}")

try:
    from src.infrastructure.di.container import create_dishka_container
    print("✅ DI container import successful")
except ImportError as e:
    print(f"❌ DI container import failed: {e}")

try:
    from src.infrastructure.adapters.inbound.rest.item_controller import router as item_router
    print("✅ Item controller import successful")
except ImportError as e:
    print(f"❌ Item controller import failed: {e}")

async def main():
    """Main test function."""
    print("\n🔍 Testing DI Container...")
    
    try:
        container = create_dishka_container()
        print("✅ DI container creation successful")
    except Exception as e:
        print(f"❌ DI container creation failed: {e}")
        return
    
    print("\n🔍 Testing FastAPI setup...")
    
    try:
        app = FastAPI(title="Test App")
        setup_dishka(container, app)
        print("✅ FastAPI + Dishka setup successful")
    except Exception as e:
        print(f"❌ FastAPI + Dishka setup failed: {e}")
        return
    
    print("\n🔍 Testing router inclusion...")
    
    try:
        app.include_router(item_router)
        print("✅ Router inclusion successful")
    except Exception as e:
        print(f"❌ Router inclusion failed: {e}")
        return
    
    print("\n🎉 All tests passed! The restructured architecture is working.")

if __name__ == "__main__":
    asyncio.run(main())
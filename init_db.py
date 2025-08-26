#!/usr/bin/env python3
"""
Database initialization script.
Creates database tables and optionally seeds with sample data.
"""

import asyncio
import sys
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.config import (
    create_tables, 
    drop_tables, 
    AsyncSessionLocal
)
from src.infrastructure.database.models import ItemModel


async def init_database(with_sample_data: bool = False):
    """Initialize database with tables and optional sample data."""
    print("Initializing database...")
    
    # Create tables
    await create_tables()
    print("✓ Database tables created")
    
    if with_sample_data:
        await seed_sample_data()
        print("✓ Sample data seeded")
    
    print("Database initialization completed!")


async def reset_database():
    """Drop and recreate all database tables."""
    print("Resetting database...")
    
    # Drop existing tables
    await drop_tables()
    print("✓ Existing tables dropped")
    
    # Create tables
    await create_tables()
    print("✓ Database tables recreated")
    
    print("Database reset completed!")


async def seed_sample_data():
    """Seed database with sample data."""
    sample_items = [
        ItemModel(
            name="Gaming Laptop",
            description="High-performance laptop for gaming and development",
            price=1299.99,
            in_stock=True
        ),
        ItemModel(
            name="Wireless Mouse",
            description="Ergonomic wireless mouse with precision tracking",
            price=49.99,
            in_stock=True
        ),
        ItemModel(
            name="Mechanical Keyboard",
            description="RGB mechanical keyboard with blue switches",
            price=129.99,
            in_stock=False
        ),
        ItemModel(
            name="Monitor 27 inch",
            description="4K UHD monitor with HDR support",
            price=399.99,
            in_stock=True
        ),
        ItemModel(
            name="USB-C Hub",
            description="Multi-port USB-C hub with HDMI and ethernet",
            price=79.99,
            in_stock=True
        )
    ]
    
    async with AsyncSessionLocal() as session:
        try:
            session.add_all(sample_items)
            await session.commit()
            print(f"✓ Added {len(sample_items)} sample items")
        except Exception as e:
            await session.rollback()
            print(f"✗ Error seeding sample data: {e}")
            raise


async def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "init":
            sample_data = "--with-data" in sys.argv
            await init_database(with_sample_data=sample_data)
        elif command == "reset":
            await reset_database()
            if "--with-data" in sys.argv:
                await seed_sample_data()
        elif command == "seed":
            await seed_sample_data()
        else:
            print("Unknown command. Use: init, reset, or seed")
            print("Options: --with-data (adds sample data)")
            sys.exit(1)
    else:
        # Default: init with sample data
        await init_database(with_sample_data=True)


if __name__ == "__main__":
    print("Database Management Script")
    print("Usage:")
    print("  python init_db.py init [--with-data]  # Initialize database")
    print("  python init_db.py reset [--with-data] # Reset database")
    print("  python init_db.py seed               # Add sample data")
    print()
    
    asyncio.run(main())
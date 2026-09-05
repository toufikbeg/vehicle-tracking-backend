import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.security import get_password_hash
from app.database import Base

# Docker ke andar postgres hostname use karo
DATABASE_URL = "postgresql+asyncpg://postgres:password@postgres:5432/gps_tracking"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


async def seed():
    # Import models here to avoid circular imports
    from app.models.user import User
    from app.models.route import BusRoute
    from app.models.vehicle import Vehicle
    from app.models import user, route, vehicle, gps  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Create Routes
        route_a = BusRoute(
            route_name="City Center to Airport",
            route_code="ROUTE-A",
            description="Express route from city center to airport",
            start_location="City Center, MG Road",
            end_location="International Airport",
            waypoints=[
                {"lat": 12.9716, "lng": 77.5946},
                {"lat": 12.9610, "lng": 77.6100},
                {"lat": 12.9500, "lng": 77.6200},
                {"lat": 12.9352, "lng": 77.6245},
            ],
        )
        route_b = BusRoute(
            route_name="University to Tech Park",
            route_code="ROUTE-B",
            description="Campus shuttle to tech park",
            start_location="State University",
            end_location="Electronic City Tech Park",
            waypoints=[
                {"lat": 13.0827, "lng": 80.2707},
                {"lat": 13.0700, "lng": 80.2600},
                {"lat": 13.0569, "lng": 80.2425},
            ],
        )
        db.add_all([route_a, route_b])
        await db.flush()

        # Create Vehicles
        bus_001 = Vehicle(
            vehicle_id="BUS-001",
            vehicle_number="KA-01-AB-1234",
            model="Volvo 9400",
            capacity=45,
            route_id=route_a.id,
        )
        bus_002 = Vehicle(
            vehicle_id="BUS-002",
            vehicle_number="KA-02-CD-5678",
            model="Tata Motors Ultra",
            capacity=40,
            route_id=route_b.id,
        )
        db.add_all([bus_001, bus_002])
        await db.flush()

        # Create Users
        user_a = User(
            username="user_a",
            email="usera@example.com",
            full_name="Alice Johnson",
            hashed_password=get_password_hash("password123"),
            assigned_route_id=route_a.id,
            assigned_vehicle_id=bus_001.id,
        )
        user_b = User(
            username="user_b",
            email="userb@example.com",
            full_name="Bob Smith",
            hashed_password=get_password_hash("password123"),
            assigned_route_id=route_b.id,
            assigned_vehicle_id=bus_002.id,
        )
        admin = User(
            username="admin",
            email="admin@example.com",
            full_name="System Admin",
            hashed_password=get_password_hash("admin123"),
            is_admin=True,
        )
        db.add_all([user_a, user_b, admin])
        await db.commit()

        print("✅ Seed data created successfully!")
        print("\n📋 Test Credentials:")
        print("  User A → username: user_a, password: password123")
        print("  User B → username: user_b, password: password123")
        print("  Admin  → username: admin,  password: admin123")


if __name__ == "__main__":
    asyncio.run(seed())
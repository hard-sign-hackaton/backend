import asyncio
import os
import uuid
from datetime import datetime, timezone

import asyncpg


DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/DisplayDB"
MOCK_DISPLAY_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    return url.replace("postgresql+asyncpg://", "postgresql://")


async def main() -> None:
    now = datetime.now(timezone.utc)
    connection = await asyncpg.connect(get_database_url())

    await connection.execute(
        """
        INSERT INTO displays (
            id,
            title,
            location,
            status,
            pairing_code,
            ujin_complex_id,
            ujin_building_id,
            last_seen_at,
            created_at,
            updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8, $8)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            location = EXCLUDED.location,
            status = EXCLUDED.status,
            pairing_code = EXCLUDED.pairing_code,
            ujin_complex_id = EXCLUDED.ujin_complex_id,
            ujin_building_id = EXCLUDED.ujin_building_id,
            last_seen_at = EXCLUDED.last_seen_at,
            updated_at = EXCLUDED.updated_at
        """,
        MOCK_DISPLAY_ID,
        "Mock lobby display",
        "Entrance 1",
        "online",
        "MOCK-WS-001",
        63,
        121,
        now,
    )
    await connection.close()

    print(f"mock_display_id={MOCK_DISPLAY_ID}")
    print("websocket_url=ws://localhost:8000/ws/displays/" + str(MOCK_DISPLAY_ID))


if __name__ == "__main__":
    asyncio.run(main())

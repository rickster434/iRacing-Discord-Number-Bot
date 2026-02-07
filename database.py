"""
Database handler for iRacing Number Bot
Manages SQLite database for number assignments and guild configurations
"""

import aiosqlite
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger('iRacingBot.Database')

class Database:
    def __init__(self, db_path: str = "iracing_numbers.db"):
        self.db_path = db_path
        self.db = None

    async def initialize(self):
        """Initialize the database and create tables"""
        try:
            self.db = await aiosqlite.connect(self.db_path)
            await self._create_tables()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def _create_tables(self):
        """Create database tables if they don't exist"""
        # Guild configurations table
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id INTEGER PRIMARY KEY,
                league_id INTEGER,
                min_number INTEGER DEFAULT 0,
                max_number INTEGER DEFAULT 999,
                admin_role_id INTEGER,
                announcement_channel_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Number assignments table
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS number_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                car_number INTEGER NOT NULL,
                discord_user_id INTEGER,
                iracing_id INTEGER,
                discord_username TEXT,
                iracing_name TEXT,
                status TEXT DEFAULT 'claimed',
                claimed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                synced_with_iracing INTEGER DEFAULT 0,
                iracing_verified INTEGER DEFAULT 0,
                notes TEXT,
                UNIQUE(guild_id, car_number),
                FOREIGN KEY (guild_id) REFERENCES guild_config(guild_id)
            )
        """)

        # Audit log table
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await self.db.commit()
        logger.info("Database tables created/verified")

    # Guild Configuration Methods
    async def get_guild_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get configuration for a guild"""
        async with self.db.execute(
            "SELECT * FROM guild_config WHERE guild_id = ?",
            (guild_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(zip([d[0] for d in cursor.description], row))
            return None

    async def set_guild_config(self, guild_id: int, **kwargs):
        """Set or update guild configuration"""
        config = await self.get_guild_config(guild_id)

        if config:
            # Update existing config
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            set_clause += ", updated_at = CURRENT_TIMESTAMP"
            values = list(kwargs.values()) + [guild_id]

            await self.db.execute(
                f"UPDATE guild_config SET {set_clause} WHERE guild_id = ?",
                values
            )
        else:
            # Insert new config
            columns = ["guild_id"] + list(kwargs.keys())
            placeholders = ", ".join(["?"] * len(columns))
            values = [guild_id] + list(kwargs.values())

            await self.db.execute(
                f"INSERT INTO guild_config ({', '.join(columns)}) VALUES ({placeholders})",
                values
            )

        await self.db.commit()

    async def get_all_guild_configs(self) -> List[Dict[str, Any]]:
        """Get all guild configurations"""
        async with self.db.execute("SELECT * FROM guild_config") as cursor:
            rows = await cursor.fetchall()
            return [dict(zip([d[0] for d in cursor.description], row)) for row in rows]

    # Number Assignment Methods
    async def claim_number(
        self,
        guild_id: int,
        car_number: int,
        discord_user_id: int,
        discord_username: str,
        iracing_id: Optional[int] = None,
        iracing_name: Optional[str] = None
    ) -> bool:
        """Claim a car number for a user"""
        try:
            await self.db.execute("""
                INSERT INTO number_assignments
                (guild_id, car_number, discord_user_id, discord_username, iracing_id, iracing_name, status)
                VALUES (?, ?, ?, ?, ?, ?, 'claimed')
            """, (guild_id, car_number, discord_user_id, discord_username, iracing_id, iracing_name))

            await self.db.commit()

            # Log the action
            await self.log_action(
                guild_id,
                discord_user_id,
                "claim_number",
                f"Claimed number {car_number}"
            )

            return True
        except aiosqlite.IntegrityError:
            # Number already claimed
            return False
        except Exception as e:
            logger.error(f"Error claiming number: {e}")
            return False

    async def release_number(self, guild_id: int, car_number: int, user_id: int) -> bool:
        """Release a car number"""
        try:
            cursor = await self.db.execute("""
                DELETE FROM number_assignments
                WHERE guild_id = ? AND car_number = ? AND discord_user_id = ?
            """, (guild_id, car_number, user_id))

            await self.db.commit()

            if cursor.rowcount > 0:
                await self.log_action(
                    guild_id,
                    user_id,
                    "release_number",
                    f"Released number {car_number}"
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Error releasing number: {e}")
            return False

    async def get_number_assignment(self, guild_id: int, car_number: int) -> Optional[Dict[str, Any]]:
        """Get assignment information for a specific number"""
        async with self.db.execute(
            "SELECT * FROM number_assignments WHERE guild_id = ? AND car_number = ?",
            (guild_id, car_number)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(zip([d[0] for d in cursor.description], row))
            return None

    async def get_user_numbers(self, guild_id: int, discord_user_id: int) -> List[Dict[str, Any]]:
        """Get all numbers assigned to a user"""
        async with self.db.execute(
            "SELECT * FROM number_assignments WHERE guild_id = ? AND discord_user_id = ? ORDER BY car_number",
            (guild_id, discord_user_id)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(zip([d[0] for d in cursor.description], row)) for row in rows]

    async def get_all_assignments(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get all number assignments for a guild"""
        async with self.db.execute(
            "SELECT * FROM number_assignments WHERE guild_id = ? ORDER BY car_number",
            (guild_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(zip([d[0] for d in cursor.description], row)) for row in rows]

    async def get_available_numbers(self, guild_id: int) -> List[int]:
        """Get list of available numbers based on guild config"""
        config = await self.get_guild_config(guild_id)

        if not config:
            # Default range if no config
            min_num, max_num = 0, 999
        else:
            min_num = config.get('min_number', 0)
            max_num = config.get('max_number', 999)

        # Get all claimed numbers
        async with self.db.execute(
            "SELECT car_number FROM number_assignments WHERE guild_id = ?",
            (guild_id,)
        ) as cursor:
            claimed = [row[0] for row in await cursor.fetchall()]

        # Return available numbers
        return [num for num in range(min_num, max_num + 1) if num not in claimed]

    async def sync_iracing_assignment(
        self,
        guild_id: int,
        car_number: int,
        iracing_id: int,
        iracing_data: Dict[str, Any]
    ):
        """Sync an assignment from iRacing"""
        iracing_name = iracing_data.get('display_name', 'Unknown')

        try:
            await self.db.execute("""
                INSERT INTO number_assignments
                (guild_id, car_number, iracing_id, iracing_name, status, synced_with_iracing, iracing_verified)
                VALUES (?, ?, ?, ?, 'synced', 1, 1)
                ON CONFLICT(guild_id, car_number) DO UPDATE SET
                    iracing_id = excluded.iracing_id,
                    iracing_name = excluded.iracing_name,
                    synced_with_iracing = 1,
                    iracing_verified = 1
            """, (guild_id, car_number, iracing_id, iracing_name))

            await self.db.commit()
        except Exception as e:
            logger.error(f"Error syncing iRacing assignment: {e}")

    async def mark_synced(self, guild_id: int, car_number: int):
        """Mark a number as synced with iRacing"""
        await self.db.execute("""
            UPDATE number_assignments
            SET synced_with_iracing = 1
            WHERE guild_id = ? AND car_number = ?
        """, (guild_id, car_number))
        await self.db.commit()

    # Audit Log Methods
    async def log_action(self, guild_id: int, user_id: int, action: str, details: str):
        """Log an action to the audit log"""
        try:
            await self.db.execute("""
                INSERT INTO audit_log (guild_id, user_id, action, details)
                VALUES (?, ?, ?, ?)
            """, (guild_id, user_id, action, details))
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error logging action: {e}")

    async def get_audit_log(self, guild_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent audit log entries"""
        async with self.db.execute(
            "SELECT * FROM audit_log WHERE guild_id = ? ORDER BY timestamp DESC LIMIT ?",
            (guild_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(zip([d[0] for d in cursor.description], row)) for row in rows]

    async def close(self):
        """Close the database connection"""
        if self.db:
            await self.db.close()

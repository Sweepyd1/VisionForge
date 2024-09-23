import asyncpg
import datetime
from loguru import logger
from typing import Union, Any, List, Dict

from data import config as cfg


class DictRecord(asyncpg.Record):
    def __getitem__(self, key) -> Any:
        value = super().__getitem__(key)
        if isinstance(value, asyncpg.Record):
            return DictRecord(value)

        return value

    def to_dict(self) -> dict:
        return self._convert_records_to_dicts(dict(super().items()))

    def _convert_records_to_dicts(self, obj) -> Union[dict, str, List[dict], Dict[Any, Any], Any]:
        if isinstance(obj, dict):
            return {k: self._convert_records_to_dicts(v) for k, v in obj.items()}
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, list):
            return [self._convert_records_to_dicts(item) for item in obj]
        elif isinstance(obj, asyncpg.Record):
            return dict(obj)
        else:
            return obj

    def __repr__(self) -> str:
        return str(self.to_dict())


class DB:
    db: asyncpg.Pool

    async def close(self) -> None:
        await self.db.close()

    async def init_database(self) -> None:
        self.db = await asyncpg.create_pool(
            host=cfg.db_host,
            port=cfg.db_port,
            user=cfg.db_username,
            password=cfg.db_password,
            database=cfg.db_name,
            record_class=DictRecord
        )

        await self._crete_tables()
        await self._add_gate_manager_trigger()
        logger.success("База данных инициализирована успешно!")

    async def _crete_tables(self) -> None:
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                refresh_token TEXT
            );
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS gates (
                id SERIAL NOT NULL PRIMARY KEY,
                serial_number TEXT NOT NULL DEFAULT gen_random_uuid(),
                name TEXT NOT NULL DEFAULT 'Шлагбаум №...', 
                owner TEXT NOT NULL, 
                country TEXT NOT NULL DEFAULT 'Russia',
                city TEXT,
                address TEXT,
                
                FOREIGN KEY (owner) REFERENCES users(username)  
            );
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS cams (
                id SERIAL NOT NULL PRIMARY KEY,
                ip_address TEXT NOT NULL,
                login TEXT,
                password TEXT,
                gate_id INT NOT NULL,
                
                FOREIGN KEY (gate_id) REFERENCES gates(id) 
            );
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS gate_history (
                id SERIAL NOT NULL PRIMARY KEY,
                gate_id INT NOT NULL,
                is_opened BOOLEAN NOT NULL,
                username TEXT,
                is_ai BOOLEAN NOT NULL,
                date TIMESTAMP NOT NULL DEFAULT now(),
                
                FOREIGN KEY (username) REFERENCES users(username), 
                FOREIGN KEY (gate_id) REFERENCES gates(id) 
            );
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS gate_managers (
                id BIGSERIAL NOT NULL PRIMARY KEY,
                username TEXT NOT NULL,
                gate_id INT NOT NULL,
                is_admin BOOLEAN NOT NULL DEFAULT FALSE,
                
                FOREIGN KEY (username) REFERENCES users(username), 
                FOREIGN KEY (gate_id) REFERENCES gates(id)
            )
        """)

    async def _add_gate_manager_trigger(self):
        trigger_exists = await self.db.fetchval("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.triggers
                WHERE trigger_name = 'gate_insert_trigger'
                AND event_object_table = 'gates'
            ) AS trigger_exists;
        """)

        if not trigger_exists:
            await self.db.execute("""
                CREATE OR REPLACE FUNCTION add_gate_manager()
                RETURNS TRIGGER AS $$
                DECLARE
                    new_gate_id INT;
                    gate_count INT;
                BEGIN
                    INSERT INTO gate_managers (username, gate_id, is_admin)
                    VALUES (NEW.owner, NEW.id, TRUE)
                    RETURNING id INTO new_gate_id;
    
                    IF NEW.name IS NULL THEN
                        SELECT COUNT(*) INTO gate_count
                        FROM gates
                        WHERE owner = NEW.owner;
            
                        NEW.name := 'Шлагбаум №' || gate_count;
                    END IF;
    
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
            await self.db.execute("""
                CREATE TRIGGER gate_insert_trigger
                AFTER INSERT ON gates
                FOR EACH ROW
                EXECUTE FUNCTION add_gate_manager();
            """)

    async def create_user(self, email: str, username: str, hashed_password: str, name: str) -> bool:
        try:
            await self.db.execute(
                "INSERT INTO users(email, username, hashed_password, name) VALUES($1, $2, $3, $4)",
                email, username, hashed_password, name
            )

            return True
        except asyncpg.exceptions.UniqueViolationError:
            return False

        except Exception as e:
            print(e)
            return False

    async def get_user_by_username(self, username: str) -> Union[DictRecord, None]:
        response = await self.db.fetchrow("SELECT * FROM users WHERE username=$1", username)
        return response

    async def update_refresh_token_by_username(self, username: str, refresh_token: str) -> None:
        await self.db.execute(
            "UPDATE users SET refresh_token=$1 WHERE username=$2",
            refresh_token,
            username
        )

    async def get_user_gates(self, username: str) -> List[DictRecord]:
        gates = await self.db.fetch(
            """
            SELECT
                m.gate_id,
                g.name AS gate_name,
                g.owner,
                g.country,
                g.city,
                g.address,
                m.is_admin
            FROM gate_managers m, gates g
            WHERE 
                m.gate_id=g.id 
                AND m.username = $1
            """,
            username
        )

        return gates

    async def get_full_data_gate_by_id(self, gate_id: int) -> DictRecord:
        gate = await self.db.fetchrow("""
            WITH manager_data AS (
                SELECT
                    m.gate_id,
                    m.id,
                    json_build_object(
                        'username', u.username,
                        'name', u.name
                    ) AS manager_obj
                FROM gate_managers m
                LEFT JOIN users u ON u.username = m.username
                WHERE m.is_admin = false
            )
            SELECT
                g.*,
                json_build_object(
                    'cam_id', c.id,
                    'ip_address', c.ip_address,
                    'login', c.login,
                    'password_length', length(c.password)
                ) AS cam,
                COALESCE(
                    json_object_agg(
                        m.id,
                        m.manager_obj
                    ) FILTER (WHERE m.id IS NOT NULL),
                    NULL
                ) AS managers
            FROM gates g
            LEFT JOIN cams AS c ON g.id = c.gate_id
            LEFT JOIN manager_data m ON m.gate_id = g.id
            WHERE g.id=$1
            GROUP BY g.id, c.id
        """, gate_id)

        return gate

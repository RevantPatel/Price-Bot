import aiosqlite

DB_FILE = "prices.db"

async def initialize():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS watches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                url TEXT,
                product_name TEXT,
                current_price REAL,
                previous_price REAL
            )
        """)
        await db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user_url ON watches(user_id, url)")
        
        cursor = await db.execute("PRAGMA table_info(watches)")
        columns = [row[1] for row in await cursor.fetchall()]
        
        if "target_price" in columns or "previous_price" not in columns:
            await db.execute("ALTER TABLE watches RENAME TO watches_old")
            await db.execute("""
                CREATE TABLE watches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    url TEXT,
                    product_name TEXT,
                    current_price REAL,
                    previous_price REAL
                )
            """)
            await db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user_url ON watches(user_id, url)")
            
            await db.execute("""
                INSERT INTO watches (id, user_id, url, product_name, current_price, previous_price)
                SELECT id, user_id, url, product_name, current_price, current_price FROM watches_old
            """)
            await db.execute("DROP TABLE watches_old")
            
        await db.commit()

async def add_watch(user_id, url, name, price):
    async with aiosqlite.connect(DB_FILE) as db:
        try:
            await db.execute(
                "INSERT INTO watches (user_id, url, product_name, current_price, previous_price) VALUES (?, ?, ?, ?, ?)",
                (user_id, url, name, price, price)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

async def get_user_watches(user_id):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, product_name, current_price, previous_price FROM watches WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchall()

async def delete_watch(watch_id, user_id):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DELETE FROM watches WHERE id = ? AND user_id = ?", (watch_id, user_id))
        await db.commit()

async def stream_watches():
    db = await aiosqlite.connect(DB_FILE)
    cursor = await db.execute("SELECT id, url, current_price, user_id, product_name FROM watches")
    return db, cursor

async def update_price(watch_id, new_price):
    async with aiosqlite.connect(DB_FILE) as db:
        # Set previous_price = current_price, and current_price = new_price
        await db.execute(
            "UPDATE watches SET previous_price = current_price, current_price = ? WHERE id = ?",
            (new_price, watch_id)
        )
        await db.commit()
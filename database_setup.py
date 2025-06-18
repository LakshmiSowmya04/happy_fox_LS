
import psycopg2
import config  

def setup_database():
    """
    Connects to the PostgreSQL database and creates the 'emails' table
    if it does not already exist.
    """
    table_creation_query = """
    CREATE TABLE IF NOT EXISTS emails (
        id SERIAL PRIMARY KEY,
        message_id VARCHAR(255) NOT NULL UNIQUE,
        from_address VARCHAR(255),
        subject VARCHAR(500),
        message_body TEXT,
        received_date TIMESTAMPTZ
    );
    """
    try:
        with psycopg2.connect(config.DB_DSN) as conn:
            with conn.cursor() as cursor:
                cursor.execute(table_creation_query)
                conn.commit()
                print("Database table 'emails' is ready.")
    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        print("Please check your DB_DSN in config.py")
    except psycopg2.Error as e:
        print(f"A database error occurred: {e}")

if __name__ == "__main__":
    setup_database()
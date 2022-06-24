# Note: the module name is psycopg, not psycopg3
import psycopg

# Connect to an existing database
conn = psycopg.connect("host=localhost dbname=postgres user=postgres password=postgres", autocommit=True)
cur = conn.cursor()
cur.execute("CREATE DATABASE noew")
conn.commit()
conn.close()

with psycopg.connect("host=localhost dbname=noew user=azureuser password=1234") as conn:


    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE sentences (
                id serial PRIMARY KEY,
                created_at timestamp,
                text text,
                fetched boolean default false,
                annotated boolean default false
                )
            """)
        # Execute a command: this creates a new table
        cur.execute("""
            CREATE TABLE annotations (
                id serial PRIMARY KEY,
                sentence_id int NOT NULL,
                created_at timestamp,
                score int,
                magnitude int,
                happiness boolean,
                sadness boolean,
                fear boolean,
                disgust boolean,
                anger boolean,
                surprise boolean,
                CONSTRAINT sentence_id FOREIGN KEY(sentence_id) REFERENCES sentences(id) 
                )
            """)

        conn.commit()

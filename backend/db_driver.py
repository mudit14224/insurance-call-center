import psycopg2
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

if POSTGRES_PASSWORD:
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
else:
    DATABASE_URL = f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


@dataclass
class Policy:
    policy_id: str
    customer_name: str
    policy_type: str
    start_date: str
    end_date: str
    status: str

@dataclass
class Customer:
    customer_id: int
    name: str
    email: Optional[str]
    phone: Optional[str]

@dataclass
class Claim:
    claim_id: int
    policy_id: int
    status: str
    amount: float
    description: str

class DatabaseDriver:
    def __init__(self, db_url: str = DATABASE_URL):
        self.db_url = db_url
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = psycopg2.connect(self.db_url)
        try: 
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    phone VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create policies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS policies (
                    policy_id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers(customer_id),
                    policy_number VARCHAR(50) UNIQUE NOT NULL,
                    policy_type VARCHAR(100),
                    start_date DATE,
                    end_date DATE,
                    status VARCHAR(50),
                    premium NUMERIC(12, 2)
                )
            """)

            # Create claims table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS claims (
                    claim_id SERIAL PRIMARY KEY,
                    policy_id INTEGER REFERENCES policies(policy_id),
                    date_filed DATE DEFAULT CURRENT_DATE,
                    status VARCHAR(50),
                    amount NUMERIC(12, 2),
                    description TEXT
                )
            """)
            conn.commit()

    def create_policy(self, customer_id: int, policy_number: str, policy_type: str, start_date: str, end_date: str, status: str, premium: float) -> Policy:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO policies (customer_id, policy_number, policy_type, start_date, end_date, status, premium)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING policy_id
            """, (customer_id, policy_number, policy_type, start_date, end_date, status, premium))
            policy_id = cursor.fetchone()[0]
            conn.commit()
            return Policy(policy_id=policy_id, customer_name="", policy_type=policy_type, start_date=start_date, end_date=end_date, status=status)
        
    def get_policy_by_number(self, policy_number: str) -> Optional[Policy]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.policy_id, c.name, p.policy_type, p.start_date, p.end_date, p.status
                FROM policies p
                JOIN customers c ON p.customer_id = c.customer_id
                WHERE p.policy_number = %s
            """, (policy_number,))
            row = cursor.fetchone()
            if not row:
                return None

            return Policy(
                policy_id=row[0],
                customer_name=row[1],
                policy_type=row[2],
                start_date=str(row[3]),
                end_date=str(row[4]),
                status=row[5]
            )
        
    def create_claim(self, policy_id: int, amount: float, description: str, status: str = "Filed") -> Claim: 
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO claims (policy_id, amount, description, status)
                VALUES (%s, %s, %s, %s)
                RETURNING claim_id
            """, (policy_id, amount, description, status))
            claim_id = cursor.fetchone()[0]
            conn.commit()
            return Claim(claim_id=claim_id, policy_id=policy_id, status=status, amount=amount, description=description)
        
    def get_claim_status(self, claim_id: int) -> Optional[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM claims WHERE claim_id = %s", (claim_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        
    def get_customer_by_email_or_phone(self, email: str, phone: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT customer_id FROM customers WHERE email = %s OR phone = %s
            """, (email, phone))
            row = cursor.fetchone()
            return row[0] if row else None
        
    def create_customer(self, name: str, email: str, phone: str) -> Customer:
        # Check if customer exists first
        existing_customer_id = self.get_customer_by_email_or_phone(email, phone)
        if existing_customer_id:
            # Fetch the existing customer details
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT customer_id, name, email, phone
                    FROM customers
                    WHERE customer_id = %s
                """, (existing_customer_id,))
                row = cursor.fetchone()
                if row:
                    return Customer(customer_id=row[0], name=row[1], email=row[2], phone=row[3])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO customers (name, email, phone)
                VALUES (%s, %s, %s)
                RETURNING customer_id
            """, (name, email, phone))
            customer_id = cursor.fetchone()[0]
            conn.commit()

            return Customer(customer_id=customer_id, name=name, email=email, phone=phone)
    


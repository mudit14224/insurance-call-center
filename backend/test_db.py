from db_driver import DatabaseDriver

def test_connection():
    try:
        # Initialize the database driver
        db = DatabaseDriver()
        print("✅ Successfully connected to database and created tables!")
        
        # Create a test customer first
        # with db._get_connection() as conn:
        #     cursor = conn.cursor()
        #     cursor.execute("""
        #         INSERT INTO customers (name, email, phone)
        #         VALUES (%s, %s, %s)
        #         RETURNING customer_id
        #     """, ("Test Customer", "test@example.com", "123-456-7890"))
        #     customer_id = cursor.fetchone()[0]
        #     conn.commit()
        #     print(f"✅ Successfully created test customer with ID: {customer_id}")
        
        # # Test creating a policy
        # policy = db.create_policy(
        #     customer_id=customer_id,
        #     policy_number="TEST001",
        #     policy_type="Home Insurance",
        #     start_date="2024-03-20",
        #     end_date="2025-03-20",
        #     status="Active",
        #     premium=1200.00
        # )
        # print(f"✅ Successfully created test policy: {policy}")

        with db._get_connection() as conn:
            cursor = conn.cursor()

            # Fetch customers
            cursor.execute("SELECT * FROM customers")
            customers = cursor.fetchall()
            print("Customers:")
            for customer in customers:
                print(customer)

            # Fetch claims
            cursor.execute("SELECT * FROM claims")
            claims = cursor.fetchall()
            print("\nClaims:")
            for claim in claims:
                print(claim)

            # Fetch policies
            cursor.execute("SELECT * FROM policies")
            policies = cursor.fetchall()
            print("\nPolicies:")
            for policy in policies:
                print(policy)

            cursor.execute("SELECT status FROM claims WHERE claim_id = %s", (1,))
            row = cursor.fetchone()
            print(row[0])
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_connection() 
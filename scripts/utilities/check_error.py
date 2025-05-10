from sqlalchemy import create_engine, text
from app.models.user import User
from app import db

def check_error():
    engine = create_engine('postgresql://localhost/expiry_tracker_v2')
    
    # Try to execute the exact query that's failing
    with engine.connect() as conn:
        try:
            result = conn.execute(text("""
                SELECT * FROM users 
                WHERE email = :email 
                LIMIT 1
            """), {"email": "divyanshsingh1800@gmail.com"})
            print("Query executed successfully!")
            for row in result:
                print(f"Found user: {row.username}")
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            
    # Check if the column exists in the database
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'login_attempts'
            );
        """))
        exists = result.scalar()
        print(f"\nDoes login_attempts column exist? {exists}")

if __name__ == '__main__':
    check_error() 
from sqlalchemy import create_engine, text

def check_columns():
    engine = create_engine('postgresql://localhost/expiry_tracker_v2')
    
    with engine.connect() as conn:
        # Get column information from information schema
        result = conn.execute(text("""
            SELECT column_name, data_type, character_maximum_length, 
                   column_default, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """))
        
        print("\nDetailed Users Table Structure:")
        for row in result:
            print(f"\nColumn: {row.column_name}")
            print(f"  Type: {row.data_type}", end="")
            if row.character_maximum_length:
                print(f"({row.character_maximum_length})")
            else:
                print()
            print(f"  Default: {row.column_default}")
            print(f"  Nullable: {row.is_nullable}")

if __name__ == '__main__':
    check_columns() 
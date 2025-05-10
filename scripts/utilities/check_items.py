from sqlalchemy import create_engine, text

def check_items_data():
    engine = create_engine('postgresql://localhost/expiry_tracker_v2')
    
    with engine.connect() as conn:
        # Get detailed items information
        result = conn.execute(text("""
            SELECT i.*, u.username as owner
            FROM items i
            JOIN users u ON i.user_id = u.id
            ORDER BY i.id
        """))
        
        print("\nItems Details:")
        for row in result:
            print(f"\nItem {row.id}: {row.name}")
            print(f"  Owner: {row.owner}")
            print(f"  Description: {row.description}")
            print(f"  Quantity: {row.quantity} {row.unit}")
            print(f"  Batch Number: {row.batch_number}")
            print(f"  Purchase Date: {row.purchase_date}")
            print(f"  Expiry Date: {row.expiry_date}")
            print(f"  Status: {row.status}")
            print(f"  Location: {row.location}")

if __name__ == '__main__':
    check_items_data() 
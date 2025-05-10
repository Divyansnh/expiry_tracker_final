from app import create_app
from app.tasks.cleanup import cleanup_expired_items

def test_cleanup():
    app = create_app()
    with app.app_context():
        print("Starting cleanup test...")
        cleanup_expired_items()
        print("Cleanup test completed!")

if __name__ == '__main__':
    test_cleanup() 
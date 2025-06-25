#!/bin/bash

# Setup script for Expiry Tracker Flask Application
# This script helps new users set up the application after cloning the repository.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
        PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python version $PYTHON_VERSION is compatible"
            return 0
        else
            print_error "Python 3.8+ required. Current version: $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8 or higher."
        return 1
    fi
}

# Function to check virtual environment
check_virtual_environment() {
    if [ -n "$VIRTUAL_ENV" ]; then
        print_success "Running in virtual environment: $VIRTUAL_ENV"
    else
        print_warning "Not running in virtual environment"
        print_warning "It's recommended to use a virtual environment"
        print_status "You can create one with: python3 -m venv venv"
        print_status "Then activate it with: source venv/bin/activate"
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "Requirements file not found: requirements.txt"
        return 1
    fi
    
    if python3 -m pip install -r requirements.txt; then
        print_success "Dependencies installed successfully"
        return 0
    else
        print_error "Failed to install dependencies"
        return 1
    fi
}

# Function to create .env file
create_env_file() {
    if [ -f ".env" ]; then
        print_success ".env file already exists"
        return 0
    fi
    
    if [ -f ".env.example" ]; then
        print_status "Creating .env file from .env.example..."
        cp .env.example .env
        print_success ".env file created from .env.example"
        print_warning "Please update .env file with your actual configuration"
        return 0
    else
        print_warning "No .env.example file found"
        print_status "Creating basic .env file..."
        
        cat > .env << 'EOF'
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://localhost/expiry_tracker_v2

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Zoho Configuration (Optional)
ZOHO_CLIENT_ID=your-zoho-client-id
ZOHO_CLIENT_SECRET=your-zoho-client-secret
ZOHO_REDIRECT_URI=http://localhost:5000/auth/zoho/callback
ZOHO_ORGANIZATION_ID=your-zoho-org-id

# Azure Computer Vision (Optional)
AZURE_VISION_KEY=your-azure-vision-key
AZURE_VISION_ENDPOINT=your-azure-vision-endpoint
EOF
        
        print_success "Basic .env file created"
        print_warning "Please update .env file with your configuration"
        return 0
    fi
}

# Function to create directories
create_directories() {
    print_status "Creating necessary directories..."
    
    directories=(
        "logs"
        "app/static/uploads"
        "app/flask_session"
        "debug_images"
        "test_images"
        "oauth_states"
    )
    
    for directory in "${directories[@]}"; do
        mkdir -p "$directory"
    done
    
    print_success "Required directories created"
}

# Function to run database setup
run_database_setup() {
    print_status "=== Database Setup ==="
    
    # Check if Flask is installed
    if ! command_exists flask; then
        print_error "Flask CLI not found. Make sure Flask is installed."
        return 1
    fi
    
    # Check if migrations directory exists
    if [ ! -d "migrations" ]; then
        print_warning "Migrations directory not found. Creating initial migration..."
        if flask db init; then
            if flask db migrate -m "Initial migration"; then
                print_success "Initial migration created"
            else
                print_error "Failed to create initial migration"
                return 1
            fi
        else
            print_error "Failed to initialize migrations"
            return 1
        fi
    fi
    
    # Run migrations
    print_status "Running database migrations..."
    if flask db upgrade; then
        print_success "Database migrations completed successfully"
    else
        print_error "Migration failed"
        return 1
    fi
    
    print_success "Database setup completed successfully"
    return 0
}

# Function to print success message
print_success_message() {
    echo ""
    print_success "Setup completed successfully!"
    echo ""
    print_status "Next steps:"
    print_status "1. Update your .env file with your actual configuration"
    print_status "2. Start the application: python run.py"
    print_status "3. Open your browser and go to: http://localhost:5000"
    echo ""
    print_status "For more information, see the README.md file"
    echo ""
}

# Main setup function
main() {
    echo "🚀 Starting Expiry Tracker Setup"
    echo "Application root: $(pwd)"
    echo ""
    
    # Check if we're in the right directory
    if [ ! -d "app" ]; then
        print_error "Invalid application root. Make sure you're running this from the project directory."
        exit 1
    fi
    
    # Check Python version
    if ! check_python_version; then
        exit 1
    fi
    
    # Check virtual environment
    check_virtual_environment
    
    # Install dependencies
    if ! install_dependencies; then
        exit 1
    fi
    
    # Create .env file
    if ! create_env_file; then
        exit 1
    fi
    
    # Create directories
    if ! create_directories; then
        exit 1
    fi
    
    # Database setup (optional)
    if [ "$SKIP_DB" != "true" ]; then
        if ! run_database_setup; then
            print_warning "Database setup failed. You can run it manually later."
        fi
    else
        print_status "⏭ Skipping database setup as requested"
    fi
    
    print_success_message
}

# Parse command line arguments
SKIP_DB=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-db)
            SKIP_DB=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Setup script for Expiry Tracker Flask Application"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-db     Skip database initialization and migrations"
            echo "  --verbose, -v Enable verbose output"
            echo "  --help, -h    Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0              # Run complete setup"
            echo "  $0 --skip-db    # Skip database setup"
            echo "  $0 --verbose    # Enable verbose output"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Set verbose mode
if [ "$VERBOSE" = "true" ]; then
    set -x
fi

# Run main setup
main 
#!/bin/bash
# Aura Analytics Dashboard - Quick Launcher
# Filename: launch-aura.sh

echo "==========================================="
echo "   🚀 Aura Analytics Dashboard Launcher   "
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[AURA]${NC} $1"
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

# Check if Node.js is installed (for future Phase 2)
check_nodejs() {
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v)
        print_success "Node.js found: $NODE_VERSION"
        return 0
    else
        print_warning "Node.js not installed (needed for Phase 2)"
        return 1
    fi
}

# Check if Python is available (alternative server)
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python3 found: $PYTHON_VERSION"
        return 0
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version)
        print_success "Python found: $PYTHON_VERSION"
        return 0
    else
        print_error "Python not available for local server"
        return 1
    fi
}

# Launch local server based on available tools
launch_server() {
    local port=8080
    local host="localhost"
    
    print_status "Starting Aura Dashboard on http://$host:$port"
    print_status "Press Ctrl+C to stop the server"
    echo ""
    
    # Try different server methods in order of preference
    if command -v npx &> /dev/null; then
        print_status "Using npx http-server..."
        npx http-server -p $port -a $host -o
    elif check_nodejs; then
        print_status "Using Node.js http-server..."
        npx http-server -p $port -a $host -o
    elif check_python; then
        if command -v python3 &> /dev/null; then
            print_status "Using Python3 HTTP server..."
            python3 -m http.server $port --bind $host
        else
            print_status "Using Python HTTP server..."
            python -m SimpleHTTPServer $port
        fi
    else
        print_error "No server tool found. Please install:"
        echo "  - Node.js (recommended): https://nodejs.org"
        echo "  - Python: https://python.org"
        echo ""
        print_warning "You can also open index.html directly in your browser"
        exit 1
    fi
}

# Quick system check
system_check() {
    print_status "Running system diagnostics..."
    
    # Check OS
    case "$(uname -s)" in
        Darwin*)    OS="macOS" ;;
        Linux*)     OS="Linux" ;;
        CYGWIN*)    OS="Windows" ;;
        MINGW*)     OS="Windows" ;;
        *)          OS="Unknown" ;;
    esac
    print_status "Operating System: $OS"
    
    # Check browser availability
    if command -v open &> /dev/null; then
        print_success "System browser available"
    elif command -v xdg-open &> /dev/null; then
        print_success "System browser available"
    else
        print_warning "Auto-browser launch might not work"
    fi
}

# Phase 2 preparation check
phase2_precheck() {
    echo ""
    print_status "Phase 2 Preparation Check..."
    
    if check_nodejs; then
        # Check for required packages
        if [ -f "package.json" ]; then
            print_success "Node.js project structure ready"
        else
            print_warning "Run 'npm init -y' to prepare for Phase 2"
        fi
    fi
    
    # Check for main HTML file
    if [ -f "index.html" ]; then
        print_success "Dashboard HTML file found"
    else
        print_error "index.html not found in current directory"
        print_status "Please run this script from your project folder"
        exit 1
    fi
}

# Main execution
main() {
    echo ""
    print_status "Initializing Aura Analytics Dashboard..."
    
    # Run checks
    system_check
    phase2_precheck
    
    echo ""
    print_status "Launching dashboard..."
    echo "-------------------------------------------"
    
    # Launch the server
    launch_server
}

# Handle script interruption
cleanup() {
    echo ""
    print_status "Shutting down Aura Dashboard..."
    echo "Thank you for using Aura Analytics!"
    exit 0
}

# Set up trap for Ctrl+C
trap cleanup INT

# Run main function
main
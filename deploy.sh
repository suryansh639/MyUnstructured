#!/bin/bash

# Streamlit Document Processing App - Automated Deployment Script
# Run with: chmod +x deploy.sh && ./deploy.sh

set -e  # Exit on any error

echo "🚀 Starting Streamlit Document Processing App Deployment"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="$PWD"
VENV_NAME="streamlit_env"
APP_NAME="streamlit-doc-processor"
PORT=8501

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    libreoffice \
    pandoc \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    antiword \
    unrtf \
    curl \
    git

print_success "System dependencies installed"

# Create virtual environment
print_status "Creating Python virtual environment..."
if [ ! -d "$VENV_NAME" ]; then
    python3 -m venv $VENV_NAME
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source $VENV_NAME/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Check if unstructured repo exists and install
print_status "Checking for Unstructured repository..."
if [ -d "../unstructured" ]; then
    print_status "Installing Unstructured in development mode..."
    cd ../unstructured
    pip install -e .
    cd "$APP_DIR"
    print_success "Unstructured installed from local repository"
elif [ -d "./unstructured" ]; then
    print_status "Installing Unstructured in development mode..."
    cd ./unstructured
    pip install -e .
    cd "$APP_DIR"
    print_success "Unstructured installed from local repository"
else
    print_warning "Local unstructured repository not found, using pip version"
fi

# Create Streamlit config directory
print_status "Creating Streamlit configuration..."
mkdir -p .streamlit

# Create config.toml
cat > .streamlit/config.toml << EOF
[server]
port = $PORT
address = "0.0.0.0"
maxUploadSize = 200
maxMessageSize = 200

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
EOF

print_success "Streamlit configuration created"

# Create systemd service file
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/${APP_NAME}.service > /dev/null << EOF
[Unit]
Description=Streamlit Document Processing App
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/$VENV_NAME/bin"
ExecStart=$APP_DIR/$VENV_NAME/bin/streamlit run app.py --server.port $PORT --server.address 0.0.0.0
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable ${APP_NAME}.service
print_success "Systemd service created and enabled"

# Create simple startup script
print_status "Creating startup script..."
cat > start_app.sh << 'EOF'
#!/bin/bash
source streamlit_env/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
EOF

chmod +x start_app.sh
print_success "Startup script created"

# Configure firewall
print_status "Configuring firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow ssh
    sudo ufw allow $PORT
    print_success "Firewall configured"
else
    print_warning "UFW not found, please configure firewall manually"
fi

# Create nginx configuration (optional)
read -p "Do you want to set up Nginx reverse proxy? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Installing and configuring Nginx..."
    sudo apt install -y nginx
    
    read -p "Enter your domain name (or press Enter for localhost): " DOMAIN_NAME
    if [ -z "$DOMAIN_NAME" ]; then
        DOMAIN_NAME="localhost"
    fi
    
    sudo tee /etc/nginx/sites-available/${APP_NAME} > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        client_max_body_size 200M;
    }
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx
    sudo ufw allow 80
    print_success "Nginx configured successfully"
fi

# Test the application
print_status "Testing the application..."
if [ -f "app.py" ]; then
    print_success "Application file found"
    
    # Start the service
    sudo systemctl start ${APP_NAME}.service
    sleep 5
    
    # Check if service is running
    if sudo systemctl is-active --quiet ${APP_NAME}.service; then
        print_success "Service is running successfully"
    else
        print_error "Service failed to start. Check logs with: sudo journalctl -u ${APP_NAME}.service -f"
    fi
else
    print_error "app.py not found! Please ensure the main application file exists."
fi

# Create management script
print_status "Creating management script..."
cat > manage_app.sh << EOF
#!/bin/bash
# Management script for Streamlit Document Processing App

case \$1 in
    start)
        sudo systemctl start ${APP_NAME}.service
        echo "App started"
        ;;
    stop)
        sudo systemctl stop ${APP_NAME}.service
        echo "App stopped"
        ;;
    restart)
        sudo systemctl restart ${APP_NAME}.service
        echo "App restarted"
        ;;
    status)
        sudo systemctl status ${APP_NAME}.service
        ;;
    logs)
        sudo journalctl -u ${APP_NAME}.service -f
        ;;
    enable)
        sudo systemctl enable ${APP_NAME}.service
        echo "App enabled for auto-start"
        ;;
    disable)
        sudo systemctl disable ${APP_NAME}.service
        echo "App disabled from auto-start"
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|status|logs|enable|disable}"
        exit 1
        ;;
esac
EOF

chmod +x manage_app.sh
print_success "Management script created"

# Create update script
print_status "Creating update script..."
cat > update_app.sh << EOF
#!/bin/bash
# Update script for Streamlit Document Processing App

echo "Stopping service..."
sudo systemctl stop ${APP_NAME}.service

echo "Activating virtual environment..."
source $VENV_NAME/bin/activate

echo "Updating dependencies..."
pip install --upgrade -r requirements.txt

echo "Starting service..."
sudo systemctl start ${APP_NAME}.service

echo "Update completed!"
EOF

chmod +x update_app.sh
print_success "Update script created"

# Final instructions
echo
echo "================================================="
print_success "🎉 Deployment completed successfully!"
echo "================================================="
echo
echo "📋 What's been set up:"
echo "   ✅ Virtual environment: $VENV_NAME"
echo "   ✅ Python dependencies installed"
echo "   ✅ Streamlit configuration created"
echo "   ✅ Systemd service: ${APP_NAME}.service"
echo "   ✅ Firewall configured (port $PORT)"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   ✅ Nginx reverse proxy configured"
fi
echo
echo "🚀 Quick start commands:"
echo "   Start app:    ./manage_app.sh start"
echo "   Stop app:     ./manage_app.sh stop"
echo "   View logs:    ./manage_app.sh logs"
echo "   Check status: ./manage_app.sh status"
echo
echo "🌐 Access your app:"
if [[ $REPLY =~ ^[Yy]$ ]] && [ "$DOMAIN_NAME" != "localhost" ]; then
    echo "   URL: http://$DOMAIN_NAME"
else
    echo "   URL: http://$(curl -s ifconfig.me):$PORT"
    echo "   Local: http://localhost:$PORT"
fi
echo
echo "📁 Important files:"
echo "   App file: $APP_DIR/app.py"
echo "   Config: $APP_DIR/.streamlit/config.toml"
echo "   Service: /etc/systemd/system/${APP_NAME}.service"
echo "   Logs: sudo journalctl -u ${APP_NAME}.service -f"
echo
echo "🔧 Next steps:"
echo "   1. Verify the app is running: ./manage_app.sh status"
echo "   2. Check the logs if needed: ./manage_app.sh logs"
echo "   3. Update EC2 security group to allow port $PORT"
echo "   4. Test document upload and processing"
echo
print_warning "Remember to:"
echo "   • Configure your EC2 security group to allow inbound traffic on port $PORT"
echo "   • Test the application with various document types"
echo "   • Monitor system resources during heavy usage"
echo "   • Set up regular backups if storing processed data"
echo
print_success "Happy document processing! 📄✨"

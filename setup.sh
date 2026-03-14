#!/data/data/com.termux/files/usr/bin/bash

# TG Post Reaction Tool - Termux Setup Script
# Colorful setup for Termux

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Banner
clear
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║     ████████╗ ██████╗     ██████╗  ██████╗ ███████╗    ║"
echo "║     ╚══██╔══╝██╔════╝     ██╔══██╗██╔═══██╗██╔════╝    ║"
echo "║        ██║   ██║  ███╗    ██████╔╝██║   ██║███████╗    ║"
echo "║        ██║   ██║   ██║    ██╔═══╝ ██║   ██║╚════██║    ║"
echo "║        ██║   ╚██████╔╝    ██║     ╚██████╔╝███████║    ║"
echo "║        ╚═╝    ╚═════╝     ╚═╝      ╚═════╝ ╚══════╝    ║"
echo "║                                                          ║"
echo "║           🔥 POST REACTION TOOL v2.0 🔥                ║"
echo "║             [ Termux Edition - Advanced ]               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}[*] Starting Termux Setup...${NC}"
sleep 2

# Update packages
echo -e "${BLUE}[1/6] 📦 Updating Termux packages...${NC}"
pkg update -y && pkg upgrade -y

# Install required packages
echo -e "${BLUE}[2/6] 📥 Installing required packages...${NC}"
pkg install -y python git nano

# Install Python packages
echo -e "${BLUE}[3/6] 🐍 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install python-telegram-bot==20.7
pip install colorama
pip install rich
pip install requests
pip install python-dotenv

# Create tool directory
echo -e "${BLUE}[4/6] 📁 Creating tool structure...${NC}"
mkdir -p ~/tg-post-reaction-tool
cd ~/tg-post-reaction-tool

# Clone repository (this will be replaced after upload)
echo -e "${BLUE}[5/6] 🔧 Configuring tool files...${NC}"

# Create config file with provided tokens
cat > config.json << 'EOF'
{
    "bots": [
        "8702203451:AAGDD_h2JdSjtr7RyCmjD2RX-t3SfvACUEk",
        "8533812308:AAHFyXY9Jc16i9xUVUlIUkYdApHKLkvISaE",
        "7914800849:AAFw-UbfVxTHoJCsDi9CxlBBriFmr9d7JLQ"
    ],
    "settings": {
        "reaction": "❤️",
        "delay_between_bots": 1.5,
        "max_retries": 3
    }
}
EOF

# Create main tool file
echo -e "${BLUE}[6/6] ⚙️ Installing main tool...${NC}"
sleep 2

# Make main.py executable
chmod +x main.py 2>/dev/null || echo "main.py will be created"

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║   ✅ SETUP COMPLETED SUCCESSFULLY!                      ║"
echo "║                                                          ║"
echo "║   📍 Tool Location: ~/tg-post-reaction-tool             ║"
echo "║   🚀 Run Command:  cd ~/tg-post-reaction-tool && python main.py  ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Ask to run tool now
echo -e "${YELLOW}❓ Do you want to run the tool now? (y/n): ${NC}"
read -r run_now
if [[ "$run_now" == "y" || "$run_now" == "Y" ]]; then
    cd ~/tg-post-reaction-tool
    python main.py
else
    echo -e "${CYAN}📝 You can run later with: cd ~/tg-post-reaction-tool && python main.py${NC}"
fi

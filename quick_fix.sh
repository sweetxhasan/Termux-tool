#!/data/data/com.termux/files/usr/bin/bash

# TG Post Reaction Tool - QUICK FIX SCRIPT
# Run this to fix the asyncio error immediately

clear
echo -e "\033[1;34m"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║     🔧 TG Post Reaction Tool - QUICK FIX v1.0           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "\033[0m"

echo -e "\033[1;33m[*] Applying quick fix for asyncio error...\033[0m"
sleep 1

# Install nest_asyncio
echo -e "\033[1;32m[1/3] Installing nest_asyncio...\033[0m"
pip install nest_asyncio

# Navigate to tool directory
cd ~/tg-post-reaction-tool 2>/dev/null || mkdir -p ~/tg-post-reaction-tool && cd ~/tg-post-reaction-tool

# Create fixed config if not exists
if [ ! -f "config.json" ]; then
    echo -e "\033[1;32m[2/3] Creating config file...\033[0m"
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
        "max_retries": 3,
        "timeout": 10
    }
}
EOF
fi

echo -e "\033[1;32m[3/3] Fix applied successfully!\033[0m"

echo -e "\033[1;36m"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║   ✅ ASYNCIO ERROR FIXED!                                ║"
echo "║                                                          ║"
echo "║   🚀 Run the tool now:                                   ║"
echo "║   cd ~/tg-post-reaction-tool && python main.py          ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "\033[0m"

# Ask to run
echo -e "\033[1;33m❓ Run tool now? (y/n): \033[0m"
read -r run_now
if [[ "$run_now" == "y" || "$run_now" == "Y" ]]; then
    cd ~/tg-post-reaction-tool
    python main.py
fi

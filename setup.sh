#!/bin/bash
# Setup script for FirstCry Hot Wheels Monitor

set -e

echo "🏎️  FirstCry Hot Wheels Monitor - Setup Script"
echo "================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt
echo "✅ Dependencies installed"
echo

# Check for environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "⚠️  Environment variables not set!"
    echo
    echo "Please set the following environment variables:"
    echo "  export TELEGRAM_BOT_TOKEN='your_bot_token_here'"
    echo "  export TELEGRAM_CHAT_ID='your_chat_id_here'"
    echo
    echo "To get these values:"
    echo "  1. Create bot: https://t.me/botfather"
    echo "  2. Get chat ID: Send message to your bot, then visit:"
    echo "     https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates"
    echo
    read -p "Do you want to enter them now? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter TELEGRAM_BOT_TOKEN: " TELEGRAM_BOT_TOKEN
        read -p "Enter TELEGRAM_CHAT_ID: " TELEGRAM_CHAT_ID
        
        export TELEGRAM_BOT_TOKEN
        export TELEGRAM_CHAT_ID
        
        echo
        echo "✅ Variables set for this session"
        echo "⚠️  Add these to your ~/.bashrc or ~/.zshrc to make them permanent:"
        echo "  export TELEGRAM_BOT_TOKEN='$TELEGRAM_BOT_TOKEN'"
        echo "  export TELEGRAM_CHAT_ID='$TELEGRAM_CHAT_ID'"
        echo
    else
        echo
        echo "⏭️  Skipping test run. Set variables and run:"
        echo "  python3 hotwheels_monitor.py --once"
        exit 0
    fi
fi

echo "✅ Environment variables configured"
echo

# Run test scan
echo "🔍 Running test scan..."
echo "   (This will check for products but won't spam you with existing items)"
echo

python3 hotwheels_monitor.py --once

echo
echo "✅ Setup complete!"
echo
echo "Next steps:"
echo "  1. Check Telegram for test notification (if any new products found)"
echo "  2. To run continuously: python3 hotwheels_monitor.py"
echo "  3. To deploy to GitHub Actions:"
echo "     - Fork this repository"
echo "     - Add secrets: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
echo "     - Enable Actions in your fork"
echo
echo "📊 Database created: hotwheels_products.db"
echo "   View products: sqlite3 hotwheels_products.db 'SELECT * FROM products;'"
echo

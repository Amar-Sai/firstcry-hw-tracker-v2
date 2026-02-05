# 🏎️ FirstCry Hot Wheels Real-Time Alert System

Get **instant Telegram notifications** when new Hot Wheels products become available on FirstCry - before they sell out!

## 🎯 What This Solves

- ✅ **Multi-layered discovery** - Scans brand pages, search results, and category listings
- ✅ **No spam** - Smart state tracking prevents repeat notifications
- ✅ **Catches restocks** - Notifies when sold-out products return
- ✅ **Fast detection** - Runs every 2 minutes during peak hours
- ✅ **Zero maintenance** - Fully automated via GitHub Actions

## 🚀 Quick Start

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. Save your **Bot Token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your Chat ID

1. Send a message to your new bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find your **Chat ID** in the response (a number like `123456789`)

### 3. Fork This Repository

Click the **Fork** button at the top of this page.

### 4. Configure Secrets

In your forked repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add two secrets:
   - Name: `TELEGRAM_BOT_TOKEN`, Value: Your bot token
   - Name: `TELEGRAM_CHAT_ID`, Value: Your chat ID

### 5. Enable GitHub Actions

1. Go to the **Actions** tab
2. Click "I understand my workflows, go ahead and enable them"

### 6. Manual First Run

1. Go to **Actions** tab
2. Click on "Hot Wheels Monitor" workflow
3. Click "Run workflow" → "Run workflow"

**That's it!** You'll now get notifications every time a new Hot Wheels product appears or restocks.

## 📱 Notification Examples

```
🆕 NEW PRODUCT ALERT

🏎️ Hot Wheels Premium McLaren F1 GTR - Red
💰 Price: ₹549
🛒 Buy Now: https://www.firstcry.com/...
⏰ Detected: 2026-02-05 14:23:45
```

```
🔄 RESTOCK ALERT

🏎️ Hot Wheels 5-Car Gift Pack
💰 Price: ₹899
🛒 Buy Now: https://www.firstcry.com/...
⏰ Detected: 2026-02-05 15:10:12
```

## ⚙️ How It Works

### 1. Multi-Layered Discovery
The system scans **3 different surfaces** to catch all products:
- Hot Wheels brand listing page
- FirstCry search results for "Hot Wheels"
- Toy Cars category filtered by Hot Wheels

### 2. Validation Gate
Every product URL discovered is validated:
- ✅ Confirms it's actually Hot Wheels brand
- ✅ Checks current buyability (Add to Cart available)
- ✅ Extracts price and product details

### 3. State Machine Tracking
Products move through states:
- `NEW` → First time seeing this product
- `BUYABLE` → Can add to cart right now
- `OUT_OF_STOCK` → Product exists but can't purchase
- `HIDDEN` → No longer visible anywhere

### 4. Smart Notifications
Notifications are sent **ONLY** when:
- `NEW → BUYABLE` (brand new product launch)
- `OUT_OF_STOCK → BUYABLE` (restock alert)
- `HIDDEN → BUYABLE` (product returns)

**Never** notifies for:
- Products that stay in stock
- Products going out of stock
- Page reshuffles or re-orderings

## 🕐 Schedule

The monitor runs automatically:
- **Every 2 minutes** from 9 AM - 11 PM IST (peak shopping hours)
- Can be triggered **manually** anytime from Actions tab

## 🔧 Local Testing

Want to test locally before deploying?

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/firstcry-hotwheels-alert.git
cd firstcry-hotwheels-alert

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"

# Run one scan
python hotwheels_monitor.py --once

# Or run continuously (scans every 2 minutes)
python hotwheels_monitor.py
```

## 📊 Database

Product states are tracked in `hotwheels_products.db` (SQLite):
- Automatically backed up to repository after each run
- Tracks entire product lifecycle
- Logs all state transitions

To inspect the database:
```bash
sqlite3 hotwheels_products.db
.tables
SELECT * FROM products LIMIT 10;
```

## 🎯 Success Criteria

You'll know it's working when:
- ✅ You receive a test notification within 2 minutes of first run
- ✅ New products trigger alerts before stock depletes
- ✅ Restocks are caught immediately
- ✅ No spam from products already in stock

## 🐛 Troubleshooting

### Not receiving notifications?

1. **Check bot token**: Send `/getMe` to @BotFather
2. **Verify chat ID**: Make sure you've sent at least one message to your bot
3. **Check Actions**: Go to Actions tab and verify the workflow is running
4. **Review logs**: Click on a completed workflow run to see execution logs

### Workflow not running?

1. **Fork is updated**: Make sure you've forked the latest version
2. **Actions enabled**: Check the Actions tab is enabled
3. **Secrets set**: Verify both secrets exist in Settings → Secrets

### Getting too many notifications?

Check the database - products might be flipping between states. This can happen if:
- Site is updating stock frequently
- Bot detection is interfering

To reduce frequency, edit `.github/workflows/monitor.yml` and change:
```yaml
- cron: '*/5 3-17 * * *'  # Every 5 minutes instead of 2
```

## 📈 Monitoring Multiple Categories

Want to monitor other brands or categories? Fork the code and modify:

```python
DISCOVERY_SURFACES = {
    "brand_listing": "/mattel/0/0/456",  # Change brand ID
    "search_results": "/search?searchstring=matchbox",  # Change search term
    ...
}
```

## ⚡ Pro Tips

1. **First run = baseline**: First run won't notify for existing products
2. **Restocks work**: System remembers products that went out of stock
3. **Manual trigger**: Use workflow dispatch for immediate scan
4. **Check Actions regularly**: Monitor for any errors
5. **Database persists**: Product history is maintained across runs

## 🔒 Privacy & Security

- Bot token and chat ID are stored as **encrypted GitHub Secrets**
- Database only stores product IDs, names, and states
- No personal information collected
- Code is fully open source and auditable

## 📝 License

MIT License - Feel free to modify and use as needed.

## 🙏 Contributing

Found a bug? Have an improvement? 
1. Fork the repo
2. Make your changes
3. Submit a pull request

## 💬 Support

Issues? Questions? Open an issue in this repository!

---

**Happy collecting! 🏁**

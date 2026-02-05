# 🚀 Deployment Guide - FirstCry Hot Wheels Monitor

This guide will help you get alerts for new Hot Wheels products in **under 10 minutes**.

## 📋 Prerequisites

- A Telegram account
- A GitHub account (free)
- 10 minutes of your time

## 🎯 Deployment Options

### Option 1: GitHub Actions (Recommended - 100% Free & Automated)

**Pros:**
- ✅ Completely free
- ✅ Runs 24/7 without your computer
- ✅ Zero maintenance
- ✅ Scans every 2 minutes during peak hours

**Cons:**
- ⚠️ Slightly more initial setup
- ⚠️ 2-minute minimum interval (GitHub Actions limit)

### Option 2: Local Deployment (For Advanced Users)

**Pros:**
- ✅ Full control over scan frequency
- ✅ Can modify code easily
- ✅ Immediate testing

**Cons:**
- ⚠️ Requires your computer to run 24/7
- ⚠️ Manual updates needed

---

## 🤖 Step-by-Step: GitHub Actions Deployment

### Step 1: Create Telegram Bot (5 minutes)

1. Open Telegram and search for **@BotFather**
2. Send: `/newbot`
3. Choose a name: `My Hot Wheels Alert Bot`
4. Choose a username: `YourNameHotWheelsBot` (must end in 'bot')
5. **Save the token** BotFather gives you (looks like: `123456789:ABCdefGHI...`)

### Step 2: Get Your Chat ID (2 minutes)

1. **Start a chat** with your new bot (click the link BotFather sent)
2. Send any message to your bot (e.g., "hello")
3. Open this URL in browser (replace `<TOKEN>` with your token):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
4. Look for `"chat":{"id":12345678` - **save this number** (your chat ID)

**Example response:**
```json
{
  "result": [{
    "message": {
      "chat": {
        "id": 123456789,  ← This is your CHAT_ID
        "first_name": "Your Name"
      }
    }
  }]
}
```

### Step 3: Fork the Repository (1 minute)

1. Go to: https://github.com/Amar-Sai/firstcry-hotwheels-alert
2. Click the **Fork** button (top right)
3. Click **Create fork**

### Step 4: Add Secrets to Your Fork (2 minutes)

1. In **your forked repository**, go to **Settings**
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**

**Add Secret #1:**
- Name: `TELEGRAM_BOT_TOKEN`
- Value: (paste your bot token from Step 1)
- Click **Add secret**

**Add Secret #2:**
- Name: `TELEGRAM_CHAT_ID`  
- Value: (paste your chat ID from Step 2)
- Click **Add secret**

### Step 5: Enable GitHub Actions (1 minute)

1. Go to **Actions** tab in your fork
2. Click **"I understand my workflows, go ahead and enable them"**
3. You should see "Hot Wheels Monitor" workflow

### Step 6: Test It! (1 minute)

1. Still in **Actions** tab, click on **"Hot Wheels Monitor"**
2. Click **"Run workflow"** dropdown → **"Run workflow"** button
3. Wait 30-60 seconds
4. Click on the running workflow to see live logs
5. **Check Telegram** - you might receive notifications if new products are found!

### ✅ Done! Your monitor is now running automatically every 2 minutes (9 AM - 11 PM IST)

---

## 💻 Step-by-Step: Local Deployment

### Step 1: Install Python (if not already installed)

**Windows:**
- Download from https://www.python.org/downloads/
- Check "Add Python to PATH" during installation

**Mac:**
```bash
brew install python3
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

### Step 2: Clone Repository

```bash
git clone https://github.com/Amar-Sai/firstcry-hotwheels-alert.git
cd firstcry-hotwheels-alert
```

### Step 3: Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

The script will:
- Install dependencies
- Prompt for Telegram credentials
- Run a test scan
- Create the database

### Step 4: Run Continuously

```bash
python3 hotwheels_monitor.py
```

This will scan every 2 minutes until you stop it (Ctrl+C).

**To run in background:**

```bash
# Linux/Mac
nohup python3 hotwheels_monitor.py > monitor.log 2>&1 &

# Windows (use Task Scheduler or run in separate terminal)
pythonw hotwheels_monitor.py
```

---

## 🔍 Verification Checklist

After deployment, verify everything works:

### ✅ Check #1: GitHub Actions Running

1. Go to **Actions** tab
2. See recent workflow runs (green checkmarks)
3. Click on latest run → see logs without errors

### ✅ Check #2: Database Created

GitHub Actions should commit `hotwheels_products.db` to your repo.

**Local:** Check file exists:
```bash
ls -lh hotwheels_products.db
```

### ✅ Check #3: Telegram Working

Within first 2-3 runs, you should get at least one notification (unless absolutely nothing changed).

If no notification after 30 minutes:
1. Check workflow logs for errors
2. Verify secrets are set correctly
3. Test bot with: `https://api.telegram.org/bot<TOKEN>/getMe`

---

## 🎯 Expected Behavior

### First Run
- Discovers all current Hot Wheels products
- **No notifications** (they're already in stock - not "new")
- Creates baseline in database

### Subsequent Runs
- Checks for new products
- Checks for restocks
- **Notifies only on state changes:**
  - NEW → BUYABLE ✅
  - OUT_OF_STOCK → BUYABLE ✅
  - BUYABLE → BUYABLE ❌ (no spam)

### Notification Timeline
```
Run 1 (14:00): Discovers 150 products → No alerts
Run 2 (14:02): Same 150 products → No alerts
Run 3 (14:04): 151 products (1 new!) → 🔔 ALERT
Run 4 (14:06): Same 151 products → No alerts
Run 5 (14:08): 150 products (1 sold out) → No alert
Run 6 (14:10): 151 products (restocked!) → 🔔 RESTOCK ALERT
```

---

## 🐛 Troubleshooting

### "No notifications received"

**Check 1:** Did you complete first baseline run?
- First run creates baseline, no alerts

**Check 2:** Are there actually new products?
- Hot Wheels releases are infrequent
- Check FirstCry manually to see if new items exist

**Check 3:** Bot credentials correct?
```bash
# Test bot
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# Should return bot info, not error
```

**Check 4:** Check workflow logs
- GitHub Actions → Latest run → View logs
- Look for errors in red

### "Workflow not running"

**Check 1:** Actions enabled?
- Actions tab → Enable workflows

**Check 2:** Schedule correct?
- Runs 9 AM - 11 PM IST
- Currently 3:30 AM - 5:30 PM UTC
- Check current time: https://time.is/IST

**Check 3:** Manually trigger
- Actions → Hot Wheels Monitor → Run workflow

### "Getting duplicate notifications"

This shouldn't happen with state machine, but if it does:

**Check database:**
```bash
sqlite3 hotwheels_products.db "SELECT * FROM state_transitions WHERE notified=1 ORDER BY timestamp DESC LIMIT 10;"
```

If same product ID appears multiple times, check:
- Product page structure changed?
- Bot detection interfering?

**Solution:** Increase scan interval:
Edit `.github/workflows/monitor.yml`:
```yaml
- cron: '*/5 3-17 * * *'  # Every 5 minutes
```

### "Database errors"

**Local deployment:**
```bash
rm hotwheels_products.db
python3 hotwheels_monitor.py --once
```

**GitHub Actions:**
- Go to Actions → Clear cache
- Manually delete `hotwheels_products.db` from repo
- Next run will recreate

---

## 📊 Monitoring & Maintenance

### View Product Database

```bash
sqlite3 hotwheels_products.db

# List all products
SELECT product_id, name, state, price FROM products;

# See recent transitions
SELECT * FROM state_transitions ORDER BY timestamp DESC LIMIT 20;

# Count products by state
SELECT state, COUNT(*) FROM products GROUP BY state;
```

### Check Workflow Health

Visit your fork's Actions tab weekly:
- Green checkmarks = healthy
- Red X = needs attention (click for details)

### Update the Code

If I push updates to main repo:

```bash
# Add upstream remote (one time)
git remote add upstream https://github.com/Amar-Sai/firstcry-hotwheels-alert.git

# Update your fork
git fetch upstream
git merge upstream/main
git push origin main
```

---

## ⚙️ Customization

### Change Scan Frequency

Edit `.github/workflows/monitor.yml`:
```yaml
schedule:
  - cron: '*/5 3-17 * * *'  # Every 5 minutes
  - cron: '0 3-17 * * *'     # Every hour
  - cron: '0 */2 3-17 * * *' # Every 2 hours
```

### Monitor Different Products

Edit `hotwheels_monitor.py`:

```python
# Change brand
DISCOVERY_SURFACES = {
    "brand_listing": "/matchbox/0/0/456",  # Different brand ID
    ...
}

# Change search term
def _verify_brand(self, soup: BeautifulSoup, name: str) -> bool:
    return 'matchbox' in name.lower()  # Different brand
```

### Custom Notification Format

Edit the `send_notification` method:

```python
message = f"""
🎯 NEW ARRIVAL!
Name: {product.name}
Price: ₹{product.price}
Link: {product.url}
"""
```

---

## 📈 Advanced Tips

### 1. Monitor Multiple Brands

Clone script for each brand:
```bash
cp hotwheels_monitor.py matchbox_monitor.py
```

Modify `DISCOVERY_SURFACES` and brand verification in each.

### 2. Price Tracking

Modify to track price changes:
```python
if old_product and old_product.price != product.price:
    # Send price drop notification
```

### 3. WhatsApp Instead of Telegram

Use Twilio/WhatsApp Business API:
```python
from twilio.rest import Client
# Replace TelegramNotifier with WhatsAppNotifier
```

### 4. Discord Notifications

Replace Telegram with Discord webhook:
```python
import discord_webhook
webhook = discord_webhook.DiscordWebhook(url="YOUR_WEBHOOK")
```

---

## 🎓 Understanding the System

### Architecture
```
┌─────────────────────────────────────────┐
│         GitHub Actions (Scheduler)       │
│  Runs every 2 minutes (9 AM - 11 PM IST) │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Multi-Layered Discovery             │
│  ┌─────────────────────────────────┐    │
│  │ Surface 1: Brand Listing         │    │
│  │ Surface 2: Search Results        │    │
│  │ Surface 3: Category Filtered     │    │
│  └─────────────────────────────────┘    │
│           Collects candidate URLs        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        Validation Gate                   │
│  For each candidate URL:                 │
│  ✓ Verify Hot Wheels brand              │
│  ✓ Check buyability signals              │
│  ✓ Extract price & details               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│       State Machine Processor            │
│  Compare with database:                  │
│  • NEW → BUYABLE? → NOTIFY               │
│  • OUT_OF_STOCK → BUYABLE? → NOTIFY      │
│  • BUYABLE → BUYABLE? → Silent           │
│  Update database with new state          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Telegram Notification               │
│  Send alert to your phone 📱             │
└─────────────────────────────────────────┘
```

### State Machine
```
    NEW
     │
     ├──► BUYABLE ──────► Notification! 🔔
     │       │
     │       ▼
     │  OUT_OF_STOCK
     │       │
     │       ▼
     └──► BUYABLE ──────► Restock Alert! 🔔
             │
             ▼
          HIDDEN
             │
             ▼
          BUYABLE ──────► Return Alert! 🔔
```

---

## ✅ Success Metrics

You'll know it's working when:

1. ✅ First run completes without errors
2. ✅ Database file created with products
3. ✅ Workflows run every 2 minutes (Actions tab)
4. ✅ Within 24 hours, you see at least one transition logged
5. ✅ When FirstCry adds a new product, you get notified within 2 minutes

---

## 🆘 Getting Help

If stuck:

1. **Check this guide's troubleshooting section** ↑
2. **Review workflow logs** (Actions tab → Latest run)
3. **Test bot manually:**
   ```bash
   python3 -c "import requests; print(requests.get('https://api.telegram.org/bot<TOKEN>/getMe').json())"
   ```
4. **Open an issue** on GitHub with:
   - What you tried
   - Error messages
   - Workflow log screenshot

---

**You're all set! Happy hunting! 🏎️🏁**

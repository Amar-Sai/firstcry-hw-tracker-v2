# ⚡ QUICK START - Get Alerts in 5 Minutes

## What You Need
- [ ] Telegram account
- [ ] GitHub account  
- [ ] 5 minutes

## Steps

### 1️⃣ Create Telegram Bot (2 min)
1. Open Telegram → Search `@BotFather`
2. Send: `/newbot`
3. Name it: `Hot Wheels Alert`
4. Username: `YourNameHotWheelsBot`
5. **Copy the token** (looks like: `1234567:ABC...`)

### 2️⃣ Get Chat ID (1 min)
1. Send message to your bot
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find the `"id"` number (like `123456789`)
4. **Save this number**

### 3️⃣ Update Your GitHub Repo (2 min)

**Upload these files to your GitHub repository:**

```
firstcry-hotwheels-alert/
├── hotwheels_monitor.py
├── requirements.txt
├── .github/
│   └── workflows/
│       └── monitor.yml
├── .gitignore
├── README.md
└── DEPLOYMENT_GUIDE.md
```

**Then add secrets:**
1. Go to repo Settings → Secrets and variables → Actions
2. Add `TELEGRAM_BOT_TOKEN` = your token from step 1
3. Add `TELEGRAM_CHAT_ID` = your ID from step 2

### 4️⃣ Enable & Test (30 sec)
1. Actions tab → Enable workflows
2. Click "Hot Wheels Monitor" → Run workflow
3. **Check Telegram in 1 minute!**

## ✅ Done!
You'll now get instant alerts when:
- 🆕 New Hot Wheels products launch
- 🔄 Sold-out products restock

## What Happens Next?
- Runs automatically every 2 minutes (9 AM - 11 PM IST)
- No spam - only notifies on NEW or RESTOCKED items
- Completely free - runs on GitHub's servers

## Not Working?
See DEPLOYMENT_GUIDE.md for detailed troubleshooting.

---

**Pro tip:** Run manually from Actions tab to test anytime!

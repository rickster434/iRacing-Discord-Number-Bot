# 🚀 Complete Setup Guide for Beginners

This guide will walk you through every step of setting up the iRacing Discord Number Bot, even if you've never set up a bot before.

## 📋 What You'll Need

- [ ] A Discord account
- [ ] Administrator access to your Discord server
- [ ] iRacing account with an active league
- [ ] About 15-30 minutes

## Part 1: Create Your Discord Bot (10 minutes)

### Step 1: Go to Discord Developer Portal

1. Open your web browser
2. Go to: https://discord.com/developers/applications
3. Log in with your Discord account

### Step 2: Create a New Application

1. Click the blue **"New Application"** button (top right)
2. Enter a name for your bot (example: "iRacing Number Bot")
3. Click **"Create"**

### Step 3: Set Up the Bot

1. In the left sidebar, click **"Bot"**
2. Click **"Add Bot"**
3. Click **"Yes, do it!"** to confirm

### Step 4: Get Your Bot Token

⚠️ **IMPORTANT**: Never share your bot token with anyone!

1. Under "Token", click **"Reset Token"**
2. Click **"Yes, do it!"**
3. Click **"Copy"** to copy your token
4. Paste it somewhere safe temporarily (like Notepad)

### Step 5: Enable Intents

Scroll down to "Privileged Gateway Intents" and enable:

- ✅ **Presence Intent** (optional)
- ✅ **Server Members Intent** (required)
- ✅ **Message Content Intent** (required)

Click **"Save Changes"**

### Step 6: Create Invite Link

1. In the left sidebar, click **"OAuth2"**
2. Click **"URL Generator"**
3. Under "Scopes", check:
   - ✅ `bot`
   - ✅ `applications.commands`
4. Under "Bot Permissions", check:
   - ✅ Read Messages/View Channels
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Use Slash Commands
5. Scroll down and click **"Copy"** next to the generated URL

### Step 7: Invite Bot to Your Server

1. Paste the copied URL into your browser
2. Select your Discord server from the dropdown
3. Click **"Authorize"**
4. Complete the captcha if prompted

Your bot should now appear in your Discord server (offline for now).

## Part 2: Install the Bot on Your Computer (10 minutes)

### Step 1: Install Python

1. Go to: https://www.python.org/downloads/
2. Download Python 3.10 or newer
3. Run the installer
4. ⚠️ **IMPORTANT**: Check "Add Python to PATH" before clicking Install
5. Click **"Install Now"**
6. Wait for installation to complete

### Step 2: Verify Python Installation

1. Open Command Prompt (Windows) or Terminal (Mac)
   - Windows: Press `Win + R`, type `cmd`, press Enter
   - Mac: Press `Cmd + Space`, type `terminal`, press Enter
2. Type: `python --version`
3. You should see something like: `Python 3.10.x`

If you see an error, restart your computer and try again.

### Step 3: Navigate to Bot Folder

In Command Prompt/Terminal:

**Windows:**
```bash
cd "C:\Users\The_R\Documents\RM Engineering\iRacing Discord Number Bot"
```

**Mac/Linux:**
```bash
cd "/Users/YourName/Documents/iRacing Discord Number Bot"
```

### Step 4: Install Dependencies

Type this command and press Enter:

```bash
pip install -r requirements.txt
```

Wait for all packages to install (may take 1-2 minutes).

### Step 5: Create Configuration File

1. In the bot folder, find the file named `.env.example`
2. Make a copy and rename it to `.env` (just `.env`, no `.txt` extension)
3. Open `.env` with Notepad or any text editor

### Step 6: Add Your Bot Token

In the `.env` file, replace `your_discord_bot_token_here` with your actual bot token:

```env
DISCORD_BOT_TOKEN=your_actual_token_here
IRACING_USERNAME=your_iracing_email@example.com
IRACING_PASSWORD=your_iracing_password
```

**Example:**
```env
DISCORD_BOT_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.AbCdEf.GhIjKlMnOpQrStUvWxYz
IRACING_USERNAME=john@example.com
IRACING_PASSWORD=MySecurePassword123
```

Save and close the file.

## Part 3: Run the Bot (5 minutes)

### Step 1: Start the Bot

In Command Prompt/Terminal (in the bot folder), type:

```bash
python bot.py
```

You should see:
```
INFO - Database initialized successfully
INFO - Logged in as iRacing Number Bot (ID: ...)
INFO - Connected to 1 server(s)
```

✅ **Your bot is now online!**

### Step 2: Configure in Discord

1. Go to your Discord server
2. Type `/setup` and press Enter
3. Fill in the command:
   - **league_id**: Your iRacing league ID (see below)
   - **min_number**: 0 (or your minimum)
   - **max_number**: 999 (or your maximum)

**Finding your League ID:**
1. Go to your league on iRacing.com
2. Look at the URL: `iracing.com/membersite/member/LeagueView.do?league=12345`
3. The number after `league=` is your ID (example: `12345`)

Example command:
```
/setup league_id:12345 min_number:0 max_number:99
```

### Step 3: Test the Bot

Try these commands:

1. `/help` - See all commands
2. `/available` - See available numbers
3. `/claim 42` - Claim number 42
4. `/roster` - View the roster

If all these work, congratulations! 🎉

## Part 4: Keep the Bot Running

### Option A: Keep Command Prompt Open

- The bot runs as long as the Command Prompt window is open
- Don't close the window!
- To stop: Press `Ctrl + C`

### Option B: Use Free Cloud Hosting

Deploy on Replit (free, runs 24/7):

1. Go to https://replit.com
2. Sign up for free
3. Click "Create Repl"
4. Choose "Import from GitHub" or "Upload files"
5. Upload all bot files
6. Click the "Secrets" icon (lock) in the left sidebar
7. Add secrets:
   - `DISCORD_BOT_TOKEN`: your token
   - `IRACING_USERNAME`: your email
   - `IRACING_PASSWORD`: your password
8. Click "Run"

Your bot will now run 24/7 on Replit's servers!

## 🎯 Next Steps

Now that your bot is running:

1. **Inform your members**: Post in your Discord about the new bot
2. **Set up announcements**: Use `/setup announcement_channel:#channel`
3. **Sync with iRacing**: Use `/sync` to sync your roster
4. **Test thoroughly**: Have a few members test claiming/releasing

## 🆘 Troubleshooting

### "ModuleNotFoundError" when running bot

**Solution**: Run `pip install -r requirements.txt` again

### Bot appears offline in Discord

**Solutions**:
1. Make sure `bot.py` is running (don't close Command Prompt)
2. Check your bot token is correct in `.env`
3. Make sure you saved the `.env` file

### "/setup command not found"

**Solutions**:
1. Wait 5 minutes after inviting the bot
2. Try kicking and re-inviting the bot
3. Make sure you checked `applications.commands` when creating invite link

### "Invalid token" error

**Solutions**:
1. Go back to Discord Developer Portal
2. Reset your bot token
3. Copy the new token to your `.env` file
4. Restart the bot

### Sync fails

**Solutions**:
1. Verify your iRacing email and password in `.env`
2. Make sure your league ID is correct
3. Ensure your league has an active season
4. Check you have an active iRacing subscription

### Bot crashes or stops responding

**Solutions**:
1. Check `bot.log` file for errors
2. Restart the bot (Ctrl+C, then `python bot.py`)
3. Make sure Python 3.10+ is installed

## 📞 Getting Help

If you're still stuck:

1. Check the `bot.log` file for error messages
2. Review the README.md
3. Ask in your Discord's tech support channel
4. Double-check each step in this guide

## ✅ Success Checklist

- [ ] Bot shows as online in Discord
- [ ] `/help` command works
- [ ] `/setup` configured successfully
- [ ] Members can `/claim` numbers
- [ ] `/roster` displays correctly
- [ ] `/sync` connects to iRacing

If all checked, you're all set! 🎉

## 💡 Pro Tips

1. **Backup your database**: Copy `iracing_numbers.db` regularly
2. **Update regularly**: Run `pip install -r requirements.txt --upgrade`
3. **Monitor logs**: Check `bot.log` for issues
4. **Test in private**: Try commands in a private channel first

---

**Welcome to easier league management! 🏁**

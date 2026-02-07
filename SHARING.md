# 📤 How to Share This Bot

This guide explains how to share the iRacing Discord Number Bot with other league administrators.

## 🎯 Distribution Options

### Option 1: Share as ZIP File (Easiest)

Perfect for sharing with friends or small communities.

**Steps:**

1. **Prepare the files:**
   - Delete `iracing_numbers.db` (your database)
   - Delete `.env` (contains your credentials)
   - Delete `__pycache__` folders
   - Delete `bot.log` (your logs)

2. **Create ZIP:**
   - Right-click the bot folder
   - Select "Send to" > "Compressed (zipped) folder"
   - Name it: `iRacing-Number-Bot-v1.0.zip`

3. **Share:**
   - Upload to Google Drive, Dropbox, or Discord
   - Share the link with other league admins
   - Include a message directing them to the SETUP_GUIDE.md

**What they'll do:**
1. Extract the ZIP
2. Follow the SETUP_GUIDE.md
3. Create their own Discord bot
4. Configure with their league ID

### Option 2: GitHub Repository (Recommended)

Perfect for wider distribution and version control.

**Setup GitHub Repository:**

1. **Create GitHub account** (if you don't have one):
   - Go to https://github.com/signup
   - Follow signup process

2. **Create new repository:**
   - Click "+" > "New repository"
   - Name: `iracing-discord-number-bot`
   - Description: "Discord bot for managing iRacing league car numbers"
   - Set to "Public"
   - Don't initialize with README (we have one)
   - Click "Create repository"

3. **Upload files:**

   **Via GitHub Web Interface (Easy):**
   - Click "uploading an existing file"
   - Drag and drop all files EXCEPT:
     - `.env` (your credentials!)
     - `iracing_numbers.db` (your database!)
     - `bot.log` (your logs!)
     - `__pycache__/` folders
   - Click "Commit changes"

   **Via Git Command Line (Advanced):**
   ```bash
   cd "C:\Users\The_R\Documents\RM Engineering\iRacing Discord Number Bot"
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/iracing-discord-number-bot.git
   git push -u origin main
   ```

4. **Share the link:**
   - Your repository URL: `https://github.com/yourusername/iracing-discord-number-bot`
   - Share this link with other leagues!

**What they'll do:**
1. Click "Code" > "Download ZIP"
2. Follow SETUP_GUIDE.md
3. Create their own bot instance

### Option 3: Public Bot Instance (Advanced)

Host ONE bot that multiple Discord servers can use.

**⚠️ Warning**: This is more complex and requires:
- 24/7 hosting (VPS or cloud service)
- Managing multiple league configurations
- Higher resource requirements
- More security considerations

**Not recommended for beginners** - stick with Option 1 or 2 where each league runs their own independent bot.

## 📋 Pre-Share Checklist

Before sharing, make sure you:

- [ ] Delete your `.env` file (contains credentials!)
- [ ] Delete `iracing_numbers.db` (your private data!)
- [ ] Delete `bot.log` files
- [ ] Delete `__pycache__` folders
- [ ] Check README.md is up to date
- [ ] Test that SETUP_GUIDE.md works for a fresh install
- [ ] Verify all documentation is clear

## 🔐 Security Reminders

**NEVER share:**
- ❌ Your Discord bot token
- ❌ Your `.env` file
- ❌ Your database file (`iracing_numbers.db`)
- ❌ Your iRacing password

**These should NOT be in your ZIP or GitHub repo!**

The `.gitignore` file is already configured to prevent accidental uploads.

## 📝 Sample Sharing Message

When sharing with others, include this message:

```
🏁 iRacing Discord Number Bot

I've been using this bot to manage car numbers for our league and thought you might find it useful!

Features:
- Members claim numbers via Discord commands
- Syncs with iRacing to track assignments
- First-come-first-served system
- Easy admin controls
- Roster export to CSV

Setup takes about 15-30 minutes following the included guide.

Download: [Your link here]

Note: Each league runs their own independent bot, so your data stays private and you have full control.

Let me know if you have questions!
```

## 🌟 Contributing Back

If others improve the bot, consider:

1. **Accept pull requests** on GitHub
2. **Merge useful features** into your version
3. **Update documentation** with new features
4. **Thank contributors** in README.md

## 📊 Usage Statistics

If you want to track how many leagues are using it:

- Add optional telemetry (with user consent)
- Create a Discord server for bot users
- Include a "Powered by" link
- Ask users to star your GitHub repo

**Remember**: Make telemetry opt-in and respect privacy!

## 🆘 Supporting Users

If you're sharing publicly, consider:

1. **GitHub Issues**: Enable for bug reports
2. **Discord Server**: Create a support server
3. **Documentation**: Keep guides updated
4. **FAQ**: Document common questions

## 🎁 Monetization (Optional)

This bot is open source (MIT License), but if you want to offer premium features:

- ✅ Hosting service for leagues
- ✅ Priority support
- ✅ Custom features
- ✅ Consulting for league setup

Just make sure to keep the core code open source per the MIT License.

## 🤝 License Information

This bot uses the MIT License, which means:

✅ **People CAN:**
- Use it commercially
- Modify it
- Distribute it
- Use it privately
- Sublicense it

⚠️ **They MUST:**
- Include the original license
- Include copyright notice

❌ **You are NOT liable for:**
- Any warranty
- Issues they encounter
- Damages from use

## 📈 Promotion Ideas

Want to help others discover this bot?

1. **Reddit**: Post in r/iRacing
2. **iRacing Forums**: Share in league section
3. **Discord**: Share in iRacing communities
4. **YouTube**: Create a setup tutorial
5. **Twitter/X**: Tweet with #iRacing #Discord
6. **Racing Leagues**: Mention in league communities

---

**Happy sharing! Help make league management easier for everyone! 🏁**

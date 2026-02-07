# 🏁 iRacing Discord Number Bot

A Discord bot that helps iRacing leagues manage car number assignments. Members can claim numbers through Discord, and the bot syncs with iRacing to track assignments.

## ✨ Features

- **Easy Number Claiming**: Members use slash commands to claim and release car numbers
- **iRacing Integration**: Syncs with iRacing league data to see what numbers are assigned
- **Account Verification**: Optional iRacing account linking to verify members
- **First-Come-First-Served**: Automatic number reservation system
- **Admin Controls**: Full admin panel for league management
- **Roster Export**: Export your roster to CSV for easy management
- **Audit Logging**: Track all number claims and releases

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- A Discord account
- Discord server with administrator permissions
- iRacing league (for sync features)

### 1. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Under "Token", click "Copy" to copy your bot token (you'll need this later)
6. Enable these **Privileged Gateway Intents**:
   - Server Members Intent
   - Message Content Intent
7. Go to "OAuth2" > "URL Generator"
8. Select scopes: `bot`, `applications.commands`
9. Select bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Attach Files
   - Use Slash Commands
10. Copy the generated URL and open it to invite the bot to your server

### 2. Install Bot

#### Option A: Run Locally (Recommended for Testing)

```bash
# Clone or download this repository
cd "iRacing Discord Number Bot"

# Install Python dependencies
pip install -r requirements.txt

# Copy the example configuration
copy .env.example .env

# Edit .env with your credentials (use notepad or any text editor)
notepad .env
```

#### Option B: Deploy on Replit (Free Hosting)

1. Go to [Replit](https://replit.com)
2. Create a new Repl
3. Upload all the bot files
4. Click "Secrets" (lock icon) in the left sidebar
5. Add your secrets:
   - Key: `DISCORD_BOT_TOKEN`, Value: your bot token
   - Key: `IRACING_USERNAME`, Value: your iRacing email
   - Key: `IRACING_PASSWORD`, Value: your iRacing password
6. Click "Run"

### 3. Configure Bot

1. In your Discord server, use `/setup` command:
   ```
   /setup league_id:12345 min_number:0 max_number:999
   ```
2. Find your league ID:
   - Go to your league on iRacing website
   - Look at the URL: `iracing.com/membersite/member/LeagueView.do?league=12345`
   - The number after `league=` is your league ID

### 4. Start Using!

Members can now:
- `/claim 42` - Claim number 42
- `/roster` - View all claimed numbers
- `/available` - See available numbers
- `/mynumbers` - Check their claimed numbers

Admins can:
- `/sync` - Sync with iRacing
- `/export` - Export roster to CSV
- `/config` - View configuration

## 📋 Full Command List

### Member Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/claim <number>` | Claim a car number | `/claim 42` |
| `/release <number>` | Release your claimed number | `/release 42` |
| `/mynumbers` | View your claimed numbers | `/mynumbers` |
| `/check <number>` | Check if a number is available | `/check 42` |
| `/roster` | View all number assignments | `/roster` |
| `/available` | View available numbers | `/available` |
| `/link <iracing_id>` | Link your iRacing account | `/link 123456` |
| `/help` | Show help information | `/help` |

### Admin Commands

| Command | Description | Permissions Required |
|---------|-------------|---------------------|
| `/setup` | Configure the bot | Administrator |
| `/sync` | Sync with iRacing | Manage Server |
| `/syncstatus` | View sync status | Any |
| `/config` | View configuration | Manage Server |
| `/export` | Export roster to CSV | Administrator |
| `/forcerelease` | Force release a number | Administrator |
| `/auditlog` | View recent actions | Administrator |

## 🔄 How Syncing Works

The bot **cannot automatically assign numbers in iRacing** (iRacing doesn't provide an API for this), but it can:

1. **Read** assignments from iRacing to see what numbers are in use
2. **Track** claims made in Discord
3. **Compare** Discord claims with iRacing assignments
4. **Export** a list for admins to manually assign in iRacing

### Workflow:

```
Member uses /claim 42 in Discord
       ↓
Bot reserves #42 (shows as "⏳ Pending")
       ↓
Admin manually assigns #42 in iRacing website
       ↓
Bot syncs via /sync command
       ↓
Number shows as "✅ Synced"
```

### Auto-Sync

The bot automatically syncs with iRacing every hour to keep the roster updated.

## 🔧 Configuration

### Number Range

Set which numbers are available:

```
/setup league_id:12345 min_number:1 max_number:99
```

This restricts claims to numbers 1-99.

### Admin Role

Set a specific role for bot admins:

```
/setup league_id:12345 admin_role:@League Admin
```

### Announcements

Set a channel for number claim announcements:

```
/setup league_id:12345 announcement_channel:#announcements
```

### iRacing Credentials

Add to your `.env` file:

```env
IRACING_USERNAME=your_email@example.com
IRACING_PASSWORD=your_password
```

**Note**: Credentials are stored locally and only used to authenticate with iRacing's official API.

## 📊 Database

The bot uses SQLite (local file database) to store:
- Number assignments
- Guild configurations
- Audit logs

Database file: `iracing_numbers.db`

**Backup**: Regularly backup this file to prevent data loss!

## 🐛 Troubleshooting

### Bot doesn't respond to commands

1. Make sure the bot is online (green status)
2. Check bot has proper permissions in your server
3. Try re-inviting the bot with the invite URL
4. Check the bot logs for errors

### Sync fails

1. Verify your iRacing credentials in `.env`
2. Confirm your league ID is correct
3. Make sure your league has an active season
4. Check that you have an active iRacing subscription

### Commands not showing

1. Wait a few minutes after inviting the bot
2. Try kicking and re-inviting the bot
3. Make sure you selected `applications.commands` scope when inviting

### Number already claimed error

- Use `/check <number>` to see who has it
- Ask them to `/release` it or have an admin `/forcerelease`

## 📁 File Structure

```
iRacing Discord Number Bot/
├── bot.py                  # Main bot file
├── config.py              # Configuration handler
├── database.py            # Database operations
├── iracing_api.py         # iRacing API client
├── commands/              # Command modules
│   ├── __init__.py
│   ├── claim.py          # Claim/link commands
│   ├── release.py        # Release commands
│   ├── roster.py         # Roster viewing
│   ├── sync.py           # Sync commands
│   └── admin.py          # Admin commands
├── requirements.txt       # Python dependencies
├── .env.example          # Configuration template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🔒 Security

- Never share your `.env` file or bot token
- Use `.gitignore` to prevent committing secrets
- Regularly update dependencies for security patches
- Only give bot necessary permissions

## 🤝 Contributing

This bot is open source! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Fork and customize for your league

## 📝 License

This project is open source and available for anyone to use and modify.

## 💬 Support

Having issues? Here's how to get help:

1. Check this README
2. Review the bot logs (`bot.log`)
3. Make sure all dependencies are installed
4. Verify your configuration

## 🎯 Roadmap

Future features we're considering:

- [ ] Multi-class number support
- [ ] Number trading between members
- [ ] Priority/reservation system
- [ ] Statistics dashboard
- [ ] Web interface

## 📞 Credits

Built for iRacing league administrators to simplify roster management.

---

**Made with ❤️ for the iRacing community**

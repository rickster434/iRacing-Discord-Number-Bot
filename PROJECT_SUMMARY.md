# 📊 Project Summary

## Overview

The iRacing Discord Number Bot is a complete Discord bot solution for managing car number assignments in iRacing leagues. It bridges Discord and iRacing, allowing members to claim numbers through Discord while syncing with iRacing league data.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────┐
│                    Discord Bot                       │
│                     (bot.py)                        │
└───────────────┬─────────────────────────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
┌─────────┐           ┌─────────────┐
│Commands │           │   Database  │
│ Modules │◄─────────►│ (database.py)│
└─────────┘           └─────────────┘
    │                       │
    │                       │
    ▼                       ▼
┌──────────┐          ┌─────────────┐
│ iRacing  │          │   SQLite    │
│   API    │          │   Storage   │
│(iracing_ │          │(numbers.db) │
│ api.py)  │          └─────────────┘
└──────────┘
    │
    ▼
┌──────────┐
│ iRacing  │
│ Servers  │
└──────────┘
```

## File Structure & Purpose

### Core Files

| File | Purpose | Key Features |
|------|---------|-------------|
| `bot.py` | Main bot entry point | Event handling, command loading, auto-sync |
| `config.py` | Configuration management | .env file parsing, validation |
| `database.py` | Data persistence | SQLite operations, async queries |
| `iracing_api.py` | iRacing integration | Authentication, league data fetching |

### Command Modules

| Module | Commands | Description |
|--------|----------|-------------|
| `claim.py` | `/claim`, `/link` | Number claiming and account linking |
| `release.py` | `/release`, `/mynumbers` | Releasing numbers, viewing claims |
| `roster.py` | `/roster`, `/available`, `/check`, `/export` | Viewing and exporting roster |
| `sync.py` | `/sync`, `/syncstatus` | iRacing synchronization |
| `admin.py` | `/setup`, `/config`, `/forcerelease`, `/auditlog`, `/help` | Administration |

### Documentation

| File | Target Audience | Content |
|------|----------------|---------|
| `README.md` | All users | Quick start, features, commands |
| `SETUP_GUIDE.md` | Beginners | Step-by-step installation |
| `SHARING.md` | Distributors | How to share the bot |
| `CHANGELOG.md` | Developers | Version history |
| `PROJECT_SUMMARY.md` | Developers | This file - architecture overview |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env.example` | Configuration template |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Git exclusions |
| `LICENSE` | MIT License |
| `start_bot.bat` | Windows quick-start script |

## Database Schema

### Tables

**guild_config**
```sql
- guild_id (PK)          - Discord server ID
- league_id              - iRacing league ID
- min_number             - Minimum car number
- max_number             - Maximum car number
- admin_role_id          - Discord role for admins
- announcement_channel_id - Channel for announcements
- created_at             - Configuration timestamp
- updated_at             - Last update timestamp
```

**number_assignments**
```sql
- id (PK)                - Auto-increment ID
- guild_id (FK)          - Discord server ID
- car_number             - The claimed number
- discord_user_id        - Discord user ID
- iracing_id             - iRacing customer ID
- discord_username       - Discord username
- iracing_name           - iRacing display name
- status                 - 'claimed', 'synced', etc.
- claimed_at             - Claim timestamp
- synced_with_iracing    - Boolean: synced?
- iracing_verified       - Boolean: account verified?
- notes                  - Additional notes
```

**audit_log**
```sql
- id (PK)                - Auto-increment ID
- guild_id               - Discord server ID
- user_id                - User who performed action
- action                 - Action type
- details                - Action details
- timestamp              - Action timestamp
```

## Data Flow

### Number Claiming Flow

```
1. User: /claim 42
       ↓
2. Bot validates: Is 42 in range? Is it available?
       ↓
3. Database: Insert new assignment
       ↓
4. Bot: Send confirmation + announcement
       ↓
5. Status: ⏳ Pending manual assignment in iRacing
```

### Sync Flow

```
1. Admin: /sync (or auto-sync timer)
       ↓
2. Bot: Authenticate with iRacing API
       ↓
3. API: Fetch league roster from iRacing
       ↓
4. Bot: Compare iRacing data with database
       ↓
5. Database: Update synced status
       ↓
6. Bot: Report sync results
       ↓
7. Status: ✅ Synced numbers confirmed
```

## Technical Details

### Technology Stack

- **Language**: Python 3.10+
- **Discord Library**: discord.py 2.3+
- **HTTP Client**: aiohttp 3.9+
- **Database**: SQLite via aiosqlite
- **Architecture**: Async/await throughout
- **Commands**: Discord slash commands (app_commands)

### Key Design Decisions

1. **SQLite over PostgreSQL**
   - Easier for beginners (no separate database server)
   - Sufficient for small-medium leagues
   - File-based backup

2. **Async/Await**
   - Non-blocking operations
   - Better performance for API calls
   - Required by discord.py 2.0+

3. **Cog-based Commands**
   - Modular command organization
   - Easy to add/remove features
   - Better code organization

4. **Read-Only iRacing Sync**
   - iRacing doesn't provide write API
   - Focus on verification and tracking
   - Manual assignment in iRacing UI

5. **Per-Guild Configuration**
   - Multiple Discord servers supported
   - Independent configurations
   - Isolated data per server

### Security Measures

1. **Credential Storage**
   - Environment variables (.env)
   - Never committed to git (.gitignore)
   - Local storage only

2. **Permission Checks**
   - Discord permission decorators
   - Admin-only commands protected
   - Guild-specific data isolation

3. **Input Validation**
   - Number range checking
   - SQL injection prevention (parameterized queries)
   - Type checking with Discord's app_commands

## Extension Points

Want to add features? Here are the key extension points:

### Adding New Commands

1. Create new command in appropriate cog file
2. Use `@app_commands.command` decorator
3. Access bot instance via `self.bot`
4. Commands auto-sync on bot startup

Example:
```python
@app_commands.command(name="mycommand", description="My new command")
async def mycommand(self, interaction: discord.Interaction):
    await interaction.response.defer()
    # Your code here
    await interaction.followup.send("Done!")
```

### Adding Database Fields

1. Update table schema in `database.py`'s `_create_tables()`
2. Add migration logic for existing databases
3. Update related queries
4. Add to relevant command outputs

### Adding iRacing API Features

1. Add new method to `iRacingAPI` class
2. Handle authentication automatically
3. Use `_make_request()` for API calls
4. Add error handling

### Adding Configuration Options

1. Add field to `guild_config` table
2. Add parameter to `/setup` command
3. Update config display in `/config`
4. Use in relevant commands

## Performance Considerations

### Current Limits

- **Discord**: 25 fields per embed (handled in roster display)
- **SQLite**: Suitable for ~10,000 numbers per server
- **API**: iRacing rate limits (handled by hourly sync)
- **Memory**: Minimal - async operations

### Optimization Opportunities

1. **Caching**: Add Redis for frequently accessed data
2. **Bulk Operations**: Batch database updates
3. **Pagination**: For large rosters (100+ numbers)
4. **Connection Pooling**: For higher traffic

## Testing Recommendations

### Manual Testing Checklist

- [ ] All slash commands respond
- [ ] Number claiming works
- [ ] Sync retrieves iRacing data
- [ ] Roster displays correctly
- [ ] Export generates valid CSV
- [ ] Permissions enforced correctly
- [ ] Multiple users can't claim same number
- [ ] Admin commands require permissions

### Automated Testing (Future)

```python
# Unit tests
- Database operations
- Config parsing
- Number validation

# Integration tests
- Command handlers
- iRacing API calls
- Database queries

# End-to-end tests
- Full command workflows
- Multi-user scenarios
```

## Common Customizations

### Change Number Format

Edit validation in `claim.py`:
```python
# Current: 0-999
# Custom: 00-99 (two digits)
if number < 0 or number > 99:
    # validation
```

### Add Number Classes

Add to database schema:
```sql
ALTER TABLE number_assignments ADD COLUMN car_class TEXT;
```

Update commands to filter by class.

### Custom Sync Interval

In `bot.py`, change:
```python
@tasks.loop(hours=1)  # Change to minutes, hours, etc.
async def auto_sync(self):
```

### Disable Announcements

In commands, skip this block:
```python
if config and config.get('announcement_channel_id'):
    # Skip or remove
```

## Deployment Options

### Local Machine
- Simplest: Double-click `start_bot.bat`
- Keep computer on 24/7
- Port forwarding not needed

### Replit (Free)
- Web-based hosting
- Automatic restarts
- Free tier available
- Secrets management built-in

### VPS (DigitalOcean, Linode, etc.)
- Full control
- Better uptime
- Costs ~$5/month
- Requires Linux knowledge

### Docker (Advanced)
- Containerized deployment
- Easy updates
- Reproducible environment
- Requires Docker knowledge

## Maintenance

### Regular Tasks

**Daily**
- Monitor bot uptime
- Check for error messages in logs

**Weekly**
- Review audit log for issues
- Check sync is working
- Backup database file

**Monthly**
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Review and clean old logs
- Check for Discord.py updates

### Troubleshooting Tools

1. **Logs**: Check `bot.log`
2. **Database**: Use SQLite browser
3. **Discord**: Developer Portal > Bot
4. **iRacing**: Test API separately

## Future Enhancements

### Planned
- Multi-class support
- Number trading
- Statistics dashboard
- Web interface

### Community Requests
- Number history tracking
- Team number blocks
- Automated reminders
- Conflict resolution

## Contributing

Want to contribute?

1. Fork on GitHub
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

See `SHARING.md` for more details.

## Credits

Built for the iRacing community by league administrators who wanted easier number management.

**Technology Credits:**
- discord.py - Discord API library
- aiohttp - Async HTTP client
- SQLite - Embedded database

---

**Version**: 1.0.0
**Last Updated**: 2026-02-07
**Python**: 3.10+
**License**: MIT

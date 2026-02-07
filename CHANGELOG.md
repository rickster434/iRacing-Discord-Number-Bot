# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-02-07

### Added
- Initial release of iRacing Discord Number Bot
- Car number claiming system (`/claim`, `/release`)
- iRacing league integration and sync
- Member account verification with iRacing
- Complete roster management (`/roster`, `/available`, `/check`)
- Admin controls and configuration (`/setup`, `/config`, `/forcerelease`)
- Automatic hourly sync with iRacing
- CSV export functionality for rosters
- Audit logging for all actions
- Comprehensive help system (`/help`)
- SQLite database for local storage
- Full slash command support
- Announcement system for number claims
- Number range configuration (min/max)
- Admin role support
- Pending vs synced status tracking

### Features
- First-come-first-served number claiming
- Read-only sync from iRacing leagues
- Beginner-friendly setup process
- Works with any iRacing league
- Supports multiple Discord servers
- Free and open source

### Documentation
- Complete README with quick start guide
- Detailed SETUP_GUIDE for beginners
- Example configuration files
- Troubleshooting guide
- Command reference

## [Unreleased]

### Planned Features
- Multi-class number support
- Number trading system
- Priority/reservation system
- Web dashboard
- Statistics tracking
- Automated testing
- Docker support

---

## Version Format

This project follows [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for new functionality (backwards compatible)
- PATCH version for bug fixes (backwards compatible)

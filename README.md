# LinkVault - URL Shortener with Analytics

A SaaS-style link management tool. Shorten URLs, track clicks, and analyze traffic sources.

## The Problem

Long URLs are unwieldy for sharing, especially on social media or in print. But most URL shorteners are either:
- Too basic (no analytics)
- Too complex (enterprise features you don't need)
- Too expensive (subscription for simple needs)

## The Solution

LinkVault provides a clean, focused link shortener with:
- **Simple URL shortening** - Paste and go
- **Click analytics** - See who's clicking
- **Traffic sources** - Know where clicks come from
- **Device breakdown** - Desktop vs mobile insights

## Features

### Dashboard
- Quick link creation form
- Stats overview (total links, clicks, active)
- 7-day click chart
- Recent links list

### Link Management
- Custom short codes
- Optional expiration dates
- Activate/deactivate links
- Delete links

### Analytics (per link)
- Total clicks
- Clicks over time (30 days)
- Device breakdown (desktop/mobile/tablet)
- Browser distribution
- Referrer sources

## Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Database**: SQLite
- **Frontend**: Vanilla JavaScript, CSS
- **Analytics**: User-agent parsing, referrer tracking

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open in browser
open http://localhost:5003

# Load demo data
# Click "Load Demo" in the navbar
```

## Project Structure

```
linkvault/
├── app.py              # Main application
├── templates/
│   ├── base.html       # Layout
│   ├── dashboard.html  # Main dashboard
│   ├── links.html      # All links list
│   ├── link_detail.html# Single link analytics
│   └── expired.html    # Expired link page
├── static/
│   ├── style.css       # Styling
│   └── app.js          # Client-side logic
├── requirements.txt
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard |
| `/links` | GET | All links |
| `/link/<id>` | GET | Link analytics |
| `/r/<code>` | GET | Redirect (tracks click) |
| `/api/link` | POST | Create link |
| `/api/link/<id>` | PUT | Update link |
| `/api/link/<id>` | DELETE | Delete link |
| `/api/stats` | GET | Overall statistics |
| `/seed` | GET | Load demo data |

## Data Model

### Link
- `id`: Primary key
- `original_url`: The destination URL
- `short_code`: The unique short identifier
- `title`: Optional descriptive title
- `created_at`: Creation timestamp
- `expires_at`: Optional expiration
- `is_active`: Enable/disable without deleting

### Click
- `id`: Primary key
- `link_id`: Foreign key to Link
- `clicked_at`: Click timestamp
- `ip_address`: Visitor IP
- `user_agent`: Browser info
- `referrer`: Traffic source
- `device_type`: desktop/mobile/tablet
- `browser`: Chrome/Safari/Firefox/etc.

## SaaS Patterns Demonstrated

1. **Freemium potential**: Core features free, premium analytics
2. **Analytics focus**: Data-driven value proposition
3. **API-first**: Clean REST API for integrations
4. **Clean UX**: Focused, no feature bloat

## Future Enhancements

- User accounts and authentication
- Team workspaces
- API keys for programmatic access
- QR code generation
- Link groups/campaigns
- Export analytics to CSV
- Custom domains

---

*Built as a portfolio project demonstrating SaaS product development.*

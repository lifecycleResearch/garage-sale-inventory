# Garage Sale Inventory & Listing App

Custom-built inventory management system with AI vision, price comps, and multi-platform listing.

## Quick Start

```bash
cd ~/workspace/garage-sale-inventory
./scripts/run.sh
```

Then open the public URL (via Cloudflared tunnel) on your phone.

## Features

- **Camera capture** — Take photos directly from phone browser
- **AI vision** — Optional API key for auto brand/description detection
- **Price comps** — DuckDuckGo search for similar item prices
- **Inventory management** — SQLite database with CRUD
- **Multi-platform listing** — eBay, Facebook Marketplace, Craigslist, Shopify, WooCommerce, X, Instagram
- **Batch export** — Select all → authenticate → mass upload

## Architecture

```
garage-sale-inventory/
├── python/
│   ├── main.py          # FastAPI backend
│   ├── db.py            # SQLite helper
│   ├── vision.py        # AI vision (Ollama or API key)
│   ├── comps.py         # Price comparison search
│   └── platforms/       # Platform integrations
├── static/
│   ├── index.html       # Single-page app
│   ├── app.js           # Frontend logic
│   └── styles.css       # Mobile-first CSS
├── uploads/             # Saved item photos
├── scripts/
│   ├── run.sh           # Start server + tunnel
│   └── setup.sh         # One-time setup
└── README.md
```

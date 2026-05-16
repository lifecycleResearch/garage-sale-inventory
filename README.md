# Garage Sale Inventory & Listing App

AI-powered inventory management system for garage sales, estate sales, and resellers. Snap a photo, get AI brand identification and description, find price comps, generate listings for 9+ platforms, and track inventory.

## Live URLs

| Environment | URL |
|-------------|-----|
| **Production (Fly.io)** | https://garage-sale-inventory.fly.dev |
| **GitHub Repo** | https://github.com/lifecycleResearch/garage-sale-inventory |

## Features

- 📷 **Camera Capture** — Browser camera with fallback to file upload
- 🤖 **AI Vision** — Optional OpenAI GPT-4 Vision for auto-identification (set `OPENAI_API_KEY`)
- 🔍 **Price Comps** — Free DuckDuckGo web search, no API key needed
- 📦 **Inventory Tracking** — Draft → Listed → Sold workflow
- 🚀 **9 Platforms** — eBay, Facebook Marketplace, Craigslist, Instagram, X, Shopify, WooCommerce, Poshmark, Mercari
- 📊 **CSV Export** — Standard + eBay File Exchange format
- 📱 **PWA** — Installable on phone home screen, works offline
- 🌐 **Public URL** — Cloudflared tunnel for instant sharing

## Quick Start (Local)

```bash
git clone https://github.com/lifecycleResearch/garage-sale-inventory.git
cd garage-sale-inventory
./scripts/setup.sh
./scripts/run.sh
```

The `run.sh` script starts the FastAPI backend and a Cloudflared tunnel. You'll get a public URL like `https://xxxx.trycloudflare.com` — open it on your phone.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/items` | POST | Create item with photo |
| `/api/items` | GET | List all items |
| `/api/items/{id}` | GET/PUT/DELETE | Item CRUD |
| `/api/items/{id}/analyze` | POST | AI vision analysis |
| `/api/items/{id}/comps` | POST | Price comparison search |
| `/api/items/{id}/listings` | POST | Generate platform listings |
| `/api/batch/list` | POST | Batch generate listings |
| `/api/platforms` | GET | List connected platforms |
| `/api/export/csv` | GET | Export inventory CSV |
| `/api/export/ebay` | GET | Export eBay File Exchange |

## Environment Variables

```bash
OPENAI_API_KEY=sk-...      # Optional, for AI vision
ANTHROPIC_API_KEY=sk-ant-... # Alternative AI provider
GEMINI_API_KEY=...          # Google Gemini alternative
PORT=8000                   # Server port
```

## Tech Stack

- **Backend**: FastAPI + Python 3.11 + SQLite
- **Frontend**: Vanilla HTML/CSS/JS (no build step)
- **AI**: OpenAI GPT-4 Vision (optional), Ollama (local, optional)
- **Search**: DuckDuckGo HTML scraping (free, no key)
- **Deploy**: Fly.io (Docker), Cloudflared tunnel (temporary)

## Mobile Setup

1. Open the Fly.io URL or Cloudflared tunnel URL on your phone
2. Tap "Add to Home Screen" (iOS) or "Install App" (Android)
3. Use the camera tab to snap photos
4. Fill in details manually or tap "Find Comps" for price suggestions

## Platform Integrations

Most platforms (FB Marketplace, Craigslist, Instagram, X, Poshmark, Mercari) don't have public APIs for listing. The app generates copy-paste formatted text for each platform.

Platforms with APIs (eBay, Shopify, WooCommerce, X API v2) can be connected in the Platforms tab. Enter API credentials and the app will store them for future automated listing.

## SaaS Roadmap

See the original design doc in the GitHub repo issues for the full SaaS architecture with React Native, multi-tenancy, and Stripe billing.

## License

MIT — Built for personal use, free to fork and extend.

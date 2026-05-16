# Marketplace APIs & Automation Guide

Deep-dive into every marketplace's API status, key requirements, and automation alternatives.

---

## Tier 1: Direct APIs (Official, Supported)

### eBay
- **API**: eBay REST API (Sell API + Buy API)
- **Key Required**: Yes — OAuth 2.0 (Client ID + Client Secret)
- **Docs**: https://developer.ebay.com/
- **Cost**: Free up to 5M calls/day for most sellers
- **Capabilities**: List items, revise, end, get orders, manage inventory, fulfillment
- **Sandbox**: Yes
- **Rate Limits**: 5,000/minute for Trading API, 10,000/day for Inventory API
- **GitHub Tools**:
  - `ebay/restfeed-sdk-java` — Official Java SDK
  - `hendt/ebay-api` — Node.js wrapper (1.2k stars)
  - `fredollinger/ebaysdk-python` — Python SDK (not maintained)
  - **Best**: `tsubik/ebay-rest-api-client` or build raw OAuth

### Amazon (Seller Central / Marketplace Web Service)
- **API**: Selling Partner API (SP-API) — replaced MWS in 2022
- **Key Required**: Yes — AWS IAM + LWA OAuth
- **Docs**: https://developer-docs.amazon.com/sp-api/
- **Cost**: Free, but complex onboarding
- **Capabilities**: Listings, orders, FBA, reports, inventory
- **GitHub Tools**:
  - `amz-tools/amazon-sp-api` — Node.js (1.5k stars)
  - `saleweaver/python-amazon-sp-api` — Python (800+ stars)
  - `jessepollak/amazon-sp-api-php` — PHP
- **Note**: Requires professional seller account ($39.99/mo)

### Etsy
- **API**: Etsy Open API v3
- **Key Required**: Yes — OAuth 2.0
- **Docs**: https://developers.etsy.com/
- **Cost**: Free
- **Capabilities**: Create listings, manage shop, get orders, shipping
- **Rate Limits**: 10 requests/second
- **GitHub Tools**:
  - `etsy/open-api` — Official
  - `bvanbree/etsy-python` — Python wrapper
- **Note**: Requires Etsy seller account

### Shopify
- **API**: Shopify Admin REST API + GraphQL
- **Key Required**: Yes — Private app API key or OAuth
- **Docs**: https://shopify.dev/docs/api/admin-rest
- **Cost**: Included with any Shopify plan
- **Capabilities**: Full store management — products, orders, customers, inventory
- **Rate Limits**: 2 requests/second (standard), 4/s (Shopify Plus)
- **GitHub Tools**:
  - `Shopify/shopify_python_api` — Official Python (1.5k stars)
  - `MONEI/Shopify-api-node` — Node.js (1.2k stars)
- **Note**: Requires active Shopify store ($29/mo+)

### WooCommerce
- **API**: WooCommerce REST API v3
- **Key Required**: Yes — Consumer Key + Consumer Secret (Basic Auth)
- **Docs**: https://woocommerce.github.io/woocommerce-rest-api-docs/
- **Cost**: Free (requires WordPress + WooCommerce plugin)
- **Capabilities**: Products, orders, customers, reports
- **Rate Limits**: Configurable, default unlimited
- **GitHub Tools**:
  - `woocommerce/wc-api-python` — Official Python
  - `woocommerce/woocommerce-rest-api-js-lib` — Official JS

### Poshmark
- **API**: **NO OFFICIAL API** — Poshmark has never released a public API
- **Workaround**: Web scraping (terms prohibit it)
- **Automation Tools**:
  - `poshmark-closet-sharing` (various repos on GitHub) — Selenium-based sharing bots
  - `poshmark-bot` — Python + Selenium for closet sharing
- **Risk**: Poshmark actively bans automation. Use at your own risk.
- **Manual Only**: Official position

### Mercari
- **API**: **NO OFFICIAL PUBLIC API**
- **Internal API**: Exists for the mobile app but undocumented
- **Workaround**: Reverse-engineered API wrappers exist
- **GitHub Tools**:
  - `mercari/mercari-api` — No official repo
  - `mercari-engineering` — Only SDKs for Japan-specific services
  - Community repos: `mercari-api-python`, `mercari-scraper` (unofficial, fragile)
- **Manual Only**: Recommended

### Depop
- **API**: Depop API exists but is **private/partner-only**
- **Public Access**: No — application required, rarely granted
- **Docs**: https://developer.depop.com/ — behind application wall
- **GitHub Tools**: None official. Community scrapers exist but break frequently.
- **Manual Only**: Recommended

### Vinted
- **API**: **NO OFFICIAL API**
- **Workaround**: Community reverse-engineered the internal API
- **GitHub Tools**:
  - `Vinted-API` — Various community repos, frequently broken
  - `vinted-python` — Unofficial wrapper
- **Manual Only**: Recommended

### Grailed
- **API**: **NO OFFICIAL API**
- **Status**: No plans announced
- **Manual Only**

### StockX
- **API**: StockX API exists for **partners only**
- **Public Access**: No — requires business partnership
- **Docs**: https://developer.stockx.com/ — behind approval wall
- **Manual Only**

### Reverb
- **API**: Reverb API (REST)
- **Key Required**: Yes — OAuth 2.0 or API key
- **Docs**: https://reverb.com/swagger/
- **Cost**: Free
- **Capabilities**: Listings, orders, messages, shipping
- **GitHub Tools**:
  - `reverb/reverb-api-ruby` — Official Ruby SDK
  - Community wrappers for Python/Node

### Chairish
- **API**: **NO PUBLIC API**
- **Manual Only**

### 1stDibs
- **API**: **NO PUBLIC API** — Partner/Dealer portal only
- **Manual Only**

### Bonanza
- **API**: Bonanza API (SOAP/XML)
- **Key Required**: Yes — API key from developer settings
- **Docs**: https://api.bonanza.com/docs
- **Cost**: Free
- **Capabilities**: Listings, orders, feedback
- **Note**: XML/SOAP only, somewhat dated

### Ruby Lane
- **API**: **NO PUBLIC API**
- **Manual Only**

### Tradesy
- **API**: **NO PUBLIC API** (shut down in 2022)
- **Status**: Defunct

---

## Tier 2: Social / Local Platforms (No API or Very Limited)

### Facebook Marketplace
- **API**: **NO PUBLIC API** for individual sellers
- **Internal**: Facebook Commerce API exists for **businesses** with a Facebook Shop
- **Requirements**: Business Manager + Commerce Account + Facebook Shop
- **Docs**: https://developers.facebook.com/docs/commerce/
- **Key Required**: Yes — Business OAuth
- **Note**: Individual garage sale sellers **cannot** use this. Must post manually.
- **Automation Alternatives**:
  - **Selenium/Playwright bots** (violates ToS)
  - `facebook-marketplace-scraper` — GitHub repos for scraping only
  - **No reliable open-source posting tool exists**

### Craigslist
- **API**: **NO API** — Craigslist famously blocks all automation
- **Posting**: Manual web form only
- **Rate Limits**: Phone verification required, strict IP limits
- **Automation**: Against ToS, accounts get flagged immediately
- **GitHub Tools**:
  - `craigslist-api` — Scrapers only, not for posting
  - **No trustworthy posting automation exists**

### Instagram
- **API**: Instagram Graph API (for Business/Creator accounts)
- **Key Required**: Yes — Facebook App + OAuth
- **Docs**: https://developers.facebook.com/docs/instagram-api/
- **Posting**: **CANNOT create feed posts via API** — only Stories, Reels, and basic media
- **Limitation**: Instagram Graph API does NOT support creating regular feed posts with captions
- **Workaround**: Meta Business Suite (manual scheduling)
- **Automation**:
  - `instagrapi` (Python, 7k stars) — Unofficial, reverse-engineered mobile API
  - `instagram-private-api` (Node.js, 5k stars) — Unofficial
  - **Risk**: Accounts get banned. Use burners.

### X / Twitter
- **API**: X API v2
- **Key Required**: Yes — Bearer Token or OAuth 1.0a
- **Docs**: https://developer.twitter.com/en/docs/twitter-api
- **Cost**: Free tier: 1,500 tweets/month read, 500 tweets/month write
- **Basic tier**: $100/mo for more write access
- **Capabilities**: Post tweets, threads, media, analytics
- **GitHub Tools**:
  - `twitterdev/twitter-api-python-sdk` — Official
  - `tweepy/tweepy` — Python (12k stars), supports v2
  - `plenaryapp/twitter-api-client` — Node.js
- **Note**: Free tier is very limited for mass listing. Consider Basic tier.

### TikTok Shop
- **API**: TikTok Shop Partner API
- **Key Required**: Yes — Partner application + OAuth
- **Docs**: https://seller.tiktokglobalshop.com/university/website
- **Note**: Requires TikTok Shop seller account (US only in select states)
- **GitHub Tools**: Limited. Official SDKs from TikTok.

### OfferUp
- **API**: **NO PUBLIC API**
- **Status**: No automation support. Manual only.

### Nextdoor
- **API**: Nextdoor Ads API exists for businesses
- **Individual Sellers**: No API. Manual posting only.

### ThredUp
- **API**: **NO PUBLIC API**
- **Model**: Send items to ThredUp, they list for you
- **Manual Only**

---

## Tier 3: Niche / Specialty Marketplaces

### Newegg
- **API**: Newegg Seller API (REST)
- **Key Required**: Yes — API key + Seller ID
- **Docs**: https://developer.newegg.com/
- **Note**: Electronics focus

### Rakuten
- **API**: Rakuten Ichiba API (Japan-focused)
- **Key Required**: Yes — Application-based
- **Docs**: https://webservice.rakuten.co.jp/

### Walmart Marketplace
- **API**: Walmart Marketplace API
- **Key Required**: Yes — OAuth
- **Docs**: https://developer.walmart.com/
- **Note**: Requires Walmart seller approval

### Target Plus
- **API**: No public API. Invitation-only seller program.

### Best Buy Marketplace
- **API**: No public API. Third-party sellers use partner portals.

### Google Shopping
- **API**: Google Content API for Shopping
- **Key Required**: Yes — Google Cloud OAuth
- **Docs**: https://developers.google.com/shopping-content
- **Note**: Free product listings + paid ads
- **GitHub Tools**:
  - `google/google-api-python-client` — Official
  - `googleads/googleads-python-lib` — For Shopping Ads

### Sears Marketplace
- **API**: No public API. Manual portal only.

### Wish
- **API**: Wish Merchant API
- **Key Required**: Yes
- **Docs**: https://merchant.wish.com/documentation/api

### AliExpress
- **API**: AliExpress Open Platform API
- **Key Required**: Yes — Application-based
- **Note**: Dropshipping focus

### Alibaba
- **API**: Alibaba Open API
- **Key Required**: Yes
- **Note**: B2B wholesale focus

### Wayfair
- **API**: Partner Home API
- **Key Required**: Yes — Invitation only
- **Note**: Furniture/home goods

### Houzz
- **API**: **NO PUBLIC API**
- **Note**: Home goods

### Curtsy
- **API**: **NO PUBLIC API**
- **Note**: Women's clothing/app

### Kidizen
- **API**: **NO PUBLIC API**
- **Note**: Kids' items

### Mercari (Japan)
- **API**: Same as US — no public API

### Yahoo Auctions (Japan)
- **API**: Yahoo! Japan Developer Network API
- **Key Required**: Yes
- **Docs**: https://developer.yahoo.co.jp/

### Auctiva / InkFrog
- **API**: These are eBay listing tools with their own APIs
- **Note**: Wrapper services around eBay

### Sellbrite / GoDaddy Commerce
- **API**: Multi-channel listing API
- **Key Required**: Yes
- **Note**: Paid service ($19/mo+)

---

## Tier 4: Open-Source Automation Alternatives (No API Platforms)

For platforms without APIs, here are **trustworthy GitHub projects** that use browser automation. Use responsibly.

### Multi-Platform Listing Tools

#### Vendoo (Closed Source, Paid)
- **URL**: https://vendoo.co/
- **Price**: $29/mo
- **Platforms**: eBay, Poshmark, Mercari, Depop, Grailed, Etsy, Facebook Marketplace, Shopify
- **API**: No open API. Browser automation under the hood.

#### List Perfectly (Closed Source, Paid)
- **URL**: https://listperfectly.com/
- **Price**: $29/mo
- **Platforms**: eBay, Poshmark, Mercari, Depop, Facebook, Instagram, Shopify

#### Crosslist (Closed Source, Paid)
- **URL**: https://crosslist.com/
- **Price**: $19/mo

### Open-Source Browser Automation Projects

#### `playwright` + `playwright-stealth`
- **URL**: https://github.com/microsoft/playwright
- **Stars**: 65k+
- **Use**: Write your own automation scripts for any platform
- **Languages**: Python, Node.js, Java, C#
- **Trustworthy**: Yes — Official Microsoft project

#### `selenium` + `undetected-chromedriver`
- **URL**: https://github.com/ultrafunkamsterdam/undetected-chromedriver
- **Stars**: 6k+
- **Use**: Stealth Chrome automation that bypasses bot detection
- **Trustworthy**: Yes — widely used

#### `puppeteer-extra` + `puppeteer-extra-plugin-stealth`
- **URL**: https://github.com/berstend/puppeteer-extra
- **Stars**: 5k+
- **Use**: Stealth Puppeteer for browser automation
- **Trustworthy**: Yes

#### `instagrapi` (Instagram Unofficial)
- **URL**: https://github.com/subzeroid/instagrapi
- **Stars**: 7k+
- **Use**: Private Instagram API wrapper
- **Risk**: Account bans possible
- **Trustworthy**: Active maintenance, large community

#### `facebook-scraper`
- **URL**: https://github.com/kevinzg/facebook-scraper
- **Stars**: 3k+
- **Use**: Scrape Facebook pages/posts (NOT marketplace listings)
- **Trustworthy**: Yes, but limited scope

#### `craigslist-scraper`
- **URL**: Various repos — search `craigslist scraper python`
- **Use**: Scrape Craigslist listings (read-only)
- **Note**: No trustworthy posting automation exists

#### `mercari-scraper`
- **URL**: Various community repos
- **Use**: Scrape Mercari listings
- **Trustworthy**: Fragile, breaks often

### All-in-One Open Source Projects

#### `resell-helper` / `closet-tools` (Search GitHub)
- Search terms: `poshmark bot`, `mercari bot`, `depop bot`
- **Caution**: Many are abandoned or contain malware. Vet carefully.

#### `browserless/chrome` (Headless Chrome as a Service)
- **URL**: https://github.com/browserless/chrome
- **Stars**: 6k+
- **Use**: Run headless Chrome in Docker for automation
- **Trustworthy**: Yes — established project

---

## Summary Matrix

| Platform | Has API | Free Tier | Key Required | Automation Level |
|----------|---------|-----------|--------------|------------------|
| eBay | ✅ Yes | ✅ Yes | OAuth | Full API |
| Amazon | ✅ Yes | ✅ Yes | AWS IAM + OAuth | Full API |
| Etsy | ✅ Yes | ✅ Yes | OAuth | Full API |
| Shopify | ✅ Yes | ✅ Included | API Key / OAuth | Full API |
| WooCommerce | ✅ Yes | ✅ Free | Basic Auth | Full API |
| X / Twitter | ✅ Yes | ✅ 500 tweets/mo | Bearer / OAuth | API (limited free) |
| Reverb | ✅ Yes | ✅ Yes | OAuth / Key | Full API |
| Bonanza | ✅ Yes | ✅ Yes | API Key | Full API (SOAP) |
| Google Shopping | ✅ Yes | ✅ Yes | OAuth | Full API |
| Newegg | ✅ Yes | ✅ Yes | Key + Seller ID | Full API |
| Walmart | ✅ Yes | ✅ Yes | OAuth | Full API |
| Wish | ✅ Yes | ✅ Yes | Key | Full API |
| Facebook Marketplace | ❌ No | N/A | N/A | Manual / Business only |
| Craigslist | ❌ No | N/A | N/A | Manual only |
| Poshmark | ❌ No | N/A | N/A | Manual / Risky bots |
| Mercari | ❌ No | N/A | N/A | Manual / Fragile scrapers |
| Depop | ❌ No | N/A | N/A | Manual |
| Vinted | ❌ No | N/A | N/A | Manual / Fragile |
| Grailed | ❌ No | N/A | N/A | Manual |
| StockX | ❌ No | N/A | N/A | Manual / Partner only |
| Instagram | ⚠️ Limited | N/A | OAuth | No feed posts via API |
| TikTok Shop | ⚠️ Partner | N/A | OAuth | Limited |
| OfferUp | ❌ No | N/A | N/A | Manual |
| Nextdoor | ❌ No | N/A | N/A | Manual |
| Chairish | ❌ No | N/A | N/A | Manual |
| 1stDibs | ❌ No | N/A | N/A | Manual |
| Ruby Lane | ❌ No | N/A | N/A | Manual |
| Curtsy | ❌ No | N/A | N/A | Manual |
| Kidizen | ❌ No | N/A | N/A | Manual |
| ThredUp | ❌ No | N/A | N/A | Send-in model |
| Tradesy | ❌ Dead | N/A | N/A | Defunct |
| AliExpress | ✅ Yes | ✅ Yes | Key | Full API |
| Rakuten | ✅ Yes | ✅ Yes | Application | Full API |
| Wayfair | ✅ Yes | ❌ Invitation | OAuth | Full API |
| Yahoo Auctions JP | ✅ Yes | ✅ Yes | OAuth | Full API |

---

## Recommendation for Our App

### Phase 1 (Current MVP): Copy-Paste Listings
For **all** platforms, generate formatted text that the user copies and pastes manually. This works for every single platform with zero API risk.

### Phase 2: API Integrations (Where Possible)
Implement direct API posting for:
1. **eBay** — Full REST API, very capable
2. **Shopify** — Full store management
3. **WooCommerce** — Easy REST API
4. **Etsy** — Good API for handmade/vintage
5. **X / Twitter** — Free tier for basic promotion
6. **Google Shopping** — Free product listings
7. **Amazon** — If user has professional seller account

### Phase 3: Browser Automation (Advanced)
For platforms without APIs (Poshmark, Mercari, Depop, Facebook Marketplace):
- Use **Playwright + stealth** in isolated Docker containers
- Rotate sessions, fingerprints, and proxies
- This is what Vendoo/List Perfectly do under the hood
- **Requires**: Daytona/browser-swarm infrastructure we already built

### Trusted GitHub Repos for Building Automation

```
# Core browser automation
microsoft/playwright                          (65k stars)
ultrafunkamsterdam/undetected-chromedriver    (6k stars)
berstend/puppeteer-extra                      (5k stars)

# Platform-specific (unofficial, use carefully)
subzeroid/instagrapi                          (7k stars) - Instagram
kevinzg/facebook-scraper                      (3k stars) - Facebook read-only

# Infrastructure
browserless/chrome                            (6k stars) - Headless Chrome service

# eBay
hendt/ebay-api                                (1.2k stars) - Node.js wrapper
saleweaver/python-amazon-sp-api               (800 stars) - Amazon SP-API

# Shopify
Shopify/shopify_python_api                    (1.5k stars) - Official Python
```

---

## Next Steps

1. **Add `cost` field to items** for profit tracking — allows true P&L reporting
2. **Implement API integrations** for eBay, Etsy, Shopify first (highest ROI)
3. **Build browser automation module** using our existing `browser-swarm` infrastructure for the no-API platforms
4. **Add OAuth credential manager** in the Platforms tab for API key storage

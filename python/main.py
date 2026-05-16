"""FastAPI backend for garage sale inventory app."""
from __future__ import annotations

import csv
import io
import json
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from comps import find_comps
from db import (
    create_item,
    delete_item,
    dict_to_item,
    get_categories,
    get_item,
    get_items,
    get_platform,
    get_platforms,
    init_db,
    set_item_status,
    set_platform_auth,
    update_item,
)
from vision import analyze_image

app = FastAPI(title="Garage Sale Inventory", version="0.1.0")

# Allow CORS for local dev and mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

init_db()


# ───────────────────────────────────────────────────────────────
# Items
# ───────────────────────────────────────────────────────────────


@app.post("/api/items")
async def api_create_item(
    name: str = Form(""),
    brand: str = Form(""),
    description: str = Form(""),
    category: str = Form("Other"),
    condition: str = Form("Good"),
    price: float = Form(0.0),
    suggested_price: float = Form(0.0),
    platforms: str = Form("[]"),
    status: str = Form("draft"),
    image: UploadFile | None = File(None),
):
    """Create a new inventory item with optional photo upload."""
    image_path = None
    if image and image.filename:
        ext = Path(image.filename).suffix or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        image_path = str(UPLOAD_DIR / filename)
        with open(image_path, "wb") as f:
            f.write(await image.read())

    item = create_item({
        "name": name,
        "brand": brand,
        "description": description,
        "category": category,
        "condition": condition,
        "price": price,
        "suggested_price": suggested_price,
        "image_path": image_path,
        "platforms_json": platforms,
        "status": status,
    })
    return dict_to_item(item)


@app.get("/api/items")
def api_list_items(status: str | None = None, limit: int = 1000, offset: int = 0):
    items = get_items(status=status, limit=limit, offset=offset)
    return {"items": [dict_to_item(i) for i in items], "count": len(items)}


@app.get("/api/items/{item_id}")
def api_get_item(item_id: str):
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return dict_to_item(item)


@app.put("/api/items/{item_id}")
async def api_update_item(
    item_id: str,
    name: str = Form(""),
    brand: str = Form(""),
    description: str = Form(""),
    category: str = Form(""),
    condition: str = Form(""),
    price: float = Form(0.0),
    suggested_price: float = Form(0.0),
    platforms: str = Form(""),
    status: str = Form(""),
    image: UploadFile | None = File(None),
):
    data: dict[str, Any] = {}
    if name:
        data["name"] = name
    if brand:
        data["brand"] = brand
    if description:
        data["description"] = description
    if category:
        data["category"] = category
    if condition:
        data["condition"] = condition
    if price > 0:
        data["price"] = price
    if suggested_price > 0:
        data["suggested_price"] = suggested_price
    if platforms:
        data["platforms_json"] = platforms
    if status:
        data["status"] = status

    if image and image.filename:
        ext = Path(image.filename).suffix or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        image_path = str(UPLOAD_DIR / filename)
        with open(image_path, "wb") as f:
            f.write(await image.read())
        data["image_path"] = image_path

    item = update_item(item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return dict_to_item(item)


@app.delete("/api/items/{item_id}")
def api_delete_item(item_id: str):
    if not delete_item(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": item_id}


@app.post("/api/items/{item_id}/analyze")
async def api_analyze_image(item_id: str):
    """Run AI vision analysis on an item's photo."""
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not item.get("image_path"):
        raise HTTPException(status_code=400, detail="Item has no image")

    result = analyze_image(item["image_path"])

    # Auto-fill fields if confidence is high enough
    updates = {}
    if result.get("name") and result.get("confidence", 0) > 0.5:
        updates["name"] = result["name"]
    if result.get("brand") and result.get("confidence", 0) > 0.5:
        updates["brand"] = result["brand"]
    if result.get("description") and result.get("confidence", 0) > 0.3:
        updates["description"] = result["description"]
    if result.get("category"):
        updates["category"] = result["category"]
    if result.get("condition"):
        updates["condition"] = result["condition"]

    if updates:
        update_item(item_id, updates)

    return {"analysis": result, "updated_fields": list(updates.keys())}


@app.post("/api/items/{item_id}/comps")
def api_find_comps(item_id: str):
    """Find price comps for an item via web search."""
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    result = find_comps(
        item_name=item.get("name", ""),
        brand=item.get("brand", ""),
        category=item.get("category", ""),
    )

    # Update suggested price if we got a good suggestion
    if result["suggestion"].get("suggested_price"):
        update_item(item_id, {"suggested_price": result["suggestion"]["suggested_price"]})

    return result


@app.post("/api/items/{item_id}/status")
def api_set_status(item_id: str, status: str = Form(...)):
    item = set_item_status(item_id, status)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return dict_to_item(item)


# ───────────────────────────────────────────────────────────────
# Categories
# ───────────────────────────────────────────────────────────────


@app.get("/api/categories")
def api_categories():
    return {"categories": get_categories()}


# ───────────────────────────────────────────────────────────────
# Platforms & Listings
# ───────────────────────────────────────────────────────────────


PLATFORM_INFO = {
    "ebay": {"name": "eBay", "has_api": True, "auth_type": "oauth"},
    "facebook_marketplace": {"name": "Facebook Marketplace", "has_api": False, "auth_type": "none"},
    "craigslist": {"name": "Craigslist", "has_api": False, "auth_type": "none"},
    "instagram": {"name": "Instagram", "has_api": False, "auth_type": "oauth"},
    "x": {"name": "X / Twitter", "has_api": True, "auth_type": "bearer"},
    "shopify": {"name": "Shopify", "has_api": True, "auth_type": "api_key"},
    "woocommerce": {"name": "WooCommerce", "has_api": True, "auth_type": "basic"},
    "poshmark": {"name": "Poshmark", "has_api": False, "auth_type": "none"},
    "mercari": {"name": "Mercari", "has_api": False, "auth_type": "none"},
}


def _generate_listing_text(item: dict, platform: str) -> dict:
    """Generate platform-specific listing text for copy-paste."""
    name = item.get("name", "Unknown Item")
    brand = item.get("brand", "")
    description = item.get("description", "")
    category = item.get("category", "Other")
    condition = item.get("condition", "Good")
    price = item.get("price", 0.0) or item.get("suggested_price", 0.0)

    full_description = f"{brand} {name}".strip() if brand else name
    if description:
        full_description += f"\n\n{description}"
    full_description += f"\n\nCondition: {condition}"
    full_description += f"\nCategory: {category}"

    if platform == "ebay":
        title = f"{brand} {name} {condition}"[:80].strip()
        return {
            "title": title,
            "description": full_description,
            "price": price,
            "category": category,
            "condition": condition,
            "format": "copy-paste",
        }

    if platform == "facebook_marketplace":
        return {
            "title": f"{name} - {condition}",
            "description": full_description + "\n\nLocal pickup or delivery available.",
            "price": price,
            "category": category,
            "format": "copy-paste",
        }

    if platform == "craigslist":
        return {
            "title": f"{name} ({condition}) - ${price:.0f}",
            "description": full_description + "\n\nCash only. No trades.",
            "price": price,
            "category": category,
            "format": "copy-paste",
        }

    if platform == "instagram":
        return {
            "caption": f"For sale: {name}\n\n{description}\n\n${price:.0f} \u2014 DM to claim!",
            "price": price,
            "hashtags": f"#forsale #{category.lower().replace(' ', '')} #{brand.lower().replace(' ', '') if brand else ''} #garagesale",
            "format": "copy-paste",
        }

    if platform == "x":
        tweet = f"For sale: {name} \u2014 ${price:.0f}\n{description[:100] if description else ''}"
        return {
            "text": tweet[:280],
            "price": price,
            "format": "copy-paste",
        }

    if platform == "shopify":
        return {
            "title": f"{brand} {name}".strip(),
            "description_html": f"<p>{description}</p><p>Condition: {condition}</p>",
            "price": price,
            "vendor": brand or "Garage Sale",
            "product_type": category,
            "format": "copy-paste",
        }

    if platform == "woocommerce":
        return {
            "name": f"{brand} {name}".strip(),
            "description": full_description,
            "regular_price": str(price),
            "categories": [{"name": category}],
            "format": "copy-paste",
        }

    if platform == "poshmark":
        return {
            "title": f"{brand} {name}".strip()[:50],
            "description": full_description + "\n\n#Poshmark #GarageSale",
            "price": price,
            "format": "copy-paste",
        }

    if platform == "mercari":
        return {
            "title": f"{name} {condition}",
            "description": full_description,
            "price": price,
            "format": "copy-paste",
        }

    return {"error": "Unknown platform", "format": "copy-paste"}


@app.get("/api/platforms")
def api_platforms():
    rows = get_platforms()
    result = []
    for row in rows:
        info = PLATFORM_INFO.get(row["platform"], {})
        result.append({
            "platform": row["platform"],
            "name": info.get("name", row["platform"]),
            "has_api": info.get("has_api", False),
            "auth_type": info.get("auth_type", "none"),
            "connected": bool(row.get("connected", 0)),
        })
    return {"platforms": result}


@app.post("/api/platforms/{platform}/connect")
def api_connect_platform(platform: str, credentials: str = Form("{}")):
    """Store platform auth credentials."""
    try:
        auth = json.loads(credentials)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON credentials")
    set_platform_auth(platform, auth, connected=True)
    return {"platform": platform, "connected": True}


@app.post("/api/items/{item_id}/listings")
def api_generate_listings(item_id: str, platforms: str = Form("[]")):
    """Generate listing text for selected platforms."""
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        platform_list = json.loads(platforms)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid platforms JSON")

    listings = {}
    for platform in platform_list:
        listings[platform] = _generate_listing_text(dict_to_item(item), platform)

    return {"item_id": item_id, "listings": listings}


@app.post("/api/batch/list")
def api_batch_list(item_ids: str = Form("[]"), platforms: str = Form("[]")):
    """Generate listings for multiple items across multiple platforms."""
    try:
        ids = json.loads(item_ids)
        platform_list = json.loads(platforms)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    results = []
    for item_id in ids:
        item = get_item(item_id)
        if not item:
            continue
        listings = {}
        for platform in platform_list:
            listings[platform] = _generate_listing_text(dict_to_item(item), platform)
        results.append({"item_id": item_id, "item_name": item.get("name"), "listings": listings})

    return {"batch": results, "count": len(results)}


# ───────────────────────────────────────────────────────────────
# Export
# ───────────────────────────────────────────────────────────────


@app.get("/api/export/csv")
def api_export_csv():
    """Export all items as CSV."""
    items = get_items(limit=10000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Brand", "Description", "Category", "Condition", "Price", "Suggested Price", "Status", "Platforms"])
    for item in items:
        writer.writerow([
            item["id"],
            item["name"],
            item["brand"],
            item["description"],
            item["category"],
            item["condition"],
            item["price"],
            item["suggested_price"],
            item["status"],
            item.get("platforms_json", "[]"),
        ])
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory.csv"},
    )


@app.get("/api/export/ebay")
def api_export_ebay():
    """Export items in eBay File Exchange format."""
    items = get_items(limit=10000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Action", "ItemID", "Title", "Description", "Category", "ConditionID", "StartPrice", "Quantity", "PicURL"])
    for item in items:
        writer.writerow([
            "Add",
            item["id"],
            item["name"],
            item["description"],
            item["category"],
            "3000" if item["condition"] == "New" else "4000",
            item["price"],
            "1",
            f"/uploads/{Path(item['image_path']).name}" if item.get("image_path") else "",
        ])
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ebay_upload.csv"},
    )


# ───────────────────────────────────────────────────────────────
# Static & Health
# ───────────────────────────────────────────────────────────────


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


# Serve uploaded images
@app.get("/uploads/{filename}")
def serve_upload(filename: str):
    path = UPLOAD_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)


# Mount static files last (so API routes take priority)
static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

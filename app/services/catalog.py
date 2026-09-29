from urllib.parse import quote_plus

CATALOG = {
    "home": [
        ("Lighting", "Warm LED floor lamp", 2499, "Amazon", "floor lamp home decor"),
        ("Seating", "Compact accent chair", 8999, "IKEA", "accent chair"),
        ("Storage", "Modular storage shelf", 5499, "IKEA", "modular storage shelf"),
        ("Decor", "Textured cushion set", 1299, "Flipkart", "decorative cushion covers set"),
        ("Lighting", "Pendant ceiling light", 3299, "Amazon", "pendant ceiling light"),
        ("Decor", "Framed botanical wall art", 1799, "Flipkart", "botanical wall art frames"),
        ("Dining", "Four-seat dining set", 18999, "IKEA", "4 seater dining table set"),
        ("Bedroom", "Cotton bedding set", 2999, "Amazon", "cotton bedsheet comforter set"),
    ],
    "party": [
        ("Food", "Buffet catering package (per guest)", 350, "Zomato", "party catering near me"),
        ("Food", "Snack and dessert spread", 220, "Swiggy", "party snacks catering"),
        ("Decor", "Balloon and backdrop kit", 2499, "Amazon", "birthday party balloon backdrop decoration"),
        ("Venue", "Community hall (estimated)", 12000, "Google Maps", "community hall event venue"),
        ("Entertainment", "Bluetooth speaker rental", 1800, "Amazon", "bluetooth speaker party"),
        ("Cake", "Celebration cake (per kg)", 900, "Zomato", "celebration cake order"),
        ("Decor", "Tableware set", 1199, "Flipkart", "disposable party plates cups set"),
    ],
    "jewelry": [
        ("Earrings", "Pearl drop earrings", 1499, "Amazon", "pearl drop earrings"),
        ("Necklace", "Minimal gold-tone pendant", 2199, "Flipkart", "gold tone pendant necklace"),
        ("Bracelet", "Delicate crystal bracelet", 999, "Amazon", "crystal bracelet women"),
        ("Earrings", "Statement oxidized jhumkas", 1299, "Flipkart", "oxidized silver jhumka earrings"),
        ("Necklace", "Layered festive necklace set", 3499, "Amazon", "layered festive necklace set"),
        ("Ring", "Adjustable stone ring", 799, "Flipkart", "adjustable stone ring"),
    ],
}


def search_url(platform: str, query: str) -> str:
    q = quote_plus(query)
    sites = {"Amazon": f"https://www.amazon.in/s?k={q}", "Flipkart": f"https://www.flipkart.com/search?q={q}",
             "IKEA": f"https://www.ikea.com/in/en/search/?q={q}", "Zomato": f"https://www.zomato.com/search?query={q}",
             "Swiggy": f"https://www.swiggy.com/search?query={q}", "Google Maps": f"https://www.google.com/maps/search/{q}"}
    return sites[platform]


def recommendations(planner: str, budget: float, guests: int = 1, limit: int = 5) -> list[dict]:
    candidates = CATALOG[planner]
    if planner == "party":
        candidates = [(cat, title, price * guests if "per guest" in title else price, platform, query)
                      for cat, title, price, platform, query in candidates]
    # Fit single items to the available budget, preferring useful lower-cost items.
    picks, remaining = [], budget
    for category, title, price, platform, query in sorted(candidates, key=lambda item: item[2]):
        if price <= remaining and len(picks) < limit:
            picks.append({"title": title, "category": category, "estimated_price": round(price, 2), "quantity": 1,
                          "platform": platform, "url": search_url(platform, query),
                          "reason": "A practical option selected to keep the plan within your budget."})
            remaining -= price
    return picks

"""
rehab_estimator.py — Granular room-by-room rehab cost estimator for real estate wholesalers.
No external dependencies.
"""

# ---------------------------------------------------------------------------
# Cost tables
# ---------------------------------------------------------------------------

ROOM_COSTS = {
    "roof": {
        "description": "Roof replacement (per sqft of roof surface)",
        "unit": "per_sqft",
        "low": 3,
        "mid": 5,
        "high": 8,
    },
    "foundation": {
        "description": "Foundation repair / stabilization",
        "unit": "flat",
        "low": 2000,
        "mid": 8000,
        "high": 25000,
    },
    "hvac": {
        "description": "HVAC full system replacement (furnace + AC)",
        "unit": "flat",
        "low": 4000,
        "mid": 7000,
        "high": 12000,
    },
    "electrical": {
        "description": "Full electrical rewire / panel upgrade",
        "unit": "flat",
        "low": 3000,
        "mid": 6000,
        "high": 12000,
    },
    "plumbing": {
        "description": "Full plumbing replacement / re-pipe",
        "unit": "flat",
        "low": 2500,
        "mid": 5000,
        "high": 10000,
    },
    "kitchen_basic": {
        "description": "Kitchen renovation — basic (paint, hardware, appliances)",
        "unit": "flat",
        "low": 3000,
        "mid": 8000,
        "high": 20000,
    },
    "kitchen_mid": {
        "description": "Kitchen renovation — mid-range (new cabinets, counters, appliances)",
        "unit": "flat",
        "low": 8000,
        "mid": 15000,
        "high": 35000,
    },
    "bathroom": {
        "description": "Bathroom renovation — basic (per bathroom)",
        "unit": "per_unit",
        "low": 2000,
        "mid": 5000,
        "high": 12000,
    },
    "flooring": {
        "description": "Flooring replacement (per sqft of living area)",
        "unit": "per_sqft",
        "low": 2,
        "mid": 5,
        "high": 12,
    },
    "paint_interior": {
        "description": "Interior painting (per sqft of living area)",
        "unit": "per_sqft",
        "low": 1,
        "mid": 2,
        "high": 4,
    },
    "paint_exterior": {
        "description": "Exterior painting (full house)",
        "unit": "flat",
        "low": 1500,
        "mid": 3500,
        "high": 7000,
    },
    "windows": {
        "description": "Window replacement (per window)",
        "unit": "per_unit",
        "low": 200,
        "mid": 450,
        "high": 900,
    },
    "doors": {
        "description": "Door replacement — interior or exterior (per door)",
        "unit": "per_unit",
        "low": 150,
        "mid": 350,
        "high": 800,
    },
    "landscaping": {
        "description": "Landscaping — basic cleanup and curb appeal",
        "unit": "flat",
        "low": 500,
        "mid": 2000,
        "high": 8000,
    },
    "demo_haul": {
        "description": "Demolition and debris haul-away",
        "unit": "flat",
        "low": 500,
        "mid": 1500,
        "high": 4000,
    },
    "permits": {
        "description": "Building permits",
        "unit": "flat",
        "low": 200,
        "mid": 800,
        "high": 2500,
    },
}

# ---------------------------------------------------------------------------
# Labor cost multipliers by region
# ---------------------------------------------------------------------------

LABOR_MULTIPLIERS = {
    "midwest": 1.0,
    "south": 0.95,
    "northeast": 1.35,
    "west": 1.45,
    "southeast": 1.05,
}

# ---------------------------------------------------------------------------
# Scope levels — what's included at each level
# ---------------------------------------------------------------------------

SCOPE_LEVELS = {
    "light": {
        "label": "Light / Cosmetic",
        "description": "Paint, flooring, cleaning, minor repairs only. No system work.",
        "includes": [
            "paint_interior",
            "flooring",
            "landscaping",
            "doors",
        ],
    },
    "medium": {
        "label": "Medium",
        "description": "Cosmetic + kitchen and bath updates + HVAC check/replace.",
        "includes": [
            "paint_interior",
            "paint_exterior",
            "flooring",
            "kitchen_basic",
            "bathroom",
            "hvac",
            "landscaping",
            "doors",
            "windows",
            "permits",
        ],
    },
    "heavy": {
        "label": "Heavy",
        "description": "Full systems (electric, plumbing, HVAC) + full cosmetic. May include foundation.",
        "includes": [
            "paint_interior",
            "paint_exterior",
            "flooring",
            "kitchen_mid",
            "bathroom",
            "hvac",
            "electrical",
            "plumbing",
            "roof",
            "landscaping",
            "doors",
            "windows",
            "demo_haul",
            "permits",
        ],
    },
    "gut": {
        "label": "Gut Rehab",
        "description": "Everything — structural, all systems, full interior rebuild.",
        "includes": [
            "foundation",
            "roof",
            "hvac",
            "electrical",
            "plumbing",
            "kitchen_mid",
            "bathroom",
            "flooring",
            "paint_interior",
            "paint_exterior",
            "windows",
            "doors",
            "landscaping",
            "demo_haul",
            "permits",
        ],
    },
}

# ---------------------------------------------------------------------------
# Core estimation functions
# ---------------------------------------------------------------------------


def _apply_multiplier(value, region):
    """Apply regional labor multiplier to a cost figure."""
    region = region.lower().strip()
    multiplier = LABOR_MULTIPLIERS.get(region, 1.0)
    return round(value * multiplier, 2)


def estimate_by_scope(sqft, scope, region="midwest", bedrooms=3, bathrooms=2):
    """
    Estimate rehab cost for a given scope level.

    Parameters
    ----------
    sqft        : int   — finished living area in square feet
    scope       : str   — one of: light, medium, heavy, gut
    region      : str   — one of: midwest, south, northeast, west, southeast
    bedrooms    : int   — number of bedrooms (used to estimate window/door count)
    bathrooms   : int   — number of bathrooms

    Returns
    -------
    dict with keys: scope, total_low, total_mid, total_high, line_items, recommendations
    """
    scope = scope.lower().strip()
    if scope not in SCOPE_LEVELS:
        raise ValueError(f"Invalid scope '{scope}'. Choose from: {list(SCOPE_LEVELS.keys())}")

    region = region.lower().strip()
    scope_data = SCOPE_LEVELS[scope]
    line_items = []
    total_low = 0
    total_mid = 0
    total_high = 0

    # Estimate window and door counts if not explicit
    estimated_windows = bedrooms * 2 + 4          # rough rule of thumb
    estimated_doors = bedrooms + bathrooms + 2    # interior + exterior

    # Roof sqft is roughly 1.15–1.2x the footprint; for a 1-story that's ~sqft
    # For 2-story it would be ~sqft/2. Use sqft as a conservative roof surface.
    roof_sqft = sqft

    for item_key in scope_data["includes"]:
        if item_key not in ROOM_COSTS:
            continue
        cost = ROOM_COSTS[item_key]
        unit = cost["unit"]

        if unit == "flat":
            qty = 1
            label = cost["description"]
        elif unit == "per_sqft":
            qty = sqft if item_key != "roof" else roof_sqft
            label = f"{cost['description']} ({qty:,} sqft)"
        elif unit == "per_unit":
            if item_key == "bathroom":
                qty = bathrooms
            elif item_key == "windows":
                qty = estimated_windows
            elif item_key == "doors":
                qty = estimated_doors
            else:
                qty = 1
            label = f"{cost['description']} x{qty}"
        else:
            qty = 1
            label = cost["description"]

        raw_low  = cost["low"]  * qty
        raw_mid  = cost["mid"]  * qty
        raw_high = cost["high"] * qty

        item_low  = _apply_multiplier(raw_low,  region)
        item_mid  = _apply_multiplier(raw_mid,  region)
        item_high = _apply_multiplier(raw_high, region)

        total_low  += item_low
        total_mid  += item_mid
        total_high += item_high

        line_items.append({
            "item": item_key,
            "label": label,
            "quantity": qty,
            "low":  item_low,
            "mid":  item_mid,
            "high": item_high,
        })

    recommendations = _build_recommendations(scope, sqft, region, bedrooms, bathrooms)

    return {
        "scope": scope_data["label"],
        "scope_key": scope,
        "sqft": sqft,
        "region": region,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "total_low":  round(total_low,  2),
        "total_mid":  round(total_mid,  2),
        "total_high": round(total_high, 2),
        "line_items": line_items,
        "recommendations": recommendations,
    }


def _build_recommendations(scope, sqft, region, bedrooms, bathrooms):
    tips = []
    if scope in ("heavy", "gut"):
        tips.append("Get a structural engineer inspection before finalizing your offer — foundation/roof issues can double your budget.")
        tips.append("Budget a 15–20% contingency on top of your high estimate for gut rehabs.")
    if region in ("northeast", "west"):
        tips.append(f"Labor in the {region} is 35–45% higher than Midwest baseline. Factor this into your MAO.")
    if sqft > 2000:
        tips.append("Large square footage amplifies per-sqft costs (flooring, paint). Get itemized contractor bids early.")
    if bathrooms >= 3:
        tips.append("Multiple bathroom renovations add up fast. Consider which baths truly need full updates vs. a clean and re-caulk.")
    tips.append("Always get at least 3 contractor bids before committing to a rehab budget.")
    tips.append("Material costs fluctuate — lock in lumber and drywall prices if you're not starting within 30 days.")
    return tips


def estimate_room_by_room(rooms_dict):
    """
    Estimate costs from a room-by-room specification dict.

    rooms_dict format:
    {
        "roof":      {"include": True, "sqft": 1200},
        "kitchen":   {"include": True, "level": "mid"},      # level: basic | mid
        "bathroom":  {"include": True, "count": 2},
        "flooring":  {"include": True, "sqft": 1400},
        "hvac":      {"include": True},
        "electrical":{"include": False},
        "windows":   {"include": True, "count": 10},
        "doors":     {"include": True, "count": 8},
        "paint_interior": {"include": True, "sqft": 1400},
        "paint_exterior": {"include": True},
        "plumbing":  {"include": False},
        "foundation":{"include": False},
        "landscaping":{"include": True},
        "demo_haul": {"include": True},
        "permits":   {"include": True},
    }

    Returns
    -------
    dict with keys: total_low, total_mid, total_high, line_items
    """
    line_items = []
    total_low = 0
    total_mid = 0
    total_high = 0

    for room_key, config in rooms_dict.items():
        if not config.get("include", False):
            continue

        # Normalize kitchen key based on level
        if room_key == "kitchen":
            level = config.get("level", "basic").lower()
            lookup_key = "kitchen_mid" if level in ("mid", "mid-range", "midrange") else "kitchen_basic"
        else:
            lookup_key = room_key

        if lookup_key not in ROOM_COSTS:
            continue

        cost = ROOM_COSTS[lookup_key]
        unit = cost["unit"]

        if unit == "flat":
            qty = config.get("count", 1)
        elif unit == "per_sqft":
            qty = config.get("sqft", 0)
        elif unit == "per_unit":
            qty = config.get("count", 1)
        else:
            qty = 1

        if qty <= 0:
            continue

        item_low  = round(cost["low"]  * qty, 2)
        item_mid  = round(cost["mid"]  * qty, 2)
        item_high = round(cost["high"] * qty, 2)

        total_low  += item_low
        total_mid  += item_mid
        total_high += item_high

        label = f"{cost['description']}"
        if unit == "per_sqft":
            label += f" ({qty:,} sqft)"
        elif unit == "per_unit" and qty > 1:
            label += f" x{qty}"

        line_items.append({
            "item": lookup_key,
            "label": label,
            "quantity": qty,
            "low":  item_low,
            "mid":  item_mid,
            "high": item_high,
        })

    return {
        "total_low":  round(total_low,  2),
        "total_mid":  round(total_mid,  2),
        "total_high": round(total_high, 2),
        "line_items": line_items,
    }


def get_contractor_tips():
    """
    Return a list of contractor management tips for real estate investors.
    """
    return [
        "Always get at least 3 bids — the spread between the cheapest and most expensive is often 40–60%. The middle bid is usually the safest.",
        "Never pay more than 50% of materials upfront, and only after materials are on-site.",
        "Never pay 100% upfront — structure payments as: 30% start, 40% at midpoint inspection, 30% on final walkthrough.",
        "Require a signed lien waiver before issuing each progress payment so subcontractors can't lien your property.",
        "Get a written scope of work (SOW) before signing any contract — 'I'll take care of it' is not a scope.",
        "Specify all materials by brand and SKU in the contract if possible — 'builder grade' is vague.",
        "Build a 10–15% contingency buffer into your budget for surprises, especially on older homes.",
        "Visit the job site at least twice a week — contractors work faster and more carefully when the owner shows up.",
        "Take date-stamped photos before, during, and after every phase for insurance, lender draws, and disputes.",
        "Check contractor licenses and insurance (general liability + workers comp) before signing — call the carrier to verify.",
        "A fast contractor is worth more than a cheap one on a flip — holding costs compound every month.",
        "Use a draw schedule tied to inspected milestones, not calendar dates.",
        "Get references from other investors, not just homeowners — investors know if a contractor stays on budget.",
        "Avoid contractors who won't pull permits — unpermitted work can kill your resale or title.",
        "For large jobs, consider a construction manager or GC — the markup is often worth it for coordination.",
    ]


def get_rehab_checklist(scope):
    """
    Return an ordered list of rehab steps for a given scope level.

    Parameters
    ----------
    scope : str — one of: light, medium, heavy, gut

    Returns
    -------
    list of str — ordered steps
    """
    scope = scope.lower().strip()

    base_order = [
        "1. Secure the property — change locks, board windows if vacant",
        "2. Pull all required permits before any work begins",
        "3. Complete full demo and debris haul-out",
        "4. Address any structural or foundation issues first",
        "5. Rough-in plumbing (if replacing pipes)",
        "6. Rough-in electrical (if rewiring)",
        "7. HVAC rough-in / ductwork",
        "8. Insulation",
        "9. Drywall hang and finish",
        "10. Prime all walls",
        "11. Install windows and exterior doors",
        "12. Roofing (if replacing)",
        "13. Exterior paint / siding",
        "14. Flooring rough prep (subfloor leveling, cement board in baths)",
        "15. Tile work — bathrooms and kitchen backsplash",
        "16. Cabinet installation — kitchen and baths",
        "17. Countertop installation",
        "18. Interior doors and trim / baseboards",
        "19. Interior paint (walls, ceilings, trim)",
        "20. Finish plumbing — fixtures, toilets, sinks",
        "21. Finish electrical — outlets, switches, fixtures, panel labels",
        "22. HVAC finish — registers, thermostats, test system",
        "23. Flooring installation (hardwood, LVP, carpet last)",
        "24. Appliance installation",
        "25. Hardware — cabinet pulls, door knobs, towel bars",
        "26. Final punch-list walk — caulking, touch-up paint, repairs",
        "27. Deep clean",
        "28. Landscaping and curb appeal",
        "29. Final permit inspections and certificate of occupancy (if required)",
        "30. Professional photography for listing or buyer showings",
    ]

    light_order = [
        "1. Secure the property — change locks",
        "2. Deep clean entire property",
        "3. Demo — remove any damaged drywall, old carpet, debris",
        "4. Minor repairs — patch drywall, fix doors, tighten fixtures",
        "5. Paint interior — walls, ceilings, trim",
        "6. Install new flooring (LVP or carpet)",
        "7. Update lighting fixtures and switch plates",
        "8. Paint exterior if needed",
        "9. Landscaping and curb appeal cleanup",
        "10. Final walkthrough and punch-list",
    ]

    medium_order = [
        "1. Secure the property — change locks, inspect systems",
        "2. Pull permits for any system work",
        "3. Demo — remove old cabinets, flooring, fixtures",
        "4. HVAC inspection and replacement if needed",
        "5. Electrical panel check — replace breakers, add GFCI where required",
        "6. Plumbing inspection — fix leaks, replace valves",
        "7. Drywall repair",
        "8. Prime all surfaces",
        "9. Kitchen cabinet and countertop installation",
        "10. Bathroom tile and fixture replacement",
        "11. Interior paint",
        "12. Flooring installation",
        "13. Window and door replacements",
        "14. Exterior paint",
        "15. Appliance installation",
        "16. Hardware and finishing details",
        "17. Landscaping",
        "18. Final inspections and punch-list",
    ]

    if scope == "light":
        return light_order
    elif scope == "medium":
        return medium_order
    elif scope in ("heavy", "gut"):
        return base_order
    else:
        raise ValueError(f"Invalid scope '{scope}'. Choose from: light, medium, heavy, gut")


def estimate_flip_profit(purchase, arv, repairs_mid, wholesale_fee=0, holding_months=4):
    """
    Estimate net profit and ROI for a fix-and-flip deal.

    Parameters
    ----------
    purchase       : float — purchase price
    arv            : float — after-repair value
    repairs_mid    : float — mid-range repair estimate
    wholesale_fee  : float — assignment fee paid to wholesaler (default 0)
    holding_months : int   — months you'll hold the property

    Returns
    -------
    dict with: purchase, arv, repairs, holding_costs, closing_costs,
               net_profit, roi_pct, wholesale_fee, is_deal
    """
    # Holding costs: insurance, utilities, taxes, loan interest
    # Rule of thumb: ~1% of purchase per month
    monthly_holding_rate = 0.01
    holding_costs = round(purchase * monthly_holding_rate * holding_months, 2)

    # Closing costs: buy-side + sell-side (agent, title, transfer tax)
    # Buy-side: ~1.5%, sell-side: ~8% (6% agent + 2% closing)
    buy_closing  = round(purchase * 0.015, 2)
    sell_closing = round(arv * 0.08,  2)
    total_closing = round(buy_closing + sell_closing, 2)

    total_costs = purchase + repairs_mid + wholesale_fee + holding_costs + total_closing
    net_profit  = round(arv - total_costs, 2)
    roi_pct     = round((net_profit / total_costs) * 100, 2) if total_costs > 0 else 0.0

    # Deal criteria: 70% rule and positive profit
    seventy_rule_max = round(arv * 0.70 - repairs_mid, 2)
    is_deal = net_profit > 0 and purchase <= seventy_rule_max

    return {
        "purchase":        purchase,
        "wholesale_fee":   wholesale_fee,
        "arv":             arv,
        "repairs_mid":     repairs_mid,
        "holding_costs":   holding_costs,
        "holding_months":  holding_months,
        "buy_closing":     buy_closing,
        "sell_closing":    sell_closing,
        "total_closing":   total_closing,
        "total_costs":     round(total_costs, 2),
        "net_profit":      net_profit,
        "roi_pct":         roi_pct,
        "seventy_rule_max": seventy_rule_max,
        "is_deal":         is_deal,
        "deal_summary":    "DEAL — meets 70% rule and positive ROI" if is_deal else "NO DEAL — does not meet 70% rule or profit threshold",
    }

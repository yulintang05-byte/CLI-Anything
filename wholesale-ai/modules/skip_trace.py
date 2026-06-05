"""
Skip Trace — Find the owner behind any address.

Free methods first (county records, USPS lookup, voter rolls).
Paid options for when speed matters (BatchSkipTracing, SkipGenie, REISkip).

The moment a lead comes in, this tells you:
  - Whether the owner is absentee (not living there) → higher motivation
  - How to find their name, phone, email
  - Which services can find them in minutes
"""
import os
from typing import Optional
from pathlib import Path


# ── Free + paid skip trace services ──────────────────────────────────────────

SKIP_TRACE_SERVICES = {
    "BatchSkipTracing": {
        "url":       "https://batchskiptracing.com/",
        "cost":      "$0.17–$0.26/record (bulk pricing)",
        "speed":     "Instant",
        "data":      "Phone, email, relatives, address history",
        "best_for":  "Bulk lists — upload your tax delinquent list and get phones in seconds",
        "free_trial": True,
        "note":      "Used by 90% of professional wholesalers. Best data quality.",
    },
    "SkipGenie": {
        "url":       "https://www.skipgenie.com/",
        "cost":      "$0.10–$0.15/record",
        "speed":     "Instant",
        "data":      "Phone numbers, email, age, relatives",
        "best_for":  "Single lookups — pay per search",
        "free_trial": True,
        "note":      "Cheap and fast for single-property skip tracing.",
    },
    "REISkip": {
        "url":       "https://www.reiskip.com/",
        "cost":      "$0.12–$0.20/record",
        "speed":     "Instant",
        "data":      "Phone (verified), email, property history",
        "best_for":  "Investors — built specifically for real estate skip tracing",
        "free_trial": True,
        "note":      "Pulls verified mobile numbers, not just landlines.",
    },
    "PropStream Skip Trace": {
        "url":       "https://www.propstream.com/",
        "cost":      "$0.12/record (add-on to PropStream sub)",
        "speed":     "Instant",
        "data":      "Phone, email + property data in one platform",
        "best_for":  "Already PropStream subscribers — all-in-one",
        "free_trial": False,
        "note":      "Best value if you already pay for PropStream.",
    },
    "TLO / TransUnion": {
        "url":       "https://www.tlo.com/",
        "cost":      "Varies (~$1/record)",
        "speed":     "Instant",
        "data":      "Comprehensive — SSN verification, full history",
        "best_for":  "Professional investigators, licensed PIs only",
        "free_trial": False,
        "note":      "Requires business license. Most complete data.",
    },
    "BeenVerified": {
        "url":       "https://www.beenverified.com/",
        "cost":      "$26/mo unlimited",
        "speed":     "Instant",
        "data":      "Phone, email, address history, relatives, social",
        "best_for":  "Getting started — no per-search cost",
        "free_trial": True,
        "note":      "Not as deep as BatchSkipTracing but great for beginners.",
    },
    "Whitepages Pro": {
        "url":       "https://pro.whitepages.com/",
        "cost":      "$49–$199/mo",
        "speed":     "Instant",
        "data":      "Phone, address history, identity verification",
        "best_for":  "Business users needing identity verification",
        "free_trial": False,
        "note":      "",
    },
}

FREE_SKIP_TRACE_METHODS = {
    "County Assessor": {
        "description": "Every county has a public property records search. Owner name and mailing address are always there.",
        "url":         "https://publicrecords.netronline.com/",
        "how":         "Go to NETR, find your county, search the property address → owner name + mailing address appears.",
        "time":        "5 minutes",
        "what_you_get": "Owner name, mailing address (where to send mail if they're absentee)",
    },
    "USPS NCOALink via Google": {
        "description": "Search '[Owner Name] [City] [State]' to find social profiles or business listings.",
        "how":         "Take the owner name from county records → Google → LinkedIn → Facebook → find contact.",
        "time":        "10 minutes",
        "what_you_get": "Phone, email, social media — if they have any public presence.",
    },
    "Voter Registration": {
        "description": "In most states, voter roll data is public — includes name, address, DOB.",
        "how":         "Search '[State] voter registration lookup public records' — many states have free search portals.",
        "time":        "15 minutes",
        "what_you_get": "Owner phone (some states include it), confirmed mailing address.",
    },
    "LinkedIn": {
        "description": "If the owner has a professional presence, LinkedIn often has their contact info or employer.",
        "how":         "Search '[Owner Name] [City]' on LinkedIn. Connect and message or find company email pattern.",
        "time":        "10–15 minutes",
        "what_you_get": "Professional email, employer, sometimes direct line.",
    },
    "Facebook": {
        "description": "Most people (especially older homeowners) have Facebook. Name + city search often finds them.",
        "how":         "Search '[Owner Name]' on Facebook, filter by city → Message directly.",
        "time":        "5–10 minutes",
        "what_you_get": "Direct message contact — no spam filters.",
    },
    "411.com / AnyWho": {
        "description": "Free phone directory. Works best for landlines and older owners.",
        "url":         "https://www.411.com/",
        "how":         "Enter name + city → returns phone listing if found.",
        "time":        "2 minutes",
        "what_you_get": "Phone number if they're listed (landline).",
    },
    "Google Street View": {
        "description": "Verify occupancy — is the property owner-occupied or vacant?",
        "how":         "Pull up address on Google Maps → Street View → look for mail piled up, no curtains, overgrown, etc.",
        "time":        "2 minutes",
        "what_you_get": "Vacancy/occupancy signal. Vacant = higher motivation.",
    },
    "Zillow / Redfin Owner Info": {
        "description": "Sometimes listing agent or owner info appears in listing history.",
        "url":         "https://www.zillow.com/",
        "how":         "Search the address on Zillow → look at listing history → may show agent who listed in the past.",
        "time":        "5 minutes",
        "what_you_get": "Prior listing agent (they know the owner) or owner info.",
    },
}

ABSENTEE_OWNER_SIGNALS = [
    ("Different mailing address", "Owner's tax bill goes to a different address than the property — they don't live there."),
    ("LLC / Trust ownership", "When a company owns it, it's almost always a rental or investment property."),
    ("No homestead exemption", "Owners who live in the property claim homestead exemption. No exemption = not their primary home."),
    ("Long ownership with no refi", "Owned 15+ years with no mortgage recorded = likely free and clear = open to creative terms."),
    ("Property in rough shape", "Street view shows deferred maintenance = absentee landlord who's tired of the property."),
    ("Multiple properties", "Same owner shows up on multiple parcels = investor who might sell one."),
    ("Out-of-state owner", "Mailing address in a different state = absentee = strong motivation to sell."),
    ("Recent inheritance", "Owner acquired via deed with 'Personal Representative' = inherited = often motivated."),
]


def get_lookup_links(address: str, city: str, state: str, zip_code: str = "") -> dict:
    """
    Build a complete set of skip trace research links for a specific property.
    No API needed — all public records.
    """
    state_lower = state.lower()
    city_slug   = city.lower().replace(" ", "-")
    addr_enc    = address.replace(" ", "+")

    return {
        "County Records (NETR)": f"https://publicrecords.netronline.com/{state_lower}/",
        "Google Owner Search":   f"https://www.google.com/search?q={addr_enc}+{city_slug}+{state_lower}+owner",
        "Zillow Listing":        f"https://www.zillow.com/homes/{addr_enc.replace('+','_')}_{state.upper()}_rb/",
        "Redfin":                f"https://www.redfin.com/city/{city_slug}/{state.upper()}",
        "Whitepages":            f"https://www.whitepages.com/address/{addr_enc.replace('+','_')}/{city_slug}-{state.upper()}-{zip_code}",
        "411.com":               "https://www.411.com/",
        "BatchSkipTracing":      "https://batchskiptracing.com/",
        "SkipGenie":             "https://www.skipgenie.com/",
        "REISkip":               "https://www.reiskip.com/",
    }


def absentee_check_from_lead(lead: dict) -> dict:
    """
    Use available lead data to estimate absentee owner likelihood.
    Integrates with RentCast lead data.
    """
    signals = []
    confidence = "unknown"

    dom = lead.get("days_on_market", 0) or 0
    distress = lead.get("distress_signals", [])
    source = lead.get("source", "").lower()

    if dom >= 90:
        signals.append(f"On market {dom} days — likely unmotivated or absentee")
    if "estate sale" in " ".join(distress).lower() or "probate" in " ".join(distress).lower():
        signals.append("Probate/estate sale — often absentee heirs with no attachment to property")
    if "as-is" in " ".join(distress).lower() or "as is" in " ".join(distress).lower():
        signals.append("Listed as-is — typical of absentee/investor seller")
    if "price reduced" in distress:
        signals.append("Price cut — seller getting eager")
    if "investor special" in " ".join(distress).lower() or "handyman" in " ".join(distress).lower():
        signals.append("Marketed to investors — already knows it won't sell retail")

    if len(signals) >= 3:
        confidence = "HIGH — classic absentee/motivated seller profile"
    elif len(signals) >= 1:
        confidence = "MEDIUM — check county records to confirm"
    else:
        confidence = "LOW — looks like owner-occupied, dig deeper"

    return {
        "signals":    signals,
        "confidence": confidence,
        "action":     (
            "Skip trace NOW — this is your hottest lead."
            if "HIGH" in confidence else
            "Pull county records first, confirm absentee status."
            if "MEDIUM" in confidence else
            "Worth verifying occupancy via Street View and county records."
        ),
    }


def get_motivated_lead_sources() -> dict:
    """
    Free public record sources for pre-motivated seller lists.
    These are the gold-mine lists every top wholesaler works from.
    """
    return {
        "Tax Delinquent List": {
            "description": "Owners behind on property taxes — county will auction if unpaid. Extreme motivation.",
            "how_to_get":  "Call or visit your county tax assessor's office. Ask for 'delinquent tax roll'. Many counties publish it online.",
            "motivation":  "10/10 — they NEED to sell or lose the property",
            "free":        True,
        },
        "Pre-Foreclosure (NOD/Lis Pendens)": {
            "description": "Owners who've been served a Notice of Default or Lis Pendens — foreclosure is filed.",
            "how_to_get":  "LPS Desktop/Auction.com OR county courthouse recorder. Search 'lis pendens [county]'.",
            "motivation":  "9/10 — they have a deadline and face credit destruction",
            "free":        "Free at courthouse, ~$50/mo tools like ATTOM",
        },
        "Probate (Estate Filings)": {
            "description": "Someone died, heirs now own property. Heirs often want cash fast — no emotional attachment.",
            "how_to_get":  "County probate court records. Search 'real property' in estate filings. Call the estate attorney.",
            "motivation":  "8/10 — heirs usually want cash, not a house in another city",
            "free":        True,
        },
        "Absentee Owners": {
            "description": "Owners whose mailing address differs from property address — they don't live there.",
            "how_to_get":  "County assessor export. BatchLeads, PropStream filter. BatchSkipTracing bulk lookup.",
            "motivation":  "7/10 — tired landlords, out-of-state owners, rental problems",
            "free":        "Free from county, $50–$100/mo for batch tools",
        },
        "Vacant Properties (USPS Vacancy)": {
            "description": "USPS marks addresses as vacant when mail is returned. These are the distressed properties.",
            "how_to_get":  "BatchLeads has USPS vacancy filter. County code enforcement sometimes publishes lists.",
            "motivation":  "8/10 — vacant = carrying costs with zero income",
            "free":        "$49/mo BatchLeads tier includes USPS vacancy data",
        },
        "High Equity + Long Ownership": {
            "description": "Owners who've had the property 15+ years and own it free & clear — open to seller finance.",
            "how_to_get":  "PropStream or BatchLeads filter: equity > 80%, ownership > 10 years.",
            "motivation":  "6/10 — less desperate but open to creative terms",
            "free":        "Requires PropStream ($99/mo) or similar",
        },
        "Driving for Dollars (D4D)": {
            "description": "You physically drive neighborhoods looking for distressed properties — boarded up, overgrown, tarps on roof.",
            "how_to_get":  "Use DealMachine or BatchLeads app — take photo, instantly get owner info.",
            "motivation":  "Varies — but you're targeting properties that are clearly problems",
            "free":        "Time investment only. DealMachine app $49/mo automates skip trace.",
        },
        "Code Violations": {
            "description": "City code enforcement lists — properties with unpaid violations are often absentee/distressed.",
            "how_to_get":  "City or county website. Search '[city] code enforcement violations list'. Many cities publish it.",
            "motivation":  "7/10 — owner has a problem they want to make go away",
            "free":        True,
        },
    }

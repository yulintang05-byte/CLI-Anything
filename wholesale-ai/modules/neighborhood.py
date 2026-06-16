"""
Neighborhood & Property Intelligence — crime data, school ratings, walk score,
tax records, and insurance estimates.

Free data sources:
- FBI Crime Data Explorer API (api.usa.gov/crime/fbi) — free, no auth
- GreatSchools.org — school ratings (requires free key)
- Walk Score API — walkability (requires free key at walkscore.com)
- NETR Online — county public records portal
- Various county assessor lookups
"""
import httpx
import os
from typing import Optional


FBI_API_BASE = "https://api.usa.gov/crime/fbi/cde"
FBI_API_KEY = os.getenv("FBI_API_KEY", "iiHnOKfno2Mgkt5AynpvPpUQTEyxE27fo1zklp")  # Public demo key


# ── Crime Data ────────────────────────────────────────────────────────────────

def get_city_crime_data(city: str, state: str) -> dict:
    """
    Fetch crime stats for a city from the FBI Crime Data Explorer.
    Returns violent crime, property crime, and a safety score.
    """
    try:
        with httpx.Client(timeout=15) as client:
            # Agency list for the city
            agency_url = f"{FBI_API_BASE}/agency/byStateAbbr/{state.upper()}?API_KEY={FBI_API_KEY}"
            r = client.get(agency_url)
            if r.status_code != 200:
                return _crime_fallback(city, state)

            agencies = r.json().get("results", [])
            # Find the city's agency
            city_lower = city.lower()
            match = None
            for agency in agencies:
                name = agency.get("agency_name", "").lower()
                if city_lower in name and "police" in name:
                    match = agency
                    break

            if not match:
                return _crime_fallback(city, state)

            ori = match.get("ori")
            if not ori:
                return _crime_fallback(city, state)

            # Get crime counts for the agency
            crime_url = f"{FBI_API_BASE}/summarized/agency/{ori}/offenses/2022/2022?API_KEY={FBI_API_KEY}"
            cr = client.get(crime_url)
            if cr.status_code != 200:
                return _crime_fallback(city, state)

            crime_data = cr.json().get("results", [])

            violent = 0
            property_crime = 0
            population = match.get("population", [{}])
            pop = population[0].get("population", 1) if population else 1

            violent_types = {"aggravated-assault", "robbery", "rape", "murder"}
            property_types = {"burglary", "larceny", "motor-vehicle-theft", "arson"}

            for record in crime_data:
                offense = record.get("offense", "").lower().replace(" ", "-")
                count = record.get("actual", 0) or 0
                if offense in violent_types:
                    violent += count
                elif offense in property_types:
                    property_crime += count

            if pop > 0:
                violent_rate = (violent / pop) * 100000
                property_rate = (property_crime / pop) * 100000
            else:
                violent_rate = property_rate = 0

            # Score: lower crime rate = higher score (0-100)
            # National avg violent rate ~380/100k, property ~2,100/100k
            safety_score = _calc_safety_score(violent_rate, property_rate)

            return {
                "city": city,
                "state": state.upper(),
                "violent_crimes": violent,
                "property_crimes": property_crime,
                "violent_rate_per_100k": round(violent_rate, 1),
                "property_rate_per_100k": round(property_rate, 1),
                "safety_score": safety_score,
                "safety_grade": _score_to_grade(safety_score),
                "population": pop,
                "source": "FBI Crime Data Explorer",
                "source_url": "https://cde.ucr.cjis.gov/",
                "note": "2022 data — most recent available in FBI CDE",
            }

    except Exception as e:
        return _crime_fallback(city, state, str(e))


def _calc_safety_score(violent_rate: float, property_rate: float) -> int:
    """
    Calculate a 0-100 safety score.
    Based on FBI national averages: violent ~380, property ~2,100 per 100k.
    """
    v_score = max(0, 100 - (violent_rate / 10))    # 1000+ violent = 0
    p_score = max(0, 100 - (property_rate / 50))   # 5000+ property = 0
    return round((v_score * 0.6 + p_score * 0.4))


def _score_to_grade(score: int) -> str:
    if score >= 80:
        return "A"
    elif score >= 65:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 35:
        return "D"
    return "F"


def _crime_fallback(city: str, state: str, error: str = "") -> dict:
    """Return guidance when API data isn't available."""
    return {
        "city": city,
        "state": state.upper(),
        "error": error or "City not found in FBI database",
        "manual_lookup": {
            "FBI Crime Explorer": f"https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/explorer/crime/crime-trend",
            "NeighborhoodScout": f"https://www.neighborhoodscout.com/{state.lower()}/{city.lower().replace(' ', '-')}/crime",
            "SpotCrime": f"https://spotcrime.com/crime-map/{city.lower().replace(' ', '-')},{state.lower()}",
            "CityProtect": f"https://cityprotect.com/",
            "CrimeMapping": f"https://www.crimemapping.com/",
            "AreaVibes": f"https://www.areavibes.com/{city.lower().replace(' ', '-')}-{state.lower()}/crime/",
        },
    }


def get_state_crime_comparison(state: str) -> dict:
    """Get state-level crime summary vs national average."""
    try:
        with httpx.Client(timeout=15) as client:
            url = f"{FBI_API_BASE}/summarized/state/{state.upper()}/all-offenses/2022/2022?API_KEY={FBI_API_KEY}"
            r = client.get(url)
            if r.status_code == 200:
                data = r.json()
                return {
                    "state": state.upper(),
                    "data": data.get("results", []),
                    "source": "FBI CDE",
                }
    except Exception:
        pass
    return {
        "state": state.upper(),
        "lookup_url": f"https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/explorer/crime/crime-trend",
    }


# ── Neighborhood Resources ────────────────────────────────────────────────────

def get_neighborhood_links(address: str, city: str, state: str, zip_code: str = "") -> dict:
    """
    Build links to all free neighborhood research tools.
    These are the same data sources Tranchi.ai uses under the hood.
    """
    city_slug = city.lower().replace(" ", "-")
    state_lower = state.lower()
    zip_part = zip_code or f"{city_slug}-{state_lower}"

    return {
        "Crime & Safety": {
            "SpotCrime (Live Crime Map)": f"https://spotcrime.com/crime-map/{city_slug},{state_lower}",
            "AreaVibes Crime Score": f"https://www.areavibes.com/{city_slug}-{state_lower}/crime/",
            "NeighborhoodScout": f"https://www.neighborhoodscout.com/{state_lower}/{city_slug}/crime",
            "CrimeMapping": "https://www.crimemapping.com/",
            "FBI Crime Data": "https://cde.ucr.cjis.gov/",
        },
        "Schools": {
            "GreatSchools": f"https://www.greatschools.org/search/search.page?q={zip_code or city_slug}&state={state.upper()}",
            "Niche School Rankings": f"https://www.niche.com/k12/search/best-schools/t/zip-code/{zip_code}/",
            "SchoolDigger": f"https://www.schooldigger.com/go/XX/schools/search.aspx?q={zip_code}",
        },
        "Walkability / Transit": {
            "Walk Score": f"https://www.walkscore.com/score/loc/lat=0/lng=0/?q={city_slug}+{state.upper()}",
            "Transit Score": f"https://www.walkscore.com/transit/{city_slug}/{state_lower}/",
        },
        "Flood / Environmental": {
            "FEMA Flood Map": f"https://msc.fema.gov/portal/search?AddressQuery={zip_code or city}",
            "EPA EnviroMapper": f"https://enviro.epa.gov/envirofacts/multisystem/search?query={zip_code}",
            "Climate Risk (First Street)": f"https://firststreet.org/",
        },
        "Property & Tax Records": {
            "NETR Online County Records": f"https://publicrecords.netronline.com/{state_lower}/",
            "County Assessor Search": f"https://publicrecords.netronline.com/{state_lower}/",
            "PropStream (Property Intel)": "https://propstream.com/",
            "BeenVerified Property": "https://www.beenverified.com/property/",
        },
        "Neighborhood Data": {
            "AreaVibes Livability": f"https://www.areavibes.com/{city_slug}-{state_lower}/",
            "City-Data.com": f"https://www.city-data.com/city/{city.replace(' ', '-')}-{state.title()}.html",
            "Sperling's Best Places": f"https://www.bestplaces.net/city/state/{state_lower}/{city_slug}",
            "Data USA": f"https://datausa.io/profile/geo/{city_slug}-{state_lower}",
        },
    }


# ── Property Tax & Insurance Estimates ───────────────────────────────────────

def estimate_property_tax(state: str, assessed_value: float) -> dict:
    """
    Estimate annual property taxes by state using median effective tax rates.
    Source: Tax Foundation state property tax data.
    """
    # Median effective property tax rates by state (2024 estimates)
    state_rates = {
        "AL": 0.0040, "AK": 0.0099, "AZ": 0.0062, "AR": 0.0061,
        "CA": 0.0075, "CO": 0.0049, "CT": 0.0173, "DE": 0.0056,
        "FL": 0.0083, "GA": 0.0092, "HI": 0.0028, "ID": 0.0063,
        "IL": 0.0205, "IN": 0.0085, "IA": 0.0150, "KS": 0.0130,
        "KY": 0.0086, "LA": 0.0055, "ME": 0.0109, "MD": 0.0099,
        "MA": 0.0114, "MI": 0.0140, "MN": 0.0113, "MS": 0.0065,
        "MO": 0.0096, "MT": 0.0084, "NE": 0.0155, "NV": 0.0053,
        "NH": 0.0186, "NJ": 0.0215, "NM": 0.0079, "NY": 0.0145,
        "NC": 0.0077, "ND": 0.0088, "OH": 0.0148, "OK": 0.0090,
        "OR": 0.0093, "PA": 0.0153, "RI": 0.0134, "SC": 0.0057,
        "SD": 0.0117, "TN": 0.0062, "TX": 0.0160, "UT": 0.0057,
        "VT": 0.0182, "VA": 0.0082, "WA": 0.0093, "WV": 0.0058,
        "WI": 0.0169, "WY": 0.0057, "DC": 0.0056,
    }

    state_upper = state.upper()
    rate = state_rates.get(state_upper, 0.0110)  # Default 1.1% if state unknown
    annual_tax = assessed_value * rate
    monthly_tax = annual_tax / 12

    return {
        "state": state_upper,
        "assessed_value": assessed_value,
        "effective_rate": rate,
        "effective_rate_pct": f"{rate * 100:.2f}%",
        "annual_estimate": round(annual_tax, 0),
        "monthly_estimate": round(monthly_tax, 0),
        "note": "Estimate based on state median rate — actual varies by county/city",
        "lookup_url": f"https://publicrecords.netronline.com/{state.lower()}/",
    }


def estimate_insurance(property_value: float, state: str, property_type: str = "sfr") -> dict:
    """
    Estimate annual homeowners/landlord insurance.
    Landlord insurance typically runs 15-25% more than homeowners.
    """
    # Average annual premiums by state (approximate, 2024)
    state_premiums = {
        "OK": 4200, "KS": 3800, "NE": 3500, "TX": 3400, "CO": 3200,
        "SD": 3000, "AR": 2900, "MS": 2800, "LA": 2700, "AL": 2600,
        "MO": 2500, "FL": 2400, "MN": 2200, "IA": 2100, "GA": 1900,
        "TN": 1800, "NC": 1700, "SC": 1600, "IN": 1500, "IL": 1500,
        "OH": 1400, "MI": 1400, "PA": 1300, "VA": 1200, "MD": 1200,
        "NJ": 1200, "NY": 1300, "MA": 1400, "CT": 1400, "CA": 1300,
        "WA": 1000, "OR": 1000, "ID": 900, "UT": 900, "AZ": 1100,
        "NV": 900, "NM": 1000, "WY": 1000, "MT": 1100, "ND": 1400,
        "HI": 500, "AK": 1200, "DC": 1100, "DE": 1000, "RI": 1400,
        "VT": 900, "NH": 1000, "ME": 1100, "WV": 1300, "KY": 1800,
    }

    state_upper = state.upper()
    base_premium = state_premiums.get(state_upper, 1400)

    # Adjust for property value (higher value = higher premium)
    value_factor = min(2.0, max(0.5, property_value / 200000))
    adjusted_premium = base_premium * value_factor

    # Landlord policy is ~25% more
    landlord_premium = adjusted_premium * 1.25

    return {
        "state": state_upper,
        "property_value": property_value,
        "homeowner_annual": round(adjusted_premium, 0),
        "homeowner_monthly": round(adjusted_premium / 12, 0),
        "landlord_annual": round(landlord_premium, 0),
        "landlord_monthly": round(landlord_premium / 12, 0),
        "note": "Estimates only — get real quotes from multiple insurers before closing",
        "quote_sources": [
            "https://www.policygenius.com/homeowners-insurance/",
            "https://www.progressive.com/homeowners/",
            "https://www.statefarm.com/",
        ],
    }


def get_property_records_urls(address: str, city: str, state: str, zip_code: str = "") -> dict:
    """Links to pull actual property tax records and ownership history."""
    state_lower = state.lower()
    state_upper = state.upper()
    city_slug = city.lower().replace(" ", "-")

    return {
        "County Records (NETR)": f"https://publicrecords.netronline.com/{state_lower}/",
        "Property Records Search": f"https://www.propertyshark.com/mason/api/comps/",
        "County Assessor": f"https://publicrecords.netronline.com/{state_lower}/",
        "Tax Records": f"https://publicrecords.netronline.com/{state_lower}/",
        "Ownership History": f"https://www.titleflex.com/",
        "Deed History": f"https://publicrecords.netronline.com/{state_lower}/",
        "Liens Check": f"https://publicrecords.netronline.com/{state_lower}/",
        "Zillow Tax History": f"https://www.zillow.com/homes/{zip_code or city_slug}_rb/",
        "Redfin Property Details": f"https://www.redfin.com/zipcode/{zip_code}" if zip_code else f"https://www.redfin.com/city/{city_slug}/{state_upper}",
    }

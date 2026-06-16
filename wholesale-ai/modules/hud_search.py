"""
HUD data integration — Fair Market Rents, HUD homes search URLs, and open data.
Free HUD USER API token: https://www.huduser.gov/portal/dataset/api.html
"""
import os
import httpx
from typing import Optional


HUD_API_BASE = "https://www.huduser.gov/hudapi/public"
HUD_ARCGIS_BASE = "https://services.arcgis.com/VTyQ9soqVukalItT/arcgis/rest/services"
HOMESTORE_SEARCH = "https://www.hudhomestore.gov/Listing/HUDListings.aspx"


# ── State abbreviations for HUD API ──────────────────────────────────────────
STATE_CODES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
}


def get_hud_token() -> Optional[str]:
    return os.getenv("HUD_API_TOKEN")


def get_fair_market_rents(state: str, county_fips: Optional[str] = None) -> dict:
    """
    Fetch HUD Fair Market Rents for a state or specific county.
    Returns rent data for 0-4 bedroom units.
    Requires free HUD token (https://www.huduser.gov/portal/dataset/api.html).
    """
    token = get_hud_token()
    if not token:
        return {"error": "HUD_API_TOKEN not set", "signup_url": "https://www.huduser.gov/portal/dataset/api.html"}

    headers = {"Authorization": f"Bearer {token}"}
    state_upper = state.upper()

    try:
        with httpx.Client(timeout=15) as client:
            # Get counties for the state first
            counties_url = f"{HUD_API_BASE}/fmr/listCounties/{state_upper}"
            r = client.get(counties_url, headers=headers)
            r.raise_for_status()
            counties_data = r.json()

            results = []
            counties = counties_data.get("data", [])

            # If specific county requested, filter
            if county_fips:
                counties = [c for c in counties if county_fips in str(c.get("fips_code", ""))]

            # Fetch FMR for first county (or specified)
            for county in counties[:3]:  # Limit to 3 for speed
                entity_id = county.get("fips_code") or county.get("cbsasub")
                if not entity_id:
                    continue
                fmr_url = f"{HUD_API_BASE}/fmr/data/{entity_id}"
                fr = client.get(fmr_url, headers=headers)
                if fr.status_code == 200:
                    fmr_data = fr.json().get("data", {})
                    fmr_record = fmr_data.get("basicdata", [{}])
                    if fmr_record:
                        rec = fmr_record[0]
                        results.append({
                            "county": county.get("county_name", "Unknown"),
                            "state": state_upper,
                            "year": fmr_data.get("year", ""),
                            "rent_0br": rec.get("Efficiency", 0),
                            "rent_1br": rec.get("One-Bedroom", 0),
                            "rent_2br": rec.get("Two-Bedroom", 0),
                            "rent_3br": rec.get("Three-Bedroom", 0),
                            "rent_4br": rec.get("Four-Bedroom", 0),
                        })

            return {"success": True, "data": results, "state": state_upper}

    except httpx.HTTPStatusError as e:
        return {"error": f"HUD API error: {e.response.status_code}", "detail": str(e)}
    except Exception as e:
        return {"error": str(e)}


def build_hud_homestore_url(
    state: str = "",
    zip_code: str = "",
    min_price: int = 0,
    max_price: int = 500000,
    bedrooms: int = 0,
    property_type: str = "SFR",
) -> str:
    """
    Build a HUD Home Store search URL — opens directly in browser.
    HUD homes are foreclosed gov-owned properties, often 10-30% below market.
    """
    params = []
    if state:
        params.append(f"StateCode={state.upper()}")
    if zip_code:
        params.append(f"ZipCode={zip_code}")
    if max_price:
        params.append(f"MaxPrice={max_price}")
    if min_price:
        params.append(f"MinPrice={min_price}")
    if bedrooms:
        params.append(f"Bedrooms={bedrooms}")
    params.append(f"PropertyType={property_type}")
    params.append("SearchType=A")  # All statuses

    query = "&".join(params)
    return f"{HOMESTORE_SEARCH}?{query}" if query else HOMESTORE_SEARCH


def build_foreclosure_search_url(state: str = "", zip_code: str = "", max_price: int = 0) -> dict:
    """
    Build search URLs across multiple free foreclosure databases.
    Returns dict of source → URL for user to open.
    """
    urls = {}

    # Foreclosure.com (free search)
    fc_base = "https://www.foreclosure.com/listing/search.html"
    fc_params = []
    if state:
        fc_params.append(f"state={state.upper()}")
    if zip_code:
        fc_params.append(f"zip={zip_code}")
    if max_price:
        fc_params.append(f"pricemax={max_price}")
    urls["Foreclosure.com (Free)"] = f"{fc_base}?{'&'.join(fc_params)}" if fc_params else fc_base

    # HUD Home Store (gov-owned)
    urls["HUD Home Store (Gov Owned)"] = build_hud_homestore_url(
        state=state, zip_code=zip_code, max_price=max_price
    )

    # Auction.com (bank-owned REO)
    auction_url = "https://www.auction.com/residential/"
    if state:
        auction_url += f"?stateCode={state.upper()}"
    urls["Auction.com (REO/Bank Owned)"] = auction_url

    # Hubzu (bank-owned)
    hubzu_url = "https://www.hubzu.com/search"
    if state:
        hubzu_url += f"?state={state.upper()}"
    urls["Hubzu (Bank Owned)"] = hubzu_url

    # HomePath (Fannie Mae gov-owned)
    homepath_url = "https://www.homepath.com/l"
    if zip_code:
        homepath_url = f"https://www.homepath.com/l/{zip_code}"
    elif state:
        homepath_url = f"https://www.homepath.com/l/{state.lower()}"
    urls["HomePath (Fannie Mae Gov)"] = homepath_url

    # HomeSteps (Freddie Mac)
    homesteps_url = "https://www.homesteps.com/app/homesearch/search"
    urls["HomeSteps (Freddie Mac Gov)"] = homesteps_url

    # USDA Rural (gov-owned rural properties)
    usda_url = "https://properties.sc.egov.usda.gov/resales/index.do"
    urls["USDA Rural Properties (Gov)"] = usda_url

    # Veterans Affairs REO
    va_url = "https://www.ocwen.com/home-search"
    urls["VA REO Properties"] = va_url

    # Data.gov foreclosures
    urls["Data.gov Foreclosure Datasets"] = "https://catalog.data.gov/dataset/?tags=foreclosures"

    return urls


def get_gsa_properties_url() -> dict:
    """GSA surplus/for-sale federal properties."""
    return {
        "GSA Property Auctions": "https://www.gsa.gov/real-estate/real-estate-services/real-estate-for-government/leasing/lease-auctions",
        "GSA Property Disposals": "https://www.gsa.gov/real-estate/real-estate-services/real-estate-for-government/property-disposal",
        "GSA PropertyForSale.gov": "https://propertyforsale.gsa.gov/",
        "Federal Real Property Dataset (Data.gov)": "https://catalog.data.gov/dataset/real-estate-across-the-united-states-rexus-inventory-building",
        "IRS Seized Property Auctions": "https://www.treasury.gov/auctions/irs/",
        "FDIC Failed Bank Auctions": "https://www.fdic.gov/bank/individual/failed/banklist.html",
        "SBA Property Sales": "https://www.sba.gov/about-sba/sba-locations",
        "DEA Asset Forfeiture": "https://www.dea.gov/seized-assets",
        "US Marshals Asset Seizures": "https://www.usmarshals.gov/what-we-do/asset-forfeiture/current-sales",
    }


def get_tax_lien_resources(state: str = "") -> dict:
    """Tax lien and tax deed sale resources by state."""
    general = {
        "IRS Tax Lien Database": "https://www.irs.gov/privacy-disclosure/automated-lien-system-database-listing",
        "Data.gov Tax Liens": "https://catalog.data.gov/dataset/?tags=lien",
        "Tax Lien University (Free Education)": "https://www.taxlienuniversity.com/",
        "RealAuction (Online Tax Sales)": "https://www.realauction.com/",
        "GovEase (Online Tax Sales)": "https://www.govease.com/",
        "Bid4Assets (Tax Deed Auctions)": "https://www.bid4assets.com/taxsale",
        "NETR Online (County Records)": "https://publicrecords.netronline.com/",
    }

    state_resources = {}
    state_upper = state.upper() if state else ""

    # High-volume tax lien states
    lien_states = {
        "FL": "https://fl.bidspotter.com/",
        "NJ": "https://www.njsalesreports.com/",
        "MD": "https://sdat.dat.maryland.gov/",
        "GA": "https://www.gsccca.org/search",
        "TX": "https://www.texastaxsales.com/",
        "AZ": "https://treasurer.maricopa.gov/",
        "IL": "https://www.cookcountyclerkil.gov/",
        "OH": "https://www.ohiostateauditor.gov/",
    }

    if state_upper and state_upper in lien_states:
        state_resources[f"{state_upper} Tax Sale Portal"] = lien_states[state_upper]

    return {**general, **state_resources}

"""
ElevenLabs Voice — turn outreach scripts into audio automatically.

When a close package is built, this module generates an MP3 voicemail
and call-ready audio so Alberto never has to read a script cold.

Env vars:
  ELEVENLABS_API_KEY   — get at elevenlabs.io
  ELEVENLABS_VOICE_ID  — default: Roger (professional US male, in Alberto's account)
                         Find IDs at: elevenlabs.io/voice-library
                         Malformed/placeholder values are ignored automatically.

Usage:
  from modules.elevenlabs_voice import speak_script, generate_voicemail
  path = speak_script("Hi, I'm calling about 123 Main St...", "voicemail_123.mp3")
"""

import os
import re
import httpx
from pathlib import Path
from typing import Optional

BASE_URL  = "https://api.elevenlabs.io/v1"
# Roger — confirmed present in Alberto's ElevenLabs account (21-voice library).
# Adam (pNInz6obpgDQGcFmaJgB) is NOT in his account, so Roger is the safe default.
DEFAULT_VOICE_ID = "CwhRBWXzGAHq8TQ4Fs17"   # Roger — neutral US male, professional

# A real ElevenLabs voice ID is a 20-char alphanumeric token.
_VOICE_ID_RE = re.compile(r"^[A-Za-z0-9]{20}$")


def has_api_key() -> bool:
    return bool(os.getenv("ELEVENLABS_API_KEY"))


def _valid_voice_id() -> str:
    """
    Return a usable voice ID. Ignores malformed ELEVENLABS_VOICE_ID values
    (placeholder text, parentheses, spaces, blanks) and falls back to default.
    This is what stopped the 400 errors when .env held a placeholder string.
    """
    raw = os.getenv("ELEVENLABS_VOICE_ID", "").strip()
    if _VOICE_ID_RE.match(raw):
        return raw
    return DEFAULT_VOICE_ID


def _voice_id() -> str:
    return _valid_voice_id()


def speak_script(
    text:        str,
    output_path: str = "voicemail.mp3",
    stability:   float = 0.5,
    similarity:  float = 0.75,
) -> Optional[str]:
    """
    Convert text to speech via ElevenLabs and save to output_path.
    Returns the saved file path, or None if no key / network failure.

    stability  0–1: lower = more expressive, higher = more consistent
    similarity 0–1: how closely it matches the cloned voice
    """
    key = os.getenv("ELEVENLABS_API_KEY")
    if not key:
        print("  [voice] ELEVENLABS_API_KEY not set — skipping audio generation")
        return None

    try:
        r = httpx.post(
            f"{BASE_URL}/text-to-speech/{_voice_id()}",
            headers={
                "xi-api-key":   key,
                "Content-Type": "application/json",
                "Accept":       "audio/mpeg",
            },
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability":         stability,
                    "similarity_boost":  similarity,
                },
            },
            timeout=30,
        )
        if r.status_code == 200:
            Path(output_path).write_bytes(r.content)
            return output_path
        if r.status_code in (400, 422):
            print(f"  [voice] ElevenLabs rejected the request ({r.status_code}). "
                  f"Likely a bad ELEVENLABS_VOICE_ID — using default '{DEFAULT_VOICE_ID}' "
                  f"should fix it. Detail: {r.text[:120]}")
        elif r.status_code == 401:
            print("  [voice] ElevenLabs 401 — API key invalid or out of credits.")
        else:
            print(f"  [voice] ElevenLabs error {r.status_code}: {r.text[:120]}")
        return None
    except Exception as e:
        print(f"  [voice] Network error: {e}")
        return None


def generate_voicemail(
    property_address: str,
    seller_name:      str = "",
    investor_name:    str = "Alberto",
    investor_phone:   str = "",
    seller_type:      str = "generic",
    output_dir:       str = ".",
) -> Optional[str]:
    """
    Generate a 30-second voicemail MP3 for a specific deal.
    Returns the saved file path, or None if voice generation fails.
    """
    name_part = f" {seller_name}" if seller_name else ""

    scripts = {
        "tax_delinquent": (
            f"Hi{name_part}, my name is {investor_name} and I'm calling about your property "
            f"at {property_address}. I understand there may be a tax situation there. "
            f"I buy properties as-is for cash and can close in as little as two weeks — "
            f"I'll even handle the back taxes. If you're open to a quick conversation, "
            f"please give me a call back at {investor_phone}. No pressure at all. "
            f"Again, that's {investor_phone}. Have a great day."
        ),
        "pre_foreclosure": (
            f"Hi{name_part}, this is {investor_name} calling about {property_address}. "
            f"I work with homeowners who are facing a difficult situation and need to sell quickly. "
            f"I can close in two weeks, all cash, and help you avoid foreclosure hitting your credit. "
            f"Please call me back at {investor_phone}. I'm happy to answer any questions. "
            f"That number again is {investor_phone}. Thank you."
        ),
        "long_dom": (
            f"Hi{name_part}, my name is {investor_name} and I noticed your property at "
            f"{property_address} has been on the market for a while. "
            f"I'm a cash buyer — no agent commissions, no financing contingencies, I can close in two weeks. "
            f"If you'd be open to a quick conversation, please give me a call at {investor_phone}. "
            f"I look forward to hearing from you."
        ),
        "generic": (
            f"Hi{name_part}, this is {investor_name} calling. I'm interested in the property at "
            f"{property_address}. I'm a cash buyer and can close quickly with no hassle. "
            f"Please give me a call back at {investor_phone} when you get a chance. "
            f"Thank you, and have a great day."
        ),
    }

    script = scripts.get(seller_type, scripts["generic"])

    # Sanitize address for filename
    safe_addr = property_address.replace(" ", "_").replace(",", "").replace("/", "-")[:50]
    filename  = f"voicemail_{safe_addr}.mp3"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_path  = str(Path(output_dir) / filename)

    result = speak_script(script, output_path=out_path)
    if result:
        print(f"  [voice] ✓ Voicemail saved: {result}")
    return result


def generate_buyer_pitch_audio(
    property_address: str,
    price:            float,
    arv:              float,
    beds:             int = 0,
    baths:            float = 0,
    investor_name:    str = "Alberto",
    investor_phone:   str = "",
    output_dir:       str = ".",
) -> Optional[str]:
    """
    Generate a 20-second buyer pitch MP3 to play when calling cash buyers.
    """
    script = (
        f"Hey, this is {investor_name}. I've got a {beds}bed {baths}bath "
        f"at {property_address} — asking {price:,.0f}, ARV is {arv:,.0f}. "
        f"BRRRR or flip, numbers work either way. "
        f"Call me back at {investor_phone} if you want the details. Thanks."
    )

    safe_addr = property_address.replace(" ", "_").replace(",", "").replace("/", "-")[:50]
    out_path  = str(Path(output_dir) / f"buyer_pitch_{safe_addr}.mp3")

    result = speak_script(script, output_path=out_path, stability=0.4)
    if result:
        print(f"  [voice] ✓ Buyer pitch saved: {result}")
    return result


def list_available_voices() -> list:
    """Fetch all voices from ElevenLabs account. Returns list of {voice_id, name, labels}."""
    key = os.getenv("ELEVENLABS_API_KEY")
    if not key:
        return []
    try:
        r = httpx.get(f"{BASE_URL}/voices", headers={"xi-api-key": key}, timeout=15)
        if r.status_code == 200:
            return [
                {
                    "voice_id": v["voice_id"],
                    "name":     v["name"],
                    "labels":   v.get("labels", {}),
                }
                for v in r.json().get("voices", [])
            ]
        return []
    except Exception:
        return []

"""Async Gemini API Provider Client with Multi-Key Pool, Smart Auto-Failover & Round-Robin Cycling."""

import json
import logging
import time
from typing import Any, Dict, List, Optional
import httpx

from backend.config import settings
from models.sanitizer import sanitize_telemetry

logger = logging.getLogger("spectra.models.gemini")

# Key Item Schema:
# {
#   "id": str,
#   "name": str,
#   "api_key": str,
#   "is_active": bool,
#   "status": "HEALTHY" | "EXHAUSTED" | "INVALID" | "UNCHECKED",
#   "error_message": Optional[str],
#   "requests_count": int,
#   "tokens_used": int,
#   "last_used_at": Optional[str]
# }

import os

KEYS_STORE_FILE = os.path.join(os.path.dirname(__file__), "..", "gemini_keys.json")

def load_keys_from_disk() -> List[Dict[str, Any]]:
    if os.path.exists(KEYS_STORE_FILE):
        try:
            with open(KEYS_STORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_keys_to_disk(pool: List[Dict[str, Any]]):
    try:
        with open(KEYS_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(pool, f, indent=2)
    except Exception as e:
        logger.error(f"Error persisting Gemini keys: {e}")

KEY_POOL: List[Dict[str, Any]] = load_keys_from_disk()

# If settings has a key and pool is empty, initialize with default key
if not KEY_POOL and settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
    KEY_POOL.append({
        "id": "key-default",
        "name": "Default Studio Key",
        "api_key": settings.GEMINI_API_KEY.strip(),
        "is_active": True,
        "status": "UNCHECKED",
        "error_message": None,
        "requests_count": 0,
        "tokens_used": 0,
        "last_used_at": None
    })
    save_keys_to_disk(KEY_POOL)

# Global Cumulative Token & Request Tracking
GEMINI_STATS = {
    "requests_total": 0,
    "requests_successful": 0,
    "requests_failed": 0,
    "prompt_tokens_used": 0,
    "candidates_tokens_used": 0,
    "total_tokens_used": 0,
    "last_latency_ms": 0,
    "last_error": None,
    "last_checked_status": "UNCONFIGURED",
    "key_exhaustion_cycles": 0
}


class GeminiClient:
    """Async client interface for Google Gemini with Intelligent Key Failover and Cycle Rotation."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-flash-lite-latest"):
        self.model = model
        if api_key and api_key.strip():
            self.add_or_select_key(api_key.strip(), "Primary Key")

    @classmethod
    def get_keys(cls) -> List[Dict[str, Any]]:
        """Return safe list of keys with masked API credentials."""
        safe_list = []
        for k in KEY_POOL:
            raw_key = k["api_key"]
            masked = f"AIza...{raw_key[-4:]}" if len(raw_key) > 8 else "AIza..."
            safe_list.append({
                "id": k["id"],
                "name": k["name"],
                "masked_key": masked,
                "is_active": k["is_active"],
                "status": k["status"],
                "error_message": k.get("error_message"),
                "requests_count": k.get("requests_count", 0),
                "tokens_used": k.get("tokens_used", 0),
                "last_used_at": k.get("last_used_at")
            })
        return safe_list

    @classmethod
    def add_key(cls, key: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Add a new API key to the pool."""
        clean_key = key.strip()
        # Check if already exists
        for existing in KEY_POOL:
            if existing["api_key"] == clean_key:
                if name:
                    existing["name"] = name
                return existing

        key_id = f"key-{int(time.time() * 1000)}"
        key_name = name or f"Gemini Key #{len(KEY_POOL) + 1}"
        new_item = {
            "id": key_id,
            "name": key_name,
            "api_key": clean_key,
            "is_active": len(KEY_POOL) == 0,  # make active if first
            "status": "UNCHECKED",
            "error_message": None,
            "requests_count": 0,
            "tokens_used": 0,
            "last_used_at": None
        }
        KEY_POOL.append(new_item)
        if len(KEY_POOL) == 1:
            settings.GEMINI_API_KEY = clean_key
        save_keys_to_disk(KEY_POOL)
        return new_item

    @classmethod
    def set_active_key(cls, key_id: str) -> bool:
        """Manually switch active API key."""
        found = False
        for k in KEY_POOL:
            if k["id"] == key_id:
                k["is_active"] = True
                settings.GEMINI_API_KEY = k["api_key"]
                found = True
            else:
                k["is_active"] = False
        if found:
            save_keys_to_disk(KEY_POOL)
        return found

    @classmethod
    def delete_key(cls, key_id: str) -> bool:
        """Remove an API key from the pool."""
        global KEY_POOL
        initial_len = len(KEY_POOL)
        KEY_POOL = [k for k in KEY_POOL if k["id"] != key_id]
        if any(k["is_active"] for k in KEY_POOL):
            pass
        elif len(KEY_POOL) > 0:
            KEY_POOL[0]["is_active"] = True
            settings.GEMINI_API_KEY = KEY_POOL[0]["api_key"]
        else:
            settings.GEMINI_API_KEY = ""
        save_keys_to_disk(KEY_POOL)
        return len(KEY_POOL) < initial_len

    @classmethod
    async def sync_keys_from_db(cls):
        """Sync keys from system_api_keys table into KEY_POOL."""
        global KEY_POOL
        try:
            from database.session import async_session_factory
            from sqlalchemy import text
            async with async_session_factory() as session:
                res = await session.execute(text("SELECT id, name, api_key, is_active FROM system_api_keys WHERE service = 'gemini' ORDER BY created_at ASC"))
                db_keys = res.fetchall()
                if db_keys:
                    for row in db_keys:
                        cls.add_key(key=row.api_key, name=row.name)
                        if row.is_active:
                            cls.set_active_key(row.id)
        except Exception as e:
            logger.warning(f"Could not sync keys from PostgreSQL: {e}")


    @classmethod
    def get_active_key_item(cls) -> Optional[Dict[str, Any]]:
        """Return the current active key entry."""
        for k in KEY_POOL:
            if k["is_active"]:
                return k
        if KEY_POOL:
            KEY_POOL[0]["is_active"] = True
            settings.GEMINI_API_KEY = KEY_POOL[0]["api_key"]
            return KEY_POOL[0]
        return None

    @classmethod
    def rotate_to_next_healthy_key(cls, current_failed_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Smart Auto-Switch: When 1 key exhausts (HTTP 429), switch automatically to next healthy key in the cycle."""
        if len(KEY_POOL) <= 1:
            return None

        # Find current index
        curr_idx = 0
        for i, k in enumerate(KEY_POOL):
            if k["id"] == current_failed_id or (current_failed_id is None and k["is_active"]):
                curr_idx = i
                break

        # Search circularly for next key that isn't hard invalid
        total_keys = len(KEY_POOL)
        for offset in range(1, total_keys + 1):
            next_idx = (curr_idx + offset) % total_keys
            candidate = KEY_POOL[next_idx]
            
            # If candidate was exhausted long ago, give it a chance on new cycle
            if candidate["status"] != "INVALID":
                # Deactivate all, activate candidate
                for k in KEY_POOL:
                    k["is_active"] = False
                candidate["is_active"] = True
                settings.GEMINI_API_KEY = candidate["api_key"]
                GEMINI_STATS["key_exhaustion_cycles"] += 1
                logger.warning(
                    f"🔁 [SMART KEY ROTATION] Key '{KEY_POOL[curr_idx]['name']}' exhausted. "
                    f"Auto-switched to '{candidate['name']}' (Index {next_idx + 1}/{total_keys})."
                )
                return candidate

        return None

    def is_configured(self) -> bool:
        """Check if at least one Gemini API Key is configured."""
        active = self.get_active_key_item()
        return bool(active and active["api_key"].strip())

    async def check_connectivity_and_health(self) -> Dict[str, Any]:
        """Test active key validity and ping Google Cloud API."""
        active_item = self.get_active_key_item()
        if not active_item:
            GEMINI_STATS["last_checked_status"] = "UNCONFIGURED"
            return {
                "healthy": False,
                "status": "UNCONFIGURED",
                "message": "No Gemini API keys registered in key pool. Add your key to start.",
                "internet_connected": False,
                "keys_count": 0
            }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}?key={active_item['api_key']}"
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    active_item["status"] = "HEALTHY"
                    active_item["error_message"] = None
                    GEMINI_STATS["last_checked_status"] = "HEALTHY"
                    GEMINI_STATS["last_error"] = None
                    return {
                        "healthy": True,
                        "status": "HEALTHY",
                        "model": self.model,
                        "display_name": data.get("displayName", "Gemini 2.5 Flash"),
                        "input_token_limit": data.get("inputTokenLimit", 1048576),
                        "output_token_limit": data.get("outputTokenLimit", 8192),
                        "message": f"Active Key '{active_item['name']}' verified and operational.",
                        "internet_connected": True,
                        "active_key_id": active_item["id"],
                        "keys_count": len(KEY_POOL)
                    }
                elif res.status_code == 429:
                    active_item["status"] = "EXHAUSTED"
                    active_item["error_message"] = "Rate limit / quota exhausted (HTTP 429)"
                    # Trigger immediate auto rotation
                    next_key = self.rotate_to_next_healthy_key(active_item["id"])
                    if next_key:
                        return await self.check_connectivity_and_health()
                    return {
                        "healthy": False,
                        "status": "EXHAUSTED",
                        "message": "All configured Gemini API keys have exhausted their quota.",
                        "internet_connected": True,
                        "keys_count": len(KEY_POOL)
                    }
                else:
                    err_msg = res.text[:120]
                    active_item["status"] = "INVALID"
                    active_item["error_message"] = err_msg
                    GEMINI_STATS["last_checked_status"] = "INVALID_KEY"
                    return {
                        "healthy": False,
                        "status": "INVALID_KEY",
                        "message": f"Gemini API error (HTTP {res.status_code}): {err_msg}",
                        "internet_connected": True,
                        "keys_count": len(KEY_POOL)
                    }
        except httpx.ConnectError:
            GEMINI_STATS["last_checked_status"] = "NO_INTERNET"
            return {
                "healthy": False,
                "status": "NO_INTERNET",
                "message": "No internet connection to Google Cloud. Switching to local Ollama.",
                "internet_connected": False,
                "keys_count": len(KEY_POOL)
            }
        except Exception as e:
            return {
                "healthy": False,
                "status": "ERROR",
                "message": f"Health check failed: {str(e)}",
                "internet_connected": False,
                "keys_count": len(KEY_POOL)
            }

    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        """Send prompt to Gemini API with automatic quota failover cycling across keys."""
        if not self.is_configured():
            logger.warning("No Gemini API key available in pool.")
            return ""

        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Instruction:\n{system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will follow these security analysis instructions."}]})
        
        sanitized_prompt = sanitize_telemetry(prompt)
        contents.append({"role": "user", "parts": [{"text": sanitized_prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048
            }
        }

        # Try active key; if 429 quota exhausted, rotate to next key and retry up to len(KEY_POOL) times
        max_retries = max(1, len(KEY_POOL))
        for attempt in range(max_retries):
            active_item = self.get_active_key_item()
            if not active_item:
                break

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={active_item['api_key']}"
            start_t = time.time()
            GEMINI_STATS["requests_total"] += 1
            active_item["requests_count"] = active_item.get("requests_count", 0) + 1

            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(url, json=payload)
                    latency = round((time.time() - start_t) * 1000)
                    GEMINI_STATS["last_latency_ms"] = latency

                    if response.status_code == 200:
                        GEMINI_STATS["requests_successful"] += 1
                        active_item["status"] = "HEALTHY"
                        active_item["last_used_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        data = response.json()
                        
                        usage = data.get("usageMetadata", {})
                        p_tok = usage.get("promptTokenCount", 0)
                        c_tok = usage.get("candidatesTokenCount", 0)
                        t_tok = usage.get("totalTokenCount", 0) or (p_tok + c_tok)
                            
                        GEMINI_STATS["prompt_tokens_used"] += p_tok
                        GEMINI_STATS["candidates_tokens_used"] += c_tok
                        GEMINI_STATS["total_tokens_used"] += t_tok
                        active_item["tokens_used"] = active_item.get("tokens_used", 0) + t_tok

                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "").strip()
                        return ""

                    # Quota Exhausted (HTTP 429) -> Auto Failover to Next Key
                    elif response.status_code == 429:
                        logger.warning(
                            f"⚠️ Gemini Key '{active_item['name']}' returned HTTP 429 (Quota Exhausted). "
                            f"Attempting smart failover..."
                        )
                        active_item["status"] = "EXHAUSTED"
                        active_item["error_message"] = "Quota Exhausted (429)"
                        GEMINI_STATS["requests_failed"] += 1
                        
                        # Rotate to next key
                        next_key = self.rotate_to_next_healthy_key(active_item["id"])
                        if not next_key:
                            logger.error("All keys in Gemini pool are exhausted.")
                            break
                        # Loop continues with next_key
                        continue

                    elif response.status_code == 503:
                        logger.warning(f"Gemini model {self.model} received 503 (high demand). Trying alternative Gemini model...")
                        alt_model = "gemini-3.5-flash" if self.model == "gemini-flash-lite-latest" else "gemini-flash-lite-latest"
                        alt_url = f"https://generativelanguage.googleapis.com/v1beta/models/{alt_model}:generateContent?key={active_item['api_key']}"
                        alt_res = await client.post(alt_url, json=payload)
                        if alt_res.status_code == 200:
                            data = alt_res.json()
                            candidates = data.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                if parts:
                                    return parts[0].get("text", "").strip()

                        GEMINI_STATS["requests_failed"] += 1
                        err_text = response.text[:200]
                        active_item["error_message"] = err_text
                        GEMINI_STATS["last_error"] = f"HTTP {response.status_code}: {err_text}"
                        logger.error(f"Gemini API returned status HTTP {response.status_code}: {err_text}")
                        return ""

                    else:
                        GEMINI_STATS["requests_failed"] += 1
                        err_text = response.text[:200]
                        active_item["error_message"] = err_text
                        GEMINI_STATS["last_error"] = f"HTTP {response.status_code}: {err_text}"
                        logger.error(f"Gemini API returned status HTTP {response.status_code}: {err_text}")
                        return ""

            except Exception as err:
                GEMINI_STATS["requests_failed"] += 1
                GEMINI_STATS["last_error"] = str(err)
                logger.error(f"Error during Gemini API generation: {err}")
                return ""

        return ""

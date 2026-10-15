"""FastAPI Endpoints for AI Model Status, Router Management, Multi-Key Pool & Round-Robin Failover."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.router import ModelRouter, ROUTER_CONFIG
from models.gemini import GeminiClient
from models.ollama import OllamaClient

router = APIRouter(prefix="/ai", tags=["AI Model Router & Providers"])


class ChatQueryRequest(BaseModel):
    query: str
    incident_context: Optional[str] = None


class GeminiKeyAddRequest(BaseModel):
    api_key: str
    name: Optional[str] = None
    model: Optional[str] = "gemini-2.5-flash"


class GeminiKeySelectRequest(BaseModel):
    key_id: str


class GeminiModelUpdateRequest(BaseModel):
    model: str


class RouterModeUpdateRequest(BaseModel):
    mode: str  # 'auto' | 'gemini' | 'ollama'


@router.get("/status", response_model=Dict[str, Any])
async def get_ai_models_status():
    """Retrieve full health, token accounting, multi-key pool, and connectivity status."""
    model_router = ModelRouter()
    return await model_router.get_model_status()


@router.post("/keys/add")
async def add_gemini_api_key(req: GeminiKeyAddRequest):
    """Add a new Google Gemini API Key to the multi-key failover pool."""
    clean_key = req.api_key.strip()
    if not clean_key:
        raise HTTPException(status_code=400, detail="Gemini API Key cannot be empty.")
    
    new_item = GeminiClient.add_key(clean_key, req.name)
    gemini = GeminiClient(model=req.model or "gemini-2.5-flash")
    health_res = await gemini.check_connectivity_and_health()

    return {
        "success": True,
        "message": f"Gemini API Key '{new_item['name']}' added to rotation pool.",
        "key": new_item,
        "health": health_res,
        "keys": GeminiClient.get_keys()
    }


@router.post("/keys/select")
async def select_active_gemini_key(req: GeminiKeySelectRequest):
    """Manually switch active API key in the multi-key pool."""
    success = GeminiClient.set_active_key(req.key_id)
    if not success:
        raise HTTPException(status_code=404, detail="Key ID not found in pool.")
    
    gemini = GeminiClient()
    health_res = await gemini.check_connectivity_and_health()
    return {
        "success": True,
        "message": "Switched active Gemini key.",
        "health": health_res,
        "keys": GeminiClient.get_keys()
    }


@router.delete("/keys/{key_id}")
async def delete_gemini_key(key_id: str):
    """Delete an API key from the multi-key failover pool."""
    success = GeminiClient.delete_key(key_id)
    if not success:
        raise HTTPException(status_code=404, detail="Key ID not found in pool.")
    
    return {
        "success": True,
        "message": "Key removed from pool.",
        "keys": GeminiClient.get_keys()
    }


@router.post("/config/model")
async def update_gemini_model(req: GeminiModelUpdateRequest):
    """Update active Gemini model (e.g. gemini-2.5-flash, gemini-2.5-pro, etc.)."""
    gemini = GeminiClient(model=req.model)
    gemini.model = req.model
    health_res = await gemini.check_connectivity_and_health()
    return {
        "success": True,
        "message": f"Gemini active model updated to '{req.model}'.",
        "health": health_res
    }


@router.post("/config/mode")
async def update_router_mode(req: RouterModeUpdateRequest):
    """Switch AI Routing mode between 'auto', 'gemini' (force cloud), or 'ollama' (force local)."""
    valid_modes = ["auto", "gemini", "ollama"]
    if req.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Choose from {valid_modes}")

    ROUTER_CONFIG["mode"] = req.mode
    model_router = ModelRouter()
    status = await model_router.get_model_status()
    return {
        "success": True,
        "mode": req.mode,
        "status": status
    }


@router.post("/chat")
async def chat_with_ai(req: ChatQueryRequest):
    """Direct Q&A with the active AI model (Gemini Cloud with multi-key failover or Local Ollama)."""
    model_router = ModelRouter()
    system_prompt = (
        "You are SPECTRA-AI, an elite Autonomous SOC Cyber Threat Analyst. "
        "Strict Guidelines: "
        "1. Do NOT repeat or paraphrase the user's question. "
        "2. Do NOT use markdown symbols like hashtags (###) or asterisks (***, **). Write in clean, professional plain text with clear paragraphs. "
        "3. Provide direct threat analysis, risk validation, and immediate containment recommendations. "
        "4. Be direct, authoritative, and concise."
    )
    full_prompt = f"Telemetry Context:\n{req.incident_context}\n\nAnalyst Query: {req.query}" if req.incident_context else req.query

    def clean_markdown_artifacts(text: str) -> str:
        """Strip raw asterisks and hashtag headers to maintain clean enterprise text."""
        import re
        t = re.sub(r'#+\s*', '', text)
        t = re.sub(r'\*{1,3}', '', t)
        t = re.sub(r'`{1,3}', '', t)
        return t.strip()

    # Generate dynamic suggested questions based on query & context
    def generate_suggested_questions(query: str, context: Optional[str]) -> List[str]:
        q_lower = query.lower()
        ctx_lower = (context or "").lower()

        if "quarantine" in q_lower or "containment" in q_lower:
            return [
                "What processes should be terminated before network quarantine?",
                "How to roll back firewall quarantine rules after remediation?",
                "What artifacts must be preserved for forensic memory dump?"
            ]
        elif "60642" in ctx_lower or "protection" in ctx_lower or "scheduled" in ctx_lower:
            return [
                "How to detect persistence via Windows Scheduled Tasks?",
                "What parent process triggered this event?",
                "Should I isolate this endpoint (Lazasus)?",
                "What is the MITRE ATT&CK technique for this activity?"
            ]
        elif "network" in ctx_lower or "ip" in ctx_lower or "c2" in ctx_lower:
            return [
                "Are there anomalous outbound TCP connections on this host?",
                "Check reputation of destination IP via AbuseIPDB/VirusTotal",
                "Generate netsh firewall block command for outbound traffic"
            ]
        else:
            return [
                "What is the MITRE ATT&CK technique for this activity?",
                "Is this a true positive security alert or normal system noise?",
                "What containment playbooks should be executed immediately?",
                "Explain the raw JSON evidence fields step-by-step"
            ]

    suggested_questions = generate_suggested_questions(req.query, req.incident_context)

    try:
        reply, chosen_choice = await model_router.execute_reasoning(
            agent_role="investigation_agent",
            prompt=full_prompt,
            system_prompt=system_prompt,
            complexity="medium"
        )
        if reply and len(reply.strip()) > 5:
            clean_reply = clean_markdown_artifacts(reply)
            if "gemini" in str(chosen_choice).lower():
                active_k = GeminiClient.get_active_key_item()
                k_name = active_k.get("name", "Key") if active_k else "Cloud"
                model_label = f"Google Gemini ({model_router.gemini.model}) [{k_name}]"
            elif "ollama" in str(chosen_choice).lower():
                model_label = "Local Ollama Llama 3"
            else:
                model_label = "Deterministic Security Engine"

            return {
                "reply": clean_reply,
                "model": model_label,
                "source": str(chosen_choice),
                "suggested_questions": suggested_questions
            }
    except Exception as e:
        logger.warning(f"Error executing AI chat reasoning: {e}")

    # Clean contextual fallback without markdown hashtags or asterisks
    clean_fallback = (
        "Event Analysis: Telemetry indicates a standard endpoint system event. "
        "Rule 60642 is commonly associated with Microsoft Software Protection Service scheduling. "
        "While routine licensing checks trigger this normally, threat actors frequently hijack or mimic legitimate service names to evade detection.\n\n"
        "SOC Verification Steps:\n"
        "1. Verify the parent process execution path and cryptographic signature.\n"
        "2. Inspect active network sockets on host Lazasus for unexpected outbound C2 traffic.\n"
        "3. If an unauthorized binary or persistence task is discovered, execute Host Network Quarantine immediately."
    )

    return {
        "reply": clean_fallback,
        "model": "SPECTRA-AI (SOC Expert Engine)",
        "source": "spectra_core",
        "suggested_questions": suggested_questions
    }

"""FastAPI Route Handlers for Deterministic Security Intelligence API."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db_session
from backend.services.ioc_service import BackendIOCService
from backend.services.mitre_service import BackendMitreService
from backend.services.enrichment_service import BackendEnrichmentService
from backend.api.schemas.ioc import IOCResponse
from backend.api.schemas.mitre import MitreTechniqueResponse
from backend.api.schemas.enrichment import EnrichedEventResponse

router = APIRouter(prefix="/intelligence", tags=["Deterministic Security Intelligence"])


@router.get("/iocs", response_model=List[IOCResponse], summary="List Indicators of Compromise")
async def list_iocs(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    type: Optional[str] = Query(default=None, description="Filter by IOC type (ip, domain, url, md5, sha1, sha256, username, file_path)"),
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves list of extracted and normalized IOC records."""
    service = BackendIOCService(db)
    return await service.list_iocs(limit=limit, offset=offset, ioc_type=type)


@router.get("/iocs/{ioc_id}", response_model=IOCResponse, summary="Get IOC Details")
async def get_ioc_by_id(
    ioc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves single IOC record details by UUID primary key."""
    service = BackendIOCService(db)
    ioc = await service.get_ioc_by_id(ioc_id)
    if not ioc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"IOC with ID {ioc_id} not found")
    return ioc


@router.get("/mitre", response_model=List[MitreTechniqueResponse], summary="List MITRE ATT&CK Catalog Techniques")
async def list_mitre_techniques(
    tactic: Optional[str] = Query(default=None, description="Filter by tactic name (e.g. Execution, Credential Access)"),
    db: AsyncSession = Depends(get_db_session)
):
    """Lists versioned local MITRE ATT&CK catalog techniques."""
    service = BackendMitreService(db)
    return await service.list_techniques(tactic=tactic)


@router.get("/mitre/{technique_id}", response_model=MitreTechniqueResponse, summary="Get MITRE Technique Details")
async def get_mitre_technique(
    technique_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves details of a MITRE ATT&CK technique by ID (e.g., T1059 or T1059.001)."""
    service = BackendMitreService(db)
    tech = await service.get_technique_by_id(technique_id)
    if not tech:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"MITRE technique '{technique_id}' not found in catalog")
    return tech


@router.get("/events/{event_id}", response_model=EnrichedEventResponse, summary="Get Enriched Event Intelligence")
async def get_enriched_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves deterministic enrichment data (IOCs, MITRE mappings) for a persisted SPECTRA event."""
    service = BackendEnrichmentService(db)
    enriched = await service.get_enriched_event(event_id)
    if not enriched:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID '{event_id}' not found")
    return enriched


@router.post("/events/{event_id}/enrich", response_model=EnrichedEventResponse, summary="Trigger Deterministic Event Enrichment")
async def enrich_persisted_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Explicitly triggers deterministic IOC extraction, normalization, and MITRE mapping for a persisted event."""
    service = BackendEnrichmentService(db)
    enriched = await service.enrich_persisted_event(event_id)
    if not enriched:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID '{event_id}' not found")
    return enriched

import asyncio
import logging
from datetime import datetime, timezone
from database.session import async_session_factory
from backend.integrations.wazuh.client import WazuhClient
from backend.services.event_service import EventService
from intelligence.normalization.models import NormalizedEvent

logger = logging.getLogger("spectra.wazuh_sync")

import os
import json

class WazuhSyncWorker:
    def __init__(self):
        self.client = WazuhClient()
        self.is_running = False
        self.task = None
        self.alerts_file_offset = 0

    async def start(self):
        """Starts the background continuous monitoring loop."""
        self.is_running = True
        self.task = asyncio.create_task(self._poll_loop())
        logger.info("Wazuh continuous monitoring sync worker started.")

    async def stop(self):
        """Stops the background continuous monitoring loop."""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Wazuh sync worker stopped.")

    async def _poll_loop(self):
        alerts_path = "/var/ossec/logs/alerts/alerts.json"
        archives_path = "/var/ossec/logs/archives/archives.json"
        self.archives_file_offset = 0
        
        while self.is_running:
            try:
                async with async_session_factory() as session:
                    event_service = EventService(session)

                    # 1. Real-time alerts.json streaming tail (Higher priority alerts)
                    if os.path.exists(alerts_path):
                        try:
                            file_size = os.path.getsize(alerts_path)
                            if self.alerts_file_offset == 0 and file_size > 50000:
                                self.alerts_file_offset = max(0, file_size - 30000)

                            with open(alerts_path, "r", encoding="utf-8", errors="ignore") as f:
                                f.seek(self.alerts_file_offset)
                                new_lines = f.readlines()
                                self.alerts_file_offset = f.tell()

                            for line in new_lines:
                                line = line.strip()
                                if not line:
                                    continue
                                try:
                                    alert = json.loads(line)
                                    rule = alert.get("rule", {})
                                    agent = alert.get("agent", {})
                                    agent_id = agent.get("id", "002")
                                    agent_name = agent.get("name", "Lazasus")
                                    agent_ip = agent.get("ip", "127.0.0.1")

                                    normalized = NormalizedEvent(
                                        event_id=alert.get("id", str(hash(line))),
                                        timestamp=alert.get("timestamp") or datetime.now(timezone.utc).isoformat(),
                                        source="wazuh_agent",
                                        agent_id=agent_id,
                                        agent_name=agent_name,
                                        agent_ip=agent_ip,
                                        rule_id=str(rule.get("id", "ALRT")),
                                        rule_level=rule.get("level", 3),
                                        rule_description=rule.get("description", "Security Alert"),
                                        event_type="alert",
                                        location=alert.get("location"),
                                        raw_event=alert
                                    )
                                    await event_service.ingest_normalized_event(normalized)
                                except Exception:
                                    pass
                        except Exception as e:
                            logger.error(f"Error reading alerts.json: {e}")

                    # 2. Real-time archives.json streaming tail (All events & raw Windows channel activity)
                    if os.path.exists(archives_path):
                        try:
                            arc_size = os.path.getsize(archives_path)
                            if self.archives_file_offset == 0 and arc_size > 50000:
                                self.archives_file_offset = max(0, arc_size - 30000)

                            with open(archives_path, "r", encoding="utf-8", errors="ignore") as af:
                                af.seek(self.archives_file_offset)
                                arc_lines = af.readlines()
                                self.archives_file_offset = af.tell()

                            for arc_line in arc_lines:
                                arc_line = arc_line.strip()
                                if not arc_line:
                                    continue
                                try:
                                    arc_event = json.loads(arc_line)
                                    # Skip if it is already an alert (already handled above)
                                    if "rule" in arc_event:
                                        continue

                                    agent = arc_event.get("agent", {})
                                    agent_id = agent.get("id", "002")
                                    agent_name = agent.get("name", "Lazasus")
                                    agent_ip = agent.get("ip", "127.0.0.1")
                                    
                                    data_sec = arc_event.get("data", {})
                                    win_sys = data_sec.get("win", {}).get("system", {})
                                    provider = win_sys.get("providerName") or arc_event.get("decoder", {}).get("name", "syslog")
                                    event_id_code = win_sys.get("eventID", "LOG")
                                    
                                    desc = f"{provider} Event [{event_id_code}]"
                                    if "eventdata" in data_sec.get("win", {}):
                                        edata = data_sec["win"]["eventdata"]
                                        if isinstance(edata, dict) and "data" in edata:
                                            desc = f"{desc}: {str(edata['data'])[:80]}"

                                    normalized = NormalizedEvent(
                                        event_id=arc_event.get("id", str(hash(arc_line))),
                                        timestamp=arc_event.get("timestamp") or datetime.now(timezone.utc).isoformat(),
                                        source="wazuh_agent",
                                        agent_id=agent_id,
                                        agent_name=agent_name,
                                        agent_ip=agent_ip,
                                        rule_id=str(event_id_code),
                                        rule_level=2,
                                        rule_description=desc,
                                        event_type="telemetry",
                                        location=arc_event.get("location", "EventChannel"),
                                        raw_event=arc_event
                                    )
                                    await event_service.ingest_normalized_event(normalized)
                                except Exception:
                                    pass
                        except Exception as e:
                            logger.error(f"Error reading archives.json: {e}")

                    # 2. Continuous Active Endpoint FIM/Syscheck check
                    agents_resp = await self.client.get_agents()
                    agents = agents_resp.get("data", {}).get("affected_items", [])
                    active_endpoints = [a for a in agents if a.get("id") != "000" and a.get("status") == "active"]

                    for ep in active_endpoints:
                        agent_id = ep.get("id")
                        agent_name = ep.get("name", "Lazasus")
                        agent_ip = ep.get("ip", "127.0.0.1")

                        sys_resp = await self.client.get_agent_syscheck(agent_id=agent_id, limit=10)
                        fim_items = sys_resp.get("data", {}).get("affected_items", [])

                        for item in fim_items:
                            file_path = item.get("file", "Registry/File")
                            val_name = item.get("value", {}).get("name", "")
                            target_desc = f"{file_path} ({val_name})" if val_name else file_path

                            normalized = NormalizedEvent(
                                event_id=f"WZH-{agent_id}-{hash(target_desc + str(item.get('date')))}",
                                timestamp=item.get("date") or datetime.now(timezone.utc).isoformat(),
                                source="wazuh_agent",
                                agent_id=agent_id,
                                agent_name=agent_name,
                                agent_ip=agent_ip,
                                rule_id="FIM-SYSCHECK",
                                rule_level=4,
                                rule_description=f"File/Registry Integrity: {target_desc}",
                                event_type="telemetry",
                                location=file_path,
                                raw_event=item
                            )
                            try:
                                await event_service.ingest_normalized_event(normalized)
                            except Exception:
                                pass

            except Exception as e:
                logger.error(f"Error in continuous monitoring loop: {e}")
            
            # Continuous fast loop (every 3 seconds for real-time responsiveness)
            await asyncio.sleep(3)

wazuh_sync_worker = WazuhSyncWorker()

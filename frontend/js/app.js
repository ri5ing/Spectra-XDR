/**
 * SPECTRA-XDR — SOC Analyst Console Application Logic.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Current Active Context State
    let activeTab = "dashboard";
    let activeIncidentId = null;
    let incidentsData = [];

    // --- Tab Navigation ---
    const navTabs = document.querySelectorAll(".nav-tab");
    const viewPanels = document.querySelectorAll(".view-panel");

    navTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const targetTab = tab.getAttribute("data-tab");
            switchTab(targetTab);
        });
    });

    function switchTab(tabName) {
        activeTab = tabName;
        navTabs.forEach(t => {
            if (t.getAttribute("data-tab") === tabName) {
                t.classList.add("active");
            } else {
                t.classList.remove("active");
            }
        });

        viewPanels.forEach(panel => {
            if (panel.id === `view-${tabName}`) {
                panel.classList.remove("hidden");
            } else {
                panel.classList.add("hidden");
            }
        });

        // Trigger load for active view
        loadActiveView();
    }

    function loadActiveView() {
        if (activeTab === "dashboard") loadDashboard();
        else if (activeTab === "incidents") loadIncidents();
        else if (activeTab === "swarm") loadSwarm();
        else if (activeTab === "detections") loadDetections();
        else if (activeTab === "intelligence") loadIntelligence();
        else if (activeTab === "wazuh") loadWazuh();
    }

    // Refresh Button & 30s Polling
    document.getElementById("btn-refresh").addEventListener("click", () => {
        loadActiveView();
    });

    setInterval(() => {
        loadActiveView();
    }, 30000);

    // Initial Load
    switchTab("dashboard");

    // ==========================================
    // 1. DASHBOARD VIEW
    // ==========================================
    async function loadDashboard() {
        try {
            const summary = await api.getDashboardSummary();
            
            // KPIs
            document.getElementById("kpi-total-incidents").textContent = summary.incidents.total;
            document.getElementById("kpi-incidents-sub").textContent = `${summary.incidents.open} Open | ${summary.incidents.investigating} Investigating`;
            
            const critHigh = (summary.severity.critical || 0) + (summary.severity.high || 0);
            document.getElementById("kpi-critical-incidents").textContent = critHigh;
            document.getElementById("kpi-critical-sub").textContent = `${summary.severity.critical || 0} Critical | ${summary.severity.high || 0} High`;

            document.getElementById("kpi-detection-matches").textContent = summary.detections.matches;
            
            const totalIntel = (summary.intelligence.iocs || 0) + (summary.intelligence.mitre_techniques || 0);
            document.getElementById("kpi-intel-count").textContent = totalIntel;
            document.getElementById("kpi-intel-sub").textContent = `${summary.intelligence.iocs} IOCs | ${summary.intelligence.mitre_techniques} ATT&CK`;

            // Wazuh status badge
            const wBadge = document.getElementById("wazuh-status-badge");
            const wText = document.getElementById("wazuh-status-text");
            if (summary.wazuh.status === "healthy") {
                wBadge.className = "flex items-center space-x-2 text-xs px-3 py-1.5 rounded-full bg-dark-800 border border-emerald-800/60";
                wText.className = "font-mono text-emerald-400";
                wText.textContent = "Wazuh Connected";
            } else {
                wBadge.className = "flex items-center space-x-2 text-xs px-3 py-1.5 rounded-full bg-dark-800 border border-rose-800/60";
                wText.className = "font-mono text-rose-400";
                wText.textContent = "Wazuh Unavailable";
            }

            // Severity Progress Bars
            const maxInc = summary.incidents.total || 1;
            ["critical", "high", "medium", "low"].forEach(sev => {
                const count = summary.severity[sev] || 0;
                document.getElementById(`cnt-sev-${sev}`).textContent = count;
                const pct = Math.round((count / maxInc) * 100);
                document.getElementById(`bar-sev-${sev}`).style.width = `${pct}%`;
            });

            // Recent Incidents Table
            const tbody = document.querySelector("#table-recent-incidents tbody");
            if (!summary.recent_incidents || summary.recent_incidents.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center py-6 text-dark-400">No recent incidents recorded</td></tr>`;
            } else {
                tbody.innerHTML = summary.recent_incidents.map(inc => `
                    <tr class="cursor-pointer" onclick="openIncidentDetail('${inc.id}')">
                        <td class="font-mono text-cyan-400 font-semibold">${inc.incident_id}</td>
                        <td>${formatSeverityBadge(inc.severity)}</td>
                        <td>${formatStatusBadge(inc.status)}</td>
                        <td class="font-medium">${escapeHtml(inc.title)}</td>
                        <td class="text-dark-400 text-xs">${formatDate(inc.created_at)}</td>
                    </tr>
                `).join("");
            }
        } catch (err) {
            console.error("Failed to load dashboard:", err);
        }
    }

    document.querySelectorAll('[data-action="goto-incidents"]').forEach(btn => {
        btn.addEventListener("click", () => switchTab("incidents"));
    });

    // ==========================================
    // 2. INCIDENTS VIEW
    // ==========================================
    async function loadIncidents() {
        try {
            const severity = document.getElementById("filter-severity").value;
            const status = document.getElementById("filter-status").value;
            const search = document.getElementById("filter-search").value.toLowerCase();

            incidentsData = await api.getIncidents({ severity, status, limit: 100 });
            
            let filtered = incidentsData;
            if (search) {
                filtered = filtered.filter(i => 
                    i.title.toLowerCase().includes(search) || 
                    i.incident_id.toLowerCase().includes(search)
                );
            }

            document.getElementById("incidents-count-label").textContent = `Showing ${filtered.length} incidents`;

            const tbody = document.querySelector("#table-incidents tbody");
            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-dark-400">No incidents match current filters</td></tr>`;
            } else {
                tbody.innerHTML = filtered.map(inc => `
                    <tr>
                        <td class="font-mono text-cyan-400 font-bold">${inc.incident_id}</td>
                        <td>${formatSeverityBadge(inc.severity)}</td>
                        <td>${formatStatusBadge(inc.status)}</td>
                        <td class="font-medium">${escapeHtml(inc.title)}</td>
                        <td class="text-xs font-mono text-dark-300">${inc.assigned_to ? escapeHtml(inc.assigned_to) : '<span class="text-dark-500">Unassigned</span>'}</td>
                        <td class="text-xs text-dark-400">${formatDate(inc.updated_at)}</td>
                        <td>
                            <button class="btn btn-xs btn-cyan" onclick="openIncidentDetail('${inc.id}')">Investigate</button>
                        </td>
                    </tr>
                `).join("");
            }
        } catch (err) {
            console.error("Failed to load incidents:", err);
        }
    }

    document.getElementById("filter-severity").addEventListener("change", loadIncidents);
    document.getElementById("filter-status").addEventListener("change", loadIncidents);
    document.getElementById("filter-search").addEventListener("input", loadIncidents);
    document.getElementById("btn-clear-filters").addEventListener("click", () => {
        document.getElementById("filter-severity").value = "";
        document.getElementById("filter-status").value = "";
        document.getElementById("filter-search").value = "";
        loadIncidents();
    });

    // ==========================================
    // 3. INCIDENT DETAIL MODAL & WORKFLOW
    // ==========================================
    window.openIncidentDetail = async function(incidentId) {
        activeIncidentId = incidentId;
        const modal = document.getElementById("modal-incident");
        modal.classList.remove("hidden");

        // Load detail data
        try {
            const inc = await api.getIncident(incidentId);
            document.getElementById("detail-inc-id").textContent = inc.incident_id;
            document.getElementById("detail-title").textContent = inc.title;
            document.getElementById("detail-description").textContent = inc.description || "No description provided.";
            
            document.getElementById("detail-severity-badge").innerHTML = formatSeverityBadge(inc.severity);
            document.getElementById("detail-status-badge").innerHTML = formatStatusBadge(inc.status);
            
            document.getElementById("action-update-status").value = inc.status.toLowerCase();
            document.getElementById("action-assignee").value = inc.assigned_to || "";

            // Switch to summary subtab inside modal
            switchDetailTab("summary");
        } catch (err) {
            console.error("Failed to fetch incident detail:", err);
        }
    };

    document.getElementById("btn-close-modal").addEventListener("click", () => {
        document.getElementById("modal-incident").classList.add("hidden");
        activeIncidentId = null;
    });

    // Modal Subtabs
    const detailTabs = document.querySelectorAll(".detail-tab");
    const detailPanels = document.querySelectorAll(".detail-panel");

    detailTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const dtab = tab.getAttribute("data-dtab");
            switchDetailTab(dtab);
        });
    });

    async function switchDetailTab(dtab) {
        detailTabs.forEach(t => {
            if (t.getAttribute("data-dtab") === dtab) t.classList.add("active");
            else t.classList.remove("active");
        });

        detailPanels.forEach(p => {
            if (p.id === `dpanel-${dtab}`) p.classList.remove("hidden");
            else p.classList.add("hidden");
        });

        if (!activeIncidentId) return;

        // Fetch sub-data
        if (dtab === "summary") {
            const sum = await api.getIncidentSummary(activeIncidentId);
            document.getElementById("dsum-events").textContent = sum.event_count;
            document.getElementById("dsum-detections").textContent = sum.detection_match_count;
            document.getElementById("dsum-iocs").textContent = sum.ioc_count;
            document.getElementById("dsum-mitre").textContent = sum.mitre_technique_count;
        } else if (dtab === "timeline") {
            const tl = await api.getIncidentTimeline(activeIncidentId);
            const container = document.getElementById("timeline-container");
            if (!tl.timeline || tl.timeline.length === 0) {
                container.innerHTML = `<div class="text-center py-6 text-dark-400">No timeline items recorded</div>`;
            } else {
                container.innerHTML = tl.timeline.map(item => `
                    <div class="p-3 bg-dark-800 rounded border border-dark-700">
                        <div class="flex justify-between items-center text-xs mb-1">
                            <span class="font-mono text-cyan-400 font-bold">${item.type.toUpperCase()}</span>
                            <span class="text-dark-400 font-mono">${formatDate(item.timestamp)}</span>
                        </div>
                        <div class="text-sm font-medium text-light">${escapeHtml(item.summary)}</div>
                    </div>
                `).join("");
            }
        } else if (dtab === "events") {
            const evts = await api.getIncidentEvents(activeIncidentId);
            const tbody = document.querySelector("#table-detail-events tbody");
            tbody.innerHTML = evts.map(e => `
                <tr>
                    <td class="font-mono text-xs text-dark-400">${formatDate(e.timestamp)}</td>
                    <td class="font-mono text-xs text-cyan-400">${e.source}</td>
                    <td class="font-mono text-xs text-dark-300">${e.agent_id || 'N/A'}</td>
                    <td class="font-mono text-xs text-indigo-400">${e.rule_id || 'N/A'}</td>
                    <td class="text-xs">${escapeHtml(e.rule_description || '')}</td>
                </tr>
            `).join("");
        } else if (dtab === "detections") {
            const dets = await api.getIncidentDetections(activeIncidentId);
            const tbody = document.querySelector("#table-detail-detections tbody");
            tbody.innerHTML = dets.map(d => `
                <tr>
                    <td class="font-mono text-xs text-indigo-400">${d.match_reason.rule_id || 'DET'}</td>
                    <td class="font-mono text-xs">${d.match_reason.condition_type}</td>
                    <td class="font-mono text-xs text-dark-400">${formatDate(d.matched_at)}</td>
                    <td class="text-xs font-mono text-dark-300">${escapeHtml(JSON.stringify(d.match_reason))}</td>
                </tr>
            `).join("");
        } else if (dtab === "iocs") {
            const iocs = await api.getIncidentIOCs(activeIncidentId);
            const tbody = document.querySelector("#table-detail-iocs tbody");
            tbody.innerHTML = iocs.map(i => `
                <tr>
                    <td class="font-mono text-xs text-amber-400 font-bold">${i.type.toUpperCase()}</td>
                    <td class="font-mono text-xs">${escapeHtml(i.value)}</td>
                    <td class="font-mono text-xs text-cyan-400">${escapeHtml(i.normalized_value)}</td>
                    <td class="font-mono text-xs">${i.confidence}</td>
                </tr>
            `).join("");
        } else if (dtab === "mitre") {
            const techs = await api.getIncidentMitre(activeIncidentId);
            const tbody = document.querySelector("#table-detail-mitre tbody");
            tbody.innerHTML = techs.map(t => `
                <tr>
                    <td class="font-mono text-xs text-emerald-400 font-bold">${t.technique_id}</td>
                    <td class="font-semibold text-xs">${escapeHtml(t.technique_name)}</td>
                    <td class="text-xs text-dark-300">${escapeHtml(t.tactic)}</td>
                </tr>
            `).join("");
        } else if (dtab === "swarm") {
            await loadSwarmTabContent();
        } else if (dtab === "notes") {
            loadIncidentNotes();
        } else if (dtab === "audit") {
            const audits = await api.getIncidentAudit(activeIncidentId);
            const tbody = document.querySelector("#table-detail-audit tbody");
            tbody.innerHTML = audits.map(a => `
                <tr>
                    <td class="font-mono text-xs text-dark-400">${formatDate(a.timestamp)}</td>
                    <td class="font-mono text-xs text-cyan-400">${escapeHtml(a.actor)}</td>
                    <td class="font-mono text-xs font-bold text-indigo-400">${a.action}</td>
                    <td class="text-xs text-dark-300">${a.field_name || '-'}</td>
                    <td class="text-xs font-mono text-rose-400">${a.old_value || '-'}</td>
                    <td class="text-xs font-mono text-emerald-400">${a.new_value || '-'}</td>
                </tr>
            `).join("");
        }
    }

    // Swarm Tab Content Loader
    async function loadSwarmTabContent() {
        if (!activeIncidentId) return;
        try {
            const swarmData = await api.getSwarmRun(activeIncidentId);
            const riskData = await api.getRiskAssessment(activeIncidentId);

            if (riskData) {
                document.getElementById("dswarm-risk-score").textContent = riskData.risk_score;
                document.getElementById("dswarm-risk-level").textContent = riskData.risk_level;
                const rBadge = document.getElementById("dswarm-risk-level");
                rBadge.className = `badge badge-${riskData.risk_level.toLowerCase()}`;
            }

            if (swarmData && swarmData.status !== "not_analyzed") {
                document.getElementById("dswarm-approval-status-text").textContent = `Approval Status: ${swarmData.human_approval_status.toUpperCase()}`;
                const appBadge = document.getElementById("dswarm-approval-badge");
                if (swarmData.human_approval_required) {
                    appBadge.className = "badge badge-rose";
                    appBadge.textContent = "HUMAN APPROVAL REQUIRED";
                } else {
                    appBadge.className = "badge badge-emerald";
                    appBadge.textContent = "AUTO-APPROVED / NO RISK";
                }

                renderSwarmThoughts(swarmData.thoughts || []);
                renderSwarmActions(swarmData.recommended_actions || []);
            } else {
                document.getElementById("dswarm-thoughts-container").innerHTML = `<div class="text-dark-400 py-4 text-center">Click "Analyze with AI Swarm" above to trigger LangGraph multi-agent reasoning.</div>`;
                document.getElementById("dswarm-actions-container").innerHTML = `<div class="text-dark-400">No containment actions generated yet.</div>`;
            }
        } catch (err) {
            console.error("Failed to load swarm tab content:", err);
        }
    }

    function renderSwarmThoughts(thoughts) {
        const container = document.getElementById("dswarm-thoughts-container");
        if (!thoughts || thoughts.length === 0) {
            container.innerHTML = `<div class="text-dark-400">No agent thoughts recorded.</div>`;
            return;
        }
        container.innerHTML = thoughts.map(t => `
            <div class="p-3 bg-dark-800 rounded border border-dark-700">
                <div class="flex justify-between items-center mb-1">
                    <span class="text-cyan-400 font-bold font-mono">${t.agent_role.toUpperCase()}</span>
                    <span class="text-xs text-dark-400 font-mono">${t.model_used} • Confidence: ${(t.confidence * 100).toFixed(0)}%</span>
                </div>
                <div class="text-sm text-light font-sans mb-2">${escapeHtml(t.summary)}</div>
                ${t.findings && t.findings.length ? `<ul class="list-disc list-inside text-xs text-dark-300 space-y-0.5 font-mono">${t.findings.map(f => `<li>${escapeHtml(f)}</li>`).join("")}</ul>` : ''}
            </div>
        `).join("");
    }

    function renderSwarmActions(actions) {
        const container = document.getElementById("dswarm-actions-container");
        if (!actions || actions.length === 0) {
            container.innerHTML = `<div class="text-dark-400">No containment actions generated.</div>`;
            return;
        }
        container.innerHTML = actions.map((a, idx) => `
            <div class="p-3 bg-dark-800 rounded border border-dark-700 flex justify-between items-center">
                <div>
                    <div class="text-xs font-mono font-bold text-rose-400">${a.action_type} <span class="text-dark-400 font-normal">on target</span> '${escapeHtml(a.target)}'</div>
                    <div class="text-xs text-dark-300 mt-1">${escapeHtml(a.description)}</div>
                </div>
                <div class="flex space-x-2">
                    <button class="btn btn-xs btn-emerald" onclick="approveAction('${a.action_type}', '${escapeHtml(a.target)}')">Approve Action</button>
                    <button class="btn btn-xs btn-cyan" onclick="executeAction('${a.action_type}', '${escapeHtml(a.target)}')">Execute</button>
                </div>
            </div>
        `).join("");
    }

    // Trigger Swarm Button Listener
    document.getElementById("btn-trigger-swarm").addEventListener("click", async () => {
        if (!activeIncidentId) return;
        const btn = document.getElementById("btn-trigger-swarm");
        btn.disabled = true;
        btn.innerHTML = `<span class="animate-pulse">Running Swarm Swarm...</span>`;
        try {
            await api.triggerSwarmAnalysis(activeIncidentId);
            await loadSwarmTabContent();
            // Switch to swarm detail tab
            const sTab = document.querySelector(`.detail-tab[data-dtab="swarm"]`);
            if (sTab) sTab.click();
        } catch (err) {
            alert(`Swarm Execution Error: ${err.message}`);
        } finally {
            btn.disabled = false;
            btn.innerHTML = `<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg><span>Analyze with AI Swarm</span>`;
        }
    });

    window.approveAction = async function(actionType, target) {
        try {
            alert(`Action '${actionType}' on target '${target}' marked APPROVED by Analyst.`);
            loadSwarmTabContent();
        } catch (err) {
            alert(err.message);
        }
    };

    window.executeAction = async function(actionType, target) {
        if (!activeIncidentId) return;
        try {
            const res = await api.executeApprovedAction(actionType, target, activeIncidentId, "SOC Lead Analyst");
            alert(`Response Action Executed Successfully!\nStatus: ${res.execution_result.status}\nCommand: ${actionType}`);
            loadSwarmTabContent();
        } catch (err) {
            alert(`Execution Failed: ${err.message}`);
        }
    };

    // Load AI Swarm View
    async function loadSwarm() {
        try {
            const statusData = await api.getAIStatus();
            document.getElementById("status-ollama").textContent = statusData.ollama_local.available ? `Active (${statusData.ollama_local.model})` : "Offline (Fallback Ready)";
            document.getElementById("status-gemini").textContent = statusData.gemini_cloud.configured ? `Configured (${statusData.gemini_cloud.model})` : "Unconfigured (Ollama/Fallback Active)";
        } catch (err) {
            console.error("Failed to load AI Swarm status:", err);
        }
    }

    // Status & Assignee Workflow Actions
    document.getElementById("action-update-status").addEventListener("change", async (e) => {
        if (!activeIncidentId) return;
        try {
            const newStatus = e.target.value;
            await api.updateIncidentWorkflow(activeIncidentId, { status: newStatus });
            openIncidentDetail(activeIncidentId);
            loadIncidents();
        } catch (err) {
            alert(err.message);
        }
    });

    document.getElementById("btn-save-assignee").addEventListener("click", async () => {
        if (!activeIncidentId) return;
        try {
            const assignee = document.getElementById("action-assignee").value;
            await api.updateIncidentWorkflow(activeIncidentId, { assigned_to: assignee });
            openIncidentDetail(activeIncidentId);
            loadIncidents();
        } catch (err) {
            alert(err.message);
        }
    });

    // Analyst Notes CRUD
    async function loadIncidentNotes() {
        if (!activeIncidentId) return;
        const notes = await api.getIncidentNotes(activeIncidentId);
        const container = document.getElementById("notes-container");
        if (notes.length === 0) {
            container.innerHTML = `<div class="text-center py-6 text-dark-400">No analyst notes recorded yet</div>`;
        } else {
            container.innerHTML = notes.map(n => `
                <div class="p-3 bg-dark-800 rounded border border-dark-700 flex justify-between items-start">
                    <div>
                        <div class="text-xs text-cyan-400 font-mono font-bold mb-1">${escapeHtml(n.author)} • <span class="text-dark-400 font-normal">${formatDate(n.created_at)}</span></div>
                        <div class="text-sm text-light">${escapeHtml(n.content)}</div>
                    </div>
                    <button class="text-xs text-rose-400 hover:text-rose-300" onclick="deleteNote('${n.id}')">Delete</button>
                </div>
            `).join("");
        }
    }

    document.getElementById("btn-add-note").addEventListener("click", async () => {
        if (!activeIncidentId) return;
        const input = document.getElementById("input-new-note");
        if (!input.value.trim()) return;
        try {
            await api.addIncidentNote(activeIncidentId, input.value.trim());
            input.value = "";
            loadIncidentNotes();
        } catch (err) {
            alert(err.message);
        }
    });

    window.deleteNote = async function(noteId) {
        if (!activeIncidentId) return;
        try {
            await api.deleteIncidentNote(activeIncidentId, noteId);
            loadIncidentNotes();
        } catch (err) {
            alert(err.message);
        }
    };

    // ==========================================
    // 4. DETECTIONS VIEW
    // ==========================================
    async function loadDetections() {
        try {
            const rules = await api.getDetectionRules();
            const matches = await api.getDetectionMatches(20);

            // Rules Table
            const tbodyRules = document.querySelector("#table-detection-rules tbody");
            tbodyRules.innerHTML = rules.map(r => `
                <tr>
                    <td class="font-mono text-xs text-indigo-400 font-bold">${r.rule_id}</td>
                    <td class="font-semibold text-xs">${escapeHtml(r.name)}</td>
                    <td class="font-mono text-xs text-dark-300">${r.condition_type}</td>
                    <td>${formatSeverityBadge(r.severity)}</td>
                    <td class="font-mono text-xs text-emerald-400">${r.mitre_technique_id || 'N/A'}</td>
                    <td><span class="badge badge-emerald">ENABLED</span></td>
                </tr>
            `).join("");

            // Matches Table
            const tbodyMatches = document.querySelector("#table-detection-matches tbody");
            if (matches.length === 0) {
                tbodyMatches.innerHTML = `<tr><td colspan="6" class="text-center py-6 text-dark-400">No detection matches generated yet</td></tr>`;
            } else {
                tbodyMatches.innerHTML = matches.map(m => `
                    <tr>
                        <td class="font-mono text-xs text-cyan-400">${m.id.substring(0, 8)}...</td>
                        <td class="font-mono text-xs font-bold text-indigo-400">${m.match_reason.rule_id || 'DET'}</td>
                        <td class="font-mono text-xs text-dark-300">${m.incident_id ? m.incident_id.substring(0, 8) + '...' : 'N/A'}</td>
                        <td class="font-mono text-xs text-dark-400">${formatDate(m.matched_at)}</td>
                        <td class="font-mono text-xs text-center">${m.event_count}</td>
                        <td class="font-mono text-xs text-dark-300">${escapeHtml(JSON.stringify(m.match_reason))}</td>
                    </tr>
                `).join("");
            }
        } catch (err) {
            console.error("Failed to load detections:", err);
        }
    }

    // ==========================================
    // 5. INTELLIGENCE VIEW
    // ==========================================
    async function loadIntelligence() {
        const subTabs = document.querySelectorAll(".sub-tab");
        subTabs.forEach(st => {
            st.addEventListener("click", () => {
                const targetSub = st.getAttribute("data-subtab");
                subTabs.forEach(t => t.classList.remove("active"));
                st.classList.add("active");

                if (targetSub === "iocs") {
                    document.getElementById("subpanel-iocs").classList.remove("hidden");
                    document.getElementById("subpanel-mitre").classList.add("hidden");
                } else {
                    document.getElementById("subpanel-iocs").classList.add("hidden");
                    document.getElementById("subpanel-mitre").classList.remove("hidden");
                }
            });
        });

        try {
            const iocs = await api.getIOCs(50);
            const mitre = await api.getMitreCatalog();

            const tbodyIocs = document.querySelector("#table-iocs tbody");
            if (iocs.length === 0) {
                tbodyIocs.innerHTML = `<tr><td colspan="5" class="text-center py-6 text-dark-400">No extracted IOCs recorded yet</td></tr>`;
            } else {
                tbodyIocs.innerHTML = iocs.map(i => `
                    <tr>
                        <td class="font-mono text-xs text-amber-400 font-bold">${i.type.toUpperCase()}</td>
                        <td class="font-mono text-xs text-light">${escapeHtml(i.value)}</td>
                        <td class="font-mono text-xs text-cyan-400">${escapeHtml(i.normalized_value)}</td>
                        <td class="font-mono text-xs">${i.confidence}</td>
                        <td class="text-xs text-dark-400">${formatDate(i.first_seen)}</td>
                    </tr>
                `).join("");
            }

            const tbodyMitre = document.querySelector("#table-mitre tbody");
            tbodyMitre.innerHTML = mitre.map(m => `
                <tr>
                    <td class="font-mono text-xs text-emerald-400 font-bold">${m.technique_id}</td>
                    <td class="font-semibold text-xs">${escapeHtml(m.technique_name)}</td>
                    <td class="text-xs text-dark-300 font-mono">${escapeHtml(m.tactic)}</td>
                    <td class="text-xs text-dark-400">${escapeHtml(m.description)}</td>
                </tr>
            `).join("");
        } catch (err) {
            console.error("Failed to load intelligence:", err);
        }
    }

    // ==========================================
    // 6. WAZUH VIEW
    // ==========================================
    async function loadWazuh() {
        try {
            const agents = await api.getWazuhAgents(20);
            const tbody = document.querySelector("#table-wazuh-agents tbody");

            const agentList = agents.items || agents;
            if (!agentList || agentList.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="text-center py-6 text-dark-400">No Wazuh agents registered</td></tr>`;
            } else {
                tbody.innerHTML = agentList.map(a => `
                    <tr>
                        <td class="font-mono text-xs text-cyan-400 font-bold">${a.id}</td>
                        <td class="font-semibold text-xs">${escapeHtml(a.name)}</td>
                        <td class="font-mono text-xs text-dark-300">${a.ip || '127.0.0.1'}</td>
                        <td><span class="badge ${a.status === 'active' ? 'badge-emerald' : 'badge-low'}">${a.status ? a.status.toUpperCase() : 'ACTIVE'}</span></td>
                        <td class="font-mono text-xs text-dark-400">${a.version || 'Wazuh 4.14.7'}</td>
                        <td class="text-xs text-dark-400">${a.lastKeepAlive || 'Just now'}</td>
                    </tr>
                `).join("");
            }
        } catch (err) {
            console.error("Failed to load Wazuh info:", err);
        }
    }

    // --- Helper Functions ---
    function formatSeverityBadge(sev) {
        const s = (sev || 'medium').toLowerCase();
        return `<span class="badge badge-${s}">${s.toUpperCase()}</span>`;
    }

    function formatStatusBadge(status) {
        const st = (status || 'open').toUpperCase();
        return `<span class="badge badge-outline">${st}</span>`;
    }

    function formatDate(dateStr) {
        if (!dateStr) return 'N/A';
        try {
            const d = new Date(dateStr);
            return d.toLocaleString();
        } catch (e) {
            return dateStr;
        }
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});

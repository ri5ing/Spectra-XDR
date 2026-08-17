/**
 * Centralized API Client for SPECTRA-XDR SOC Console.
 * Encapsulates all backend REST API endpoints. Zero Wazuh credentials or JWT tokens in client.
 */

class ApiClient {
    constructor(baseUrl = "/api/v1") {
        this.baseUrl = baseUrl;
    }

    async _request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const defaultHeaders = { "Content-Type": "application/json" };
        const config = {
            ...options,
            headers: { ...defaultHeaders, ...options.headers }
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
                try {
                    const errJson = await response.json();
                    if (errJson.detail) errorMsg = errJson.detail;
                } catch (e) { }
                throw new Error(errorMsg);
            }
            if (response.status === 204) return null;
            return await response.json();
        } catch (err) {
            console.error(`[ApiClient Error] ${options.method || 'GET'} ${url}:`, err);
            throw err;
        }
    }

    // 1. Dashboard API
    async getDashboardSummary() {
        return await this._request("/dashboard/summary");
    }

    // 2. Incidents & Investigation APIs
    async getIncidents(params = {}) {
        const query = new URLSearchParams();
        if (params.limit) query.append("limit", params.limit);
        if (params.offset) query.append("offset", params.offset);
        if (params.status) query.append("status", params.status);
        if (params.severity) query.append("severity", params.severity);
        if (params.assigned_to) query.append("assigned_to", params.assigned_to);

        const qStr = query.toString();
        return await this._request(`/incidents${qStr ? '?' + qStr : ''}`);
    }

    async getIncident(incidentId) {
        return await this._request(`/incidents/${incidentId}`);
    }

    async getIncidentSummary(incidentId) {
        return await this._request(`/incidents/${incidentId}/summary`);
    }

    async getIncidentEvents(incidentId, params = {}) {
        const query = new URLSearchParams(params);
        const qStr = query.toString();
        return await this._request(`/incidents/${incidentId}/events${qStr ? '?' + qStr : ''}`);
    }

    async getIncidentDetections(incidentId) {
        return await this._request(`/incidents/${incidentId}/detections`);
    }

    async getIncidentIOCs(incidentId) {
        return await this._request(`/incidents/${incidentId}/iocs`);
    }

    async getIncidentMitre(incidentId) {
        return await this._request(`/incidents/${incidentId}/mitre`);
    }

    async getIncidentTimeline(incidentId) {
        return await this._request(`/incidents/${incidentId}/timeline`);
    }

    async getIncidentEvidence(incidentId) {
        return await this._request(`/incidents/${incidentId}/evidence`);
    }

    async updateIncidentWorkflow(incidentId, payload) {
        return await this._request(`/incidents/${incidentId}`, {
            method: "PATCH",
            body: JSON.stringify(payload)
        });
    }

    // 3. Analyst Notes APIs
    async getIncidentNotes(incidentId) {
        return await this._request(`/incidents/${incidentId}/notes`);
    }

    async addIncidentNote(incidentId, content, author = "analyst") {
        return await this._request(`/incidents/${incidentId}/notes`, {
            method: "POST",
            body: JSON.stringify({ content, author })
        });
    }

    async updateIncidentNote(incidentId, noteId, content, author = "analyst") {
        return await this._request(`/incidents/${incidentId}/notes/${noteId}`, {
            method: "PATCH",
            body: JSON.stringify({ content, author })
        });
    }

    async deleteIncidentNote(incidentId, noteId) {
        return await this._request(`/incidents/${incidentId}/notes/${noteId}`, {
            method: "DELETE"
        });
    }

    async getIncidentAudit(incidentId) {
        return await this._request(`/incidents/${incidentId}/audit`);
    }

    // 4. Detections APIs
    async getDetectionRules() {
        return await this._request("/detections/rules");
    }

    async getDetectionMatches(limit = 20) {
        return await this._request(`/detections/matches?limit=${limit}`);
    }

    async runDetectionPipeline(ruleId = null) {
        return await this._request("/detections/run", {
            method: "POST",
            body: JSON.stringify({ rule_id: ruleId })
        });
    }

    // 5. Intelligence APIs
    async getIOCs(limit = 50, type = null) {
        let endpoint = `/intelligence/iocs?limit=${limit}`;
        if (type) endpoint += `&type=${type}`;
        return await this._request(endpoint);
    }

    async getMitreCatalog() {
        return await this._request("/intelligence/mitre");
    }

    // 6. Wazuh Operational APIs
    async getWazuhHealth() {
        return await this._request("/wazuh/health");
    }

    async getWazuhAgents(limit = 20) {
        return await this._request(`/wazuh/agents?limit=${limit}`);
    }

    async getWazuhAlerts(limit = 20) {
        return await this._request(`/wazuh/alerts?limit=${limit}`);
    }
}

const api = new ApiClient();

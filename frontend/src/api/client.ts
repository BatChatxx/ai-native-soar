// 使用原生 fetch，避免 axios 在浏览器环境引用 process 的坑
const BASE = '/api/v1'

export interface Incident {
  id: number
  number: string
  title: string
  description: string | null
  severity: string
  status: string
  priority: string
  source_type: string
  detection_id: string | null
  detection_source: string | null
  created_at: string
  updated_at: string
}

export interface IncidentInput {
  title: string
  description?: string
  severity?: string
  status?: string
  priority?: string
  source_type?: string
  auto_enrich?: boolean
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

export async function listIncidents(params?: {
  status?: string
  severity?: string
}): Promise<Incident[]> {
  const qs = new URLSearchParams()
  if (params?.status) qs.set('status', params.status)
  if (params?.severity) qs.set('severity', params.severity)
  const suffix = qs.toString() ? `?${qs.toString()}` : ''
  return request<Incident[]>(`/incidents${suffix}`)
}

export async function getIncident(id: number): Promise<Incident> {
  return request<Incident>(`/incidents/${id}`)
}

export interface IncidentEvent {
  id: number
  title: string
  description: string | null
  timestamp: string | null
}

export interface IncidentComment {
  id: number
  content: string
  created_at: string | null
}

export interface Observable {
  id: number
  observable_type: string
  observable_value: string
  severity: string | null
  enrichment_status: string | null
  malicious_score: number | null
  reputation: string | null
  enrichment_data: {
    score: number
    reputation: string
    tags: string[]
    source: string
  } | null
  enriched_at: string | null
  created_at: string | null
}

export interface QAItem {
  id: number
  question: string
  answer: string
  created_at: string | null
}

export interface IncidentDetail extends Incident {
  source_alert: { id: number; number: string; title: string } | null
  events: IncidentEvent[]
  comments: IncidentComment[]
  observables: Observable[]
  qa_history: QAItem[]
}

export async function getIncidentDetail(id: number): Promise<IncidentDetail> {
  return request<IncidentDetail>(`/incidents/${id}`)
}

export function addIncidentEvent(
  id: number,
  data: { title: string; description?: string }
): Promise<IncidentEvent> {
  return request<IncidentEvent>(`/incidents/${id}/events`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function addIncidentComment(
  id: number,
  content: string
): Promise<IncidentComment> {
  return request<IncidentComment>(`/incidents/${id}/comments`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  })
}

export function extractObservables(id: number): Promise<{
  added: number
  observables: { type: string; value: string }[]
}> {
  return request(`/incidents/${id}/observables/extract`, { method: 'POST' })
}

export function enrichObservables(id: number): Promise<{
  enriched: number
  results: {
    id: number
    observable_type: string
    observable_value: string
    malicious_score: number
    reputation: string
    tags: string[]
  }[]
}> {
  return request(`/incidents/${id}/observables/enrich`, { method: 'POST' })
}

export function addObservable(
  id: number,
  data: { observable_type: string; observable_value: string }
): Promise<Observable> {
  return request<Observable>(`/incidents/${id}/observables`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function deleteObservable(
  incidentId: number,
  observableId: number
): Promise<void> {
  await fetch(`${BASE}/incidents/${incidentId}/observables/${observableId}`, {
    method: 'DELETE',
  })
}

export function createIncident(data: IncidentInput): Promise<Incident & { auto_extracted?: number }> {
  return request<Incident & { auto_extracted?: number }>('/incidents', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function updateIncident(
  id: number,
  data: Partial<IncidentInput>
): Promise<Incident> {
  return request<Incident>(`/incidents/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteIncident(id: number): Promise<void> {
  await fetch(`${BASE}/incidents/${id}`, { method: 'DELETE' })
}

// ---------- Alerts ----------

export interface Alert {
  id: number
  number: string
  title: string
  description: string | null
  severity: string
  status: string
  source_type: string
  source_id: string | null
  detection_id: string | null
  incident_id: number | null
  created_at: string
  updated_at: string
}

export interface AlertInput {
  title: string
  description?: string
  severity?: string
  status?: string
  source_type?: string
  source_id?: string
  detection_id?: string
  auto_enrich?: boolean
}

export async function listAlerts(params?: {
  status?: string
  severity?: string
}): Promise<Alert[]> {
  const qs = new URLSearchParams()
  if (params?.status) qs.set('status', params.status)
  if (params?.severity) qs.set('severity', params.severity)
  const suffix = qs.toString() ? `?${qs.toString()}` : ''
  return request<Alert[]>(`/alerts${suffix}`)
}

export function createAlert(data: AlertInput): Promise<Alert & { auto_extracted?: number }> {
  return request<Alert & { auto_extracted?: number }>('/alerts', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function updateAlert(
  id: number,
  data: Partial<AlertInput>
): Promise<Alert> {
  return request<Alert>(`/alerts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteAlert(id: number): Promise<void> {
  await fetch(`${BASE}/alerts/${id}`, { method: 'DELETE' })
}

export async function promoteAlert(id: number): Promise<{
  incident_id: number
  incident_number: string
  alert_id: number
}> {
  return request(`/alerts/${id}/promote`, { method: 'POST' })
}

export interface AlertDetail extends Alert {
  observables: Observable[]
  qa_history: QAItem[]
}

export async function getAlertDetail(id: number): Promise<AlertDetail> {
  return request<AlertDetail>(`/alerts/${id}`)
}

export function extractAlertObservables(id: number): Promise<{
  added: number
  observables: { type: string; value: string }[]
}> {
  return request(`/alerts/${id}/observables/extract`, { method: 'POST' })
}

export function enrichAlertObservables(id: number): Promise<{
  enriched: number
  results: {
    id: number
    observable_type: string
    observable_value: string
    malicious_score: number
    reputation: string
  }[]
}> {
  return request(`/alerts/${id}/observables/enrich`, { method: 'POST' })
}

export function addAlertObservable(
  id: number,
  data: { observable_type: string; observable_value: string }
): Promise<Observable> {
  return request<Observable>(`/alerts/${id}/observables`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function deleteAlertObservable(
  alertId: number,
  observableId: number
): Promise<void> {
  await fetch(`${BASE}/alerts/${alertId}/observables/${observableId}`, {
    method: 'DELETE',
  })
}

// ---------- Dashboard ----------

export interface DashboardSummary {
  totals: {
    incidents: number
    alerts: number
    critical: number
    malicious_observables: number
  }
  severity_counts: Record<string, number>
  status_counts: Record<string, number>
  alert_status_counts: Record<string, number>
  observable_stats: {
    malicious: number
    suspicious: number
    clean: number
    unknown: number
    total: number
  }
  recent_incidents: {
    id: number
    number: string
    title: string
    severity: string
    status: string
    created_at: string | null
  }[]
  recent_alerts: {
    id: number
    number: string
    title: string
    severity: string
    status: string
    created_at: string | null
  }[]
}

export function getDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>('/dashboard/summary')
}

// ---------- AI Analysis ----------

export function analyzeIncident(id: number): Promise<{ incident_id: number; summary: string }> {
  return request(`/incidents/${id}/analyze`, { method: 'POST' })
}

export function analyzeAlert(id: number): Promise<{ alert_id: number; summary: string }> {
  return request(`/alerts/${id}/analyze`, { method: 'POST' })
}

export function askIncident(
  id: number,
  question: string
): Promise<{ incident_id: number; question: string; answer: string }> {
  return request(`/incidents/${id}/ask`, {
    method: 'POST',
    body: JSON.stringify({ question }),
  })
}

export function askAlert(
  id: number,
  question: string
): Promise<{ alert_id: number; question: string; answer: string }> {
  return request(`/alerts/${id}/ask`, {
    method: 'POST',
    body: JSON.stringify({ question }),
  })
}

// ---------- Settings ----------

export interface SettingsHealth {
  status: string
  database: { connected: boolean }
  llm: { connected: boolean; message: string }
  counts: {
    incidents: number
    alerts: number
    observables: number
  }
  timestamp: string
}

export interface LLMProfile {
  id: number
  name: string
  base_url: string
  model: string
  api_key: string
  context_window: number
  is_active: boolean
  created_at: string | null
  updated_at: string | null
}

export interface LLMProfileList {
  active_profile_id: number | null
  profiles: LLMProfile[]
}

export function getSettingsHealth(): Promise<SettingsHealth> {
  return request<SettingsHealth>('/settings/health')
}

export function getLLMProfiles(): Promise<LLMProfileList> {
  return request<LLMProfileList>('/settings/llm')
}

export function createLLMProfile(data: {
  name: string
  base_url: string
  model: string
  api_key?: string
  context_window?: number
}): Promise<LLMProfile> {
  return request<LLMProfile>('/settings/llm', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function updateLLMProfile(
  id: number,
  data: Partial<{ name: string; base_url: string; model: string; api_key: string; context_window: number }>
): Promise<LLMProfile> {
  return request<LLMProfile>(`/settings/llm/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export function deleteLLMProfile(id: number): Promise<{ message: string; id: number }> {
  return request(`/settings/llm/${id}`, { method: 'DELETE' })
}

export function activateLLMProfile(id: number): Promise<{ message: string; id: number; is_active: boolean }> {
  return request(`/settings/llm/${id}/activate`, { method: 'POST' })
}

// ---------- Auth ----------

export interface LoginResult {
  access_token: string
  token_type: string
  username: string
  is_superuser: boolean
}

export function login(username: string, password: string): Promise<LoginResult> {
  return request<LoginResult>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export function changePassword(
  current_password: string,
  new_password: string
): Promise<{ message: string }> {
  return request('/auth/change-password', {
    method: 'POST',
    body: JSON.stringify({ current_password, new_password }),
  })
}

export function getMe(): Promise<{
  username: string
  email: string
  full_name: string
  is_superuser: boolean
}> {
  return request('/auth/me')
}

// ---------- Phishing analysis ----------

export interface PhishingAuthResults {
  spf: string | null
  dkim: string | null
  dmarc: string | null
  raw: string | null
}

export interface PhishingAnalysisResult {
  filename: string
  size: number
  parsed: {
    subject: string
    sender: string
    to: string
    cc: string | null
    date: string
    message_id: string
    return_path: string
    routing: { raw: string; ip: string | null; from: string | null }[]
    auth_results: PhishingAuthResults
    text_body: string
    html_body: string
    urls: string[]
    attachments: { filename: string; content_type: string }[]
  }
  indicators: {
    domains: string[]
    ips: string[]
    urls: string[]
  }
  dns: Record<string, { domain: string; a_records: string[]; mx_records: string[]; error: string | null }>
  scored: { type: string; value: string; score: number; reputation: string }[]
  verdict: { is_likely_phishing: boolean }
}

export async function analyzePhishingEmail(file: File): Promise<PhishingAnalysisResult> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${BASE}/phishing/analyze`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => null)
    throw new Error(err?.detail || `Upload failed: ${res.status}`)
  }
  return res.json()
}

export async function aiPhishingAnalysis(
  parsed: PhishingAnalysisResult['parsed'],
  indicators: PhishingAnalysisResult['indicators'],
  scored: PhishingAnalysisResult['scored']
): Promise<{ analysis: string }> {
  return request('/phishing/ai-analysis', {
    method: 'POST',
    body: JSON.stringify({ parsed, indicators, scored }),
  })
}

export function createIncidentFromPhishing(data: {
  subject: string
  sender: string
  indicators: { domains: string[]; ips: string[]; urls: string[] }
  ai_analysis: string
}): Promise<{ incident_id: number; incident_number: string; title: string }> {
  return request('/phishing/create-incident', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

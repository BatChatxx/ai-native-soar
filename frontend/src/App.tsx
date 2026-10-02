import React from 'react'
import { Routes, Route, Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import {
  Incident,
  IncidentInput,
  IncidentDetail,
  listIncidents,
  createIncident,
  updateIncident,
  deleteIncident,
  getIncidentDetail,
  addIncidentEvent,
  addIncidentComment,
  Observable,
  extractObservables,
  enrichObservables,
  addObservable,
  deleteObservable,
  Alert,
  AlertInput,
  AlertDetail,
  listAlerts,
  createAlert,
  updateAlert,
  deleteAlert,
  promoteAlert,
  getAlertDetail,
  extractAlertObservables,
  enrichAlertObservables,
  addAlertObservable,
  deleteAlertObservable,
  DashboardSummary,
  getDashboardSummary,
  analyzeIncident,
  analyzeAlert,
  askIncident,
  askAlert,
  SettingsHealth,
  LLMProfileList,
  LLMProfile,
  getSettingsHealth,
  getLLMProfiles,
  createLLMProfile,
  updateLLMProfile,
  deleteLLMProfile,
  activateLLMProfile,
  LoginResult,
  login,
  changePassword,
  getMe,
  PhishingAnalysisResult,
  analyzePhishingEmail,
  aiPhishingAnalysis,
  createIncidentFromPhishing,
} from './api/client'

type Tab = 'dashboard' | 'incidents' | 'alerts' | 'phishing' | 'settings'

const SEVERITY_COLORS: Record<string, string> = {
  critical: '#dc2626',
  high: '#ea580c',
  medium: '#ca8a04',
  low: '#16a34a',
}

const SEVERITY_OPTIONS = ['critical', 'high', 'medium', 'low']
const INCIDENT_STATUS_OPTIONS = ['open', 'investigating', 'containment', 'resolved', 'closed']
const ALERT_STATUS_OPTIONS = ['new', 'acknowledged', 'promoted', 'resolved', 'closed']
const SOURCE_OPTIONS = ['manual', 'SIEM', 'EDR', 'Email', 'User Report', 'Other']

const OBSERVABLE_TYPES = ['ip', 'domain', 'url', 'hash_md5', 'hash_sha1', 'hash_sha256', 'file', 'process', 'ethereum_contract', 'arweave_drive_id']

// Preset AI questions shown in detail pages
const INCIDENT_PRESET_QUESTIONS = [
  '总结这次攻击链',
  '评估严重性和影响范围',
  '推荐优先处置步骤',
  '提取关键 IOC 并说明为什么这些最需要关注',
  '最关键的检测盲点是什么？',
]

const ALERT_PRESET_QUESTIONS = [
  '这是否是真阳性？',
  '推荐分诊步骤',
  '是否该升级为 incident？',
  '最紧急的遏制动作是什么？',
]

const OBSERVABLE_COLORS: Record<string, string> = {
  ip: '#2563eb',
  domain: '#7c3aed',
  url: '#0891b2',
  hash_md5: '#d97706',
  hash_sha1: '#d97706',
  hash_sha256: '#d97706',
  file: '#059669',
  process: '#dc2626',
  ethereum_contract: '#9333ea',
  arweave_drive_id: '#0d9488',
}

export default function App() {
  const [user, setUser] = React.useState<string | null>(() => localStorage.getItem('soar_username'))

  const handleLogin = (username: string) => {
    localStorage.setItem('soar_username', username)
    setUser(username)
  }

  const handleLogout = () => {
    localStorage.removeItem('soar_username')
    localStorage.removeItem('soar_token')
    setUser(null)
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f3f4f6', color: '#111827' }}>
      <Header user={user} onLogout={handleLogout} />
      <main style={{ maxWidth: '1100px', margin: '0 auto', padding: '1.5rem' }}>
        <Routes>
          <Route path="/login" element={<LoginView onLogin={handleLogin} />} />
          <Route path="/" element={<DashboardView />} />
          <Route path="/incidents" element={<IncidentsView />} />
          <Route path="/incidents/:id" element={<IncidentDetailRoute />} />
          <Route path="/alerts" element={<AlertsView />} />
          <Route path="/alerts/:id" element={<AlertDetailRoute />} />
          <Route path="/phishing" element={<PhishingView />} />
          <Route path="/settings" element={<SettingsView />} />
          <Route path="*" element={<DashboardView />} />
        </Routes>
      </main>
    </div>
  )
}

function Header({ user, onLogout }: { user: string | null; onLogout: () => void }) {
  const location = useLocation()
  const active = (path: string) => (location.pathname === path || location.pathname.startsWith(path + '/'))

  const tabs: { id: Tab; path: string; label: string }[] = [
    { id: 'dashboard', path: '/', label: 'Dashboard' },
    { id: 'incidents', path: '/incidents', label: 'Incidents' },
    { id: 'alerts', path: '/alerts', label: 'Alerts' },
    { id: 'phishing', path: '/phishing', label: 'Phishing' },
    { id: 'settings', path: '/settings', label: 'Settings' },
  ]

  return (
    <header
      style={{
        background: '#111827',
        color: '#fff',
        padding: '0 2rem',
        height: '56px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '1.25rem' }}>
        <span style={{ fontSize: '1.25rem', fontWeight: 700 }}>AI-Native SOAR</span>
        <span style={{ fontSize: '0.8rem', color: '#9ca3af' }}>Dashboard</span>
        <nav style={{ display: 'flex', gap: '0.25rem', marginLeft: '1rem' }}>
          {tabs.map((t) => (
            <Link
              key={t.id}
              to={t.path}
              style={{
                background: active(t.path) ? '#2563eb' : 'transparent',
                color: '#fff',
                textDecoration: 'none',
                padding: '0.4rem 0.9rem',
                borderRadius: '6px',
                fontSize: '0.9rem',
                fontWeight: 600,
              }}
            >
              {t.label}
            </Link>
          ))}
        </nav>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {user ? (
          <>
            <span style={{ fontSize: '0.85rem', color: '#d1d5db' }}>
              👤 {user}
            </span>
            <button
              onClick={onLogout}
              style={{ background: 'transparent', color: '#9ca3af', border: '1px solid #374151', borderRadius: '6px', padding: '0.3rem 0.7rem', fontSize: '0.8rem', cursor: 'pointer' }}
            >
              Logout
            </button>
          </>
        ) : (
          <Link
            to="/login"
            style={{ color: '#fff', textDecoration: 'none', fontSize: '0.85rem', fontWeight: 600 }}
          >
            Login
          </Link>
        )}
      </div>
    </header>
  )
}

// ===================== Phishing View =====================

function PhishingView() {
  const [result, setResult] = React.useState<PhishingAnalysisResult | null>(null)
  const [aiText, setAiText] = React.useState<string | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [aiLoading, setAiLoading] = React.useState(false)
  const [promoteMsg, setPromoteMsg] = React.useState<string | null>(null)
  const [error, setError] = React.useState<string | null>(null)
  const fileInput = React.useRef<HTMLInputElement>(null)

  const handleFile = async (file: File) => {
    setLoading(true)
    setError(null)
    setResult(null)
    setAiText(null)
    try {
      setResult(await analyzePhishingEmail(file))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const handleAI = async () => {
    if (!result) return
    setAiLoading(true)
    setAiText(null)
    try {
      const res = await aiPhishingAnalysis(result.parsed, result.indicators, result.scored)
      setAiText(res.analysis)
    } catch (e) {
      setAiText(e instanceof Error ? `AI analysis failed: ${e.message}` : 'AI analysis failed')
    } finally {
      setAiLoading(false)
    }
  }

  const handleCreateIncident = async () => {
    if (!result) return
    try {
      const res = await createIncidentFromPhishing({
        subject: result.parsed.subject,
        sender: result.parsed.sender,
        indicators: result.indicators,
        ai_analysis: aiText ?? '',
      })
      setPromoteMsg(`Created incident ${res.incident_number}`)
    } catch (e) {
      setPromoteMsg(e instanceof Error ? `Failed: ${e.message}` : 'Failed to create incident')
    }
  }

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Phishing Email Analysis</h2>

      {/* Upload area */}
      <div
        onClick={() => fileInput.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault()
          const f = e.dataTransfer.files?.[0]
          if (f) handleFile(f)
        }}
        style={{
          border: '2px dashed #d1d5db',
          borderRadius: '8px',
          padding: '2rem',
          textAlign: 'center',
          background: '#fff',
          cursor: 'pointer',
          marginBottom: '1rem',
        }}
      >
        <input
          ref={fileInput}
          type="file"
          accept=".eml"
          style={{ display: 'none' }}
          onChange={(e) => {
            const f = e.target.files?.[0]
            if (f) handleFile(f)
          }}
        />
        <div style={{ fontSize: '1.2rem', fontWeight: 600, color: '#374151' }}>
          Drop an .eml file here, or click to select
        </div>
        <div style={{ fontSize: '0.85rem', color: '#6b7280', marginTop: '0.5rem' }}>
          Parses headers, routing, SPF/DKIM/DMARC, extracts IOCs, and scores against threat intel
        </div>
      </div>

      {loading && <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>Analyzing…</div>}
      {error && <div style={{ color: '#dc2626', padding: '1rem' }}>{error}</div>}

      {/* Result */}
      {result && (
        <div>
          {/* Verdict */}
          <div
            style={{
              background: result.verdict.is_likely_phishing ? '#fef2f2' : '#ecfdf5',
              border: `1px solid ${result.verdict.is_likely_phishing ? '#fecaca' : '#bbf7d0'}`,
              borderRadius: '8px',
              padding: '1rem 1.5rem',
              marginBottom: '1rem',
            }}
          >
            <div style={{ fontSize: '1.2rem', fontWeight: 700, color: result.verdict.is_likely_phishing ? '#dc2626' : '#16a34a' }}>
              {result.verdict.is_likely_phishing ? '⚠ Likely Phishing' : '✓ Appears Legitimate'}
            </div>
          </div>

          {/* Basic info */}
          <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)', marginBottom: '1rem' }}>
            <h3 style={{ marginTop: 0 }}>Email Details</h3>
            <InfoRow label="Subject" value={result.parsed.subject} />
            <InfoRow label="From" value={result.parsed.sender} />
            <InfoRow label="To" value={result.parsed.to} />
            <InfoRow label="Date" value={result.parsed.date} />
            <InfoRow label="Return-Path" value={result.parsed.return_path} />
            <InfoRow label="SPF" value={result.parsed.auth_results.spf ?? 'N/A'} />
            <InfoRow label="DKIM" value={result.parsed.auth_results.dkim ?? 'N/A'} />
            <InfoRow label="DMARC" value={result.parsed.auth_results.dmarc ?? 'N/A'} />
            {result.parsed.attachments.length > 0 && (
              <InfoRow label="Attachments" value={result.parsed.attachments.map((a) => a.filename).join(', ')} />
            )}
          </div>

          {/* IOCs & scores */}
          <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)', marginBottom: '1rem' }}>
            <h3 style={{ marginTop: 0 }}>Indicators & Threat Scores</h3>
            <InfoRow label="URLs" value={result.indicators.urls.join(', ') || '(none)'} />
            <div style={{ marginTop: '0.5rem' }}>
              {result.scored.map((s, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.4rem 0', borderBottom: '1px solid #f3f4f6' }}>
                  <span style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{s.type}</span>
                  <span style={{ fontFamily: 'monospace', fontSize: '0.85rem', flex: 1 }}>{s.value}</span>
                  {s.reputation && s.reputation !== 'unknown' && (
                    <Badge
                      text={`${s.reputation} ${s.score}`}
                      color={s.reputation === 'malicious' ? '#dc2626' : s.reputation === 'suspicious' ? '#d97706' : '#16a34a'}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* AI analysis */}
          <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0 }}>AI Analysis</h3>
              <button onClick={handleAI} disabled={aiLoading} style={primaryBtnStyle}>
                {aiLoading ? 'Analyzing…' : aiText ? 'Re-run AI' : 'Analyze with AI'}
              </button>
            </div>
            {aiLoading && <div style={{ color: '#6b7280', marginTop: '0.75rem' }}>Generating analysis…</div>}
            {aiText && (
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, fontSize: '0.9rem', color: '#374151', marginTop: '0.75rem' }}>
                {aiText}
              </div>
            )}

            {/* Convert to incident */}
            <div style={{ marginTop: '1rem', borderTop: '1px solid #f3f4f6', paddingTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <button onClick={handleCreateIncident} style={promoteBtnStyle}>
                Create Incident from this email
              </button>
              {promoteMsg && <span style={{ fontSize: '0.85rem', color: promoteMsg.startsWith('Failed') ? '#dc2626' : '#16a34a' }}>{promoteMsg}</span>}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', gap: '1rem', padding: '0.35rem 0', fontSize: '0.9rem' }}>
      <span style={{ width: '120px', flexShrink: 0, fontWeight: 600, color: '#6b7280' }}>{label}</span>
      <span style={{ flex: 1, wordBreak: 'break-word' }}>{value}</span>
    </div>
  )
}

// ===================== Login View =====================

function LoginView({ onLogin }: { onLogin: (username: string) => void }) {
  const navigate = useNavigate()
  const [username, setUsername] = React.useState('admin')
  const [password, setPassword] = React.useState('')
  const [error, setError] = React.useState<string | null>(null)
  const [loading, setLoading] = React.useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await login(username, password)
      localStorage.setItem('soar_token', res.access_token)
      onLogin(res.username)
      navigate('/')
    } catch (ex) {
      setError(ex instanceof Error ? ex.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem 1rem' }}>
      <div style={{ background: '#fff', borderRadius: '8px', padding: '2rem', maxWidth: '400px', width: '100%', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h2 style={{ marginTop: 0, textAlign: 'center' }}>Sign in</h2>
        <p style={{ textAlign: 'center', color: '#6b7280', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
          Default account: admin / admin
        </p>
        <form onSubmit={handleSubmit}>
          <Field label="Username">
            <input value={username} onChange={(e) => setUsername(e.target.value)} style={inputStyle} />
          </Field>
          <Field label="Password">
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={inputStyle} />
          </Field>
          {error && <div style={{ color: '#dc2626', marginBottom: '0.75rem' }}>{error}</div>}
          <button type="submit" disabled={loading} style={{ ...primaryBtnStyle, width: '100%' }}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}

// ===================== Settings View =====================

function SettingsView() {
  const [health, setHealth] = React.useState<SettingsHealth | null>(null)
  const [profiles, setProfiles] = React.useState<LLMProfileList | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [showForm, setShowForm] = React.useState(false)
  const [editingProfile, setEditingProfile] = React.useState<LLMProfile | null>(null)

  const load = React.useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [h, p] = await Promise.all([getSettingsHealth(), getLLMProfiles()])
      setHealth(h)
      setProfiles(p)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load settings')
    } finally {
      setLoading(false)
    }
  }, [])

  React.useEffect(() => {
    load()
  }, [load])

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>Loading…</div>
  }
  if (error || !health || !profiles) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#dc2626' }}>Error: {error}</div>
  }

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Settings</h2>

      {/* Health & status */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
        <HealthCard
          label="System Status"
          value={health.status}
          color={health.status === 'ok' ? '#16a34a' : '#d97706'}
        />
        <HealthCard
          label="Database"
          value={health.database.connected ? 'Connected' : 'Disconnected'}
          color={health.database.connected ? '#16a34a' : '#dc2626'}
        />
        <HealthCard
          label="LLM"
          value={health.llm.connected ? 'Connected' : 'Disconnected'}
          color={health.llm.connected ? '#16a34a' : '#dc2626'}
          sub={health.llm.message}
        />
      </div>

      {/* Data counts */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <StatCard label="Incidents" value={health.counts.incidents} color="#111827" />
        <StatCard label="Alerts" value={health.counts.alerts} color="#7c3aed" />
        <StatCard label="Observables" value={health.counts.observables} color="#2563eb" />
      </div>

      {/* LLM Profiles */}
      <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ margin: 0 }}>LLM Profiles</h3>
          <button onClick={() => { setShowForm(true); setEditingProfile(null) }} style={primaryBtnStyle}>
            + Add Profile
          </button>
        </div>

        {profiles.profiles.length === 0 ? (
          <p style={{ color: '#6b7280' }}>No LLM profiles configured.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {profiles.profiles.map((p) => (
              <div
                key={p.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.75rem 1rem',
                  border: p.is_active ? '1px solid #2563eb' : '1px solid #e5e7eb',
                  borderRadius: '6px',
                  background: p.is_active ? '#eff6ff' : '#fff',
                }}
              >
                <div>
                  <div style={{ fontWeight: 600 }}>
                    {p.name}
                    {p.is_active && (
                      <span style={{ marginLeft: '0.5rem', fontSize: '0.7rem', color: '#2563eb', fontWeight: 700 }}>
                        ● ACTIVE
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>
                    {p.model} · {p.base_url} · {p.context_window} ctx
                  </div>
                  {p.api_key && <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>key: {p.api_key}</div>}
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  {!p.is_active && (
                    <button
                      onClick={async () => { await activateLLMProfile(p.id); load() }}
                      style={{ ...secondaryBtnStyle, fontSize: '0.8rem' }}
                    >
                      Activate
                    </button>
                  )}
                  <button
                    onClick={() => { setEditingProfile(p); setShowForm(true) }}
                    style={{ ...secondaryBtnStyle, fontSize: '0.8rem' }}
                  >
                    Edit
                  </button>
                  <button
                    onClick={async () => {
                      if (confirm(`Delete profile "${p.name}"?`)) {
                        await deleteLLMProfile(p.id)
                        load()
                      }
                    }}
                    style={{ ...secondaryBtnStyle, fontSize: '0.8rem', color: '#dc2626' }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Account */}
      <AccountSection />

      {/* Profile form modal */}
      {showForm && (
        <LLMProfileForm
          profile={editingProfile}
          onCancel={() => { setShowForm(false); setEditingProfile(null) }}
          onSaved={() => { setShowForm(false); setEditingProfile(null); load() }}
        />
      )}
    </div>
  )
}

function AccountSection() {
  const [me, setMe] = React.useState<{ username: string; email: string; full_name: string; is_superuser: boolean } | null>(null)
  const [currentPw, setCurrentPw] = React.useState('')
  const [newPw, setNewPw] = React.useState('')
  const [msg, setMsg] = React.useState<string | null>(null)
  const [err, setErr] = React.useState<string | null>(null)
  const [saving, setSaving] = React.useState(false)

  React.useEffect(() => {
    getMe().then(setMe).catch(() => {})
  }, [])

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setErr(null)
    setMsg(null)
    try {
      await changePassword(currentPw, newPw)
      setMsg('Password changed successfully')
      setCurrentPw('')
      setNewPw('')
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : 'Failed to change password')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)', marginTop: '1.5rem' }}>
      <h3 style={{ marginTop: 0 }}>Account</h3>
      {me && (
        <div style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '1rem' }}>
          Signed in as <strong>{me.username}</strong> ({me.email})
          {me.is_superuser && ' · Superuser'}
        </div>
      )}

      <form onSubmit={handleChangePassword} style={{ maxWidth: '400px' }}>
        <Field label="Current Password">
          <input type="password" value={currentPw} onChange={(e) => setCurrentPw(e.target.value)} style={inputStyle} />
        </Field>
        <Field label="New Password">
          <input type="password" value={newPw} onChange={(e) => setNewPw(e.target.value)} style={inputStyle} />
        </Field>
        {msg && <div style={{ color: '#16a34a', marginBottom: '0.5rem', fontSize: '0.85rem' }}>{msg}</div>}
        {err && <div style={{ color: '#dc2626', marginBottom: '0.5rem', fontSize: '0.85rem' }}>{err}</div>}
        <button type="submit" disabled={saving || !currentPw || !newPw} style={primaryBtnStyle}>
          {saving ? 'Changing…' : 'Change Password'}
        </button>
      </form>
    </div>
  )
}

function HealthCard({ label, value, color, sub }: { label: string; value: string; color: string; sub?: string }) {
  return (
    <div style={{ background: '#fff', borderRadius: '8px', padding: '1rem 1.25rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)' }}>
      <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{label}</div>
      <div style={{ fontSize: '1.5rem', fontWeight: 700, color }}>{value}</div>
      {sub && <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '0.25rem' }}>{sub}</div>}
    </div>
  )
}

function LLMProfileForm({
  profile,
  onCancel,
  onSaved,
}: {
  profile: LLMProfile | null
  onCancel: () => void
  onSaved: () => void
}) {
  const [form, setForm] = React.useState({
    name: profile?.name ?? '',
    base_url: profile?.base_url ?? '',
    model: profile?.model ?? '',
    api_key: profile?.api_key ?? '',
    context_window: profile?.context_window ?? 40000,
  })
  const [saving, setSaving] = React.useState(false)
  const [err, setErr] = React.useState<string | null>(null)

  const set = (key: string, value: string | number) =>
    setForm((prev) => ({ ...prev, [key]: value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setErr(null)
    try {
      const payload = {
        name: form.name,
        base_url: form.base_url,
        model: form.model,
        // Only send api_key if provided (empty keeps existing on update)
        ...(form.api_key ? { api_key: form.api_key } : {}),
        context_window: Number(form.context_window),
      }
      if (profile) {
        await updateLLMProfile(profile.id, payload)
      } else {
        await createLLMProfile(payload)
      }
      onSaved()
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
      <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', maxWidth: '480px', width: '100%', boxShadow: '0 10px 30px rgba(0,0,0,0.2)' }}>
        <h3 style={{ marginTop: 0 }}>{profile ? 'Edit LLM Profile' : 'Add LLM Profile'}</h3>
        <form onSubmit={handleSubmit}>
          <Field label="Name *">
            <input required value={form.name} onChange={(e) => set('name', e.target.value)} style={inputStyle} placeholder="e.g. Local Qwen 3.5" />
          </Field>
          <Field label="Base URL *">
            <input required value={form.base_url} onChange={(e) => set('base_url', e.target.value)} style={inputStyle} placeholder="http://host.docker.internal:56987" />
          </Field>
          <Field label="Model *">
            <input required value={form.model} onChange={(e) => set('model', e.target.value)} style={inputStyle} placeholder="qwen/qwen3.5-9b" />
          </Field>
          <Field label={`API Key ${profile ? '(leave blank to keep existing)' : ''}`}>
            <input value={form.api_key} onChange={(e) => set('api_key', e.target.value)} style={inputStyle} placeholder="sk-lm-..." />
          </Field>
          <Field label="Context Window (tokens)">
            <input type="number" value={form.context_window} onChange={(e) => set('context_window', Number(e.target.value))} style={inputStyle} />
          </Field>

          {err && <div style={{ color: '#dc2626', marginBottom: '0.75rem' }}>{err}</div>}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
            <button type="button" onClick={onCancel} style={secondaryBtnStyle}>Cancel</button>
            <button type="submit" disabled={saving} style={primaryBtnStyle}>
              {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ===================== Dashboard View =====================

function DashboardView() {
  const [summary, setSummary] = React.useState<DashboardSummary | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    let cancelled = false
    getDashboardSummary()
      .then((s) => {
        if (!cancelled) setSummary(s)
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>Loading…</div>
  }
  if (error || !summary) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#dc2626' }}>Error: {error}</div>
  }

  const severities = ['critical', 'high', 'medium', 'low']
  const maxSeverity = Math.max(1, ...severities.map((s) => summary.severity_counts[s] ?? 0))

  const obs = summary.observable_stats
  const obsTotal = Math.max(1, obs.total)

  return (
    <div>
      {/* Top summary cards */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <StatCard label="Incidents" value={summary.totals.incidents} color="#111827" />
        <StatCard label="Alerts" value={summary.totals.alerts} color="#7c3aed" />
        <StatCard label="Critical" value={summary.totals.critical} color="#dc2626" />
        <StatCard label="Malicious IOCs" value={summary.totals.malicious_observables} color="#ea580c" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        {/* Severity distribution */}
        <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)' }}>
          <h3 style={{ marginTop: 0 }}>Incident Severity Distribution</h3>
          {severities.map((s) => {
            const count = summary.severity_counts[s] ?? 0
            const pct = (count / maxSeverity) * 100
            return (
              <div key={s} style={{ marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                  <span style={{ textTransform: 'capitalize', color: '#374151' }}>{s}</span>
                  <span style={{ fontWeight: 600, color: SEVERITY_COLORS[s] }}>{count}</span>
                </div>
                <div style={{ height: '8px', background: '#f3f4f6', borderRadius: '999px', overflow: 'hidden' }}>
                  <div style={{ width: `${pct}%`, height: '100%', background: SEVERITY_COLORS[s], borderRadius: '999px', transition: 'width 0.3s' }} />
                </div>
              </div>
            )
          })}
        </div>

        {/* Observable reputation breakdown */}
        <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)' }}>
          <h3 style={{ marginTop: 0 }}>Observable Reputation</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <ReputationDonut obs={obs} />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {[
                { key: 'malicious', label: 'Malicious', color: '#dc2626' },
                { key: 'suspicious', label: 'Suspicious', color: '#d97706' },
                { key: 'clean', label: 'Clean', color: '#16a34a' },
                { key: 'unknown', label: 'Unknown', color: '#9ca3af' },
              ].map((r) => {
                const val = obs[r.key as 'malicious' | 'suspicious' | 'clean' | 'unknown'] ?? 0
                return (
                  <div key={r.key} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: r.color }} />
                    <span style={{ fontSize: '0.85rem', color: '#374151' }}>{r.label}</span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{val}</span>
                  </div>
                )
              })}
            </div>
          </div>
          <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: '#6b7280' }}>
            Total observables: {obs.total}
          </div>
        </div>
      </div>

      {/* Recent activity */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <RecentList title="Recent Incidents" items={summary.recent_incidents.map((i) => ({
          id: i.id,
          number: i.number,
          title: i.title,
          severity: i.severity,
          time: i.created_at,
        }))} />
        <RecentList title="Recent Alerts" items={summary.recent_alerts.map((a) => ({
          id: a.id,
          number: a.number,
          title: a.title,
          severity: a.severity,
          time: a.created_at,
        }))} />
      </div>
    </div>
  )
}

function ReputationDonut({ obs }: { obs: { malicious: number; suspicious: number; clean: number; unknown: number; total: number } }) {
  const total = Math.max(1, obs.total)
  const segments = [
    { key: 'malicious', color: '#dc2626' },
    { key: 'suspicious', color: '#d97706' },
    { key: 'clean', color: '#16a34a' },
    { key: 'unknown', color: '#9ca3af' },
  ]
  const r = 40
  const c = 2 * Math.PI * r
  let offset = 0

  return (
    <svg width="120" height="120" viewBox="0 0 120 120">
      <circle cx="60" cy="60" r={r} fill="none" stroke="#f3f4f6" strokeWidth="18" />
      {segments.map((seg) => {
        const val = obs[seg.key as 'malicious' | 'suspicious' | 'clean' | 'unknown'] ?? 0
        const frac = val / total
        const dash = frac * c
        const el = (
          <circle
            key={seg.key}
            cx="60"
            cy="60"
            r={r}
            fill="none"
            stroke={seg.color}
            strokeWidth="18"
            strokeDasharray={`${dash} ${c - dash}`}
            strokeDashoffset={-offset}
            transform="rotate(-90 60 60)"
          />
        )
        offset += dash
        return el
      })}
      <text x="60" y="65" textAnchor="middle" fontSize="20" fontWeight="700" fill="#111827">
        {obs.total}
      </text>
    </svg>
  )
}

function RecentList({ title, items }: { title: string; items: { id: number; number: string; title: string; severity: string; time: string | null }[] }) {
  return (
    <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)' }}>
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      {items.length === 0 ? (
        <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>None yet.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {items.map((it) => (
            <li key={it.id} style={{ padding: '0.6rem 0', borderBottom: '1px solid #f3f4f6' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: '#6b7280' }}>{it.number}</span>
                <Badge text={it.severity ?? '—'} color={SEVERITY_COLORS[it.severity] ?? '#6b7280'} />
              </div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem', marginTop: '0.2rem' }}>{it.title}</div>
              <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                {it.time ? new Date(it.time).toLocaleString() : ''}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

// ===================== Incidents View =====================

function IncidentsView() {
  const navigate = useNavigate()
  const [items, setItems] = React.useState<Incident[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [mode, setMode] = React.useState<'list' | 'create' | 'edit'>('list')
  const [editing, setEditing] = React.useState<Incident | null>(null)
  const [fSeverity, setFSeverity] = React.useState('')
  const [fStatus, setFStatus] = React.useState('')
  const [notice, setNotice] = React.useState<string | null>(null)

  const refresh = React.useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setItems(
        await listIncidents({
          ...(fSeverity ? { severity: fSeverity } : {}),
          ...(fStatus ? { status: fStatus } : {}),
        })
      )
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load')
    } finally {
      setLoading(false)
    }
  }, [fSeverity, fStatus])

  React.useEffect(() => {
    refresh()
  }, [refresh])

  const stats = {
    total: items.length,
    critical: items.filter((i) => i.severity === 'critical').length,
    open: items.filter((i) => i.status === 'open').length,
  }

  return (
    <div>
      <ViewStats
        totalLabel="Total Incidents"
        total={stats.total}
        critLabel="Critical"
        crit={stats.critical}
        openLabel="Open"
        open={stats.open}
        onCreate={() => {
          setEditing(null)
          setMode('create')
        }}
        createLabel="+ New Incident"
      />

      <FilterBar
        severity={fSeverity}
        status={fStatus}
        statusOptions={INCIDENT_STATUS_OPTIONS}
        onSeverity={setFSeverity}
        onStatus={setFStatus}
      />

      {notice && (
        <div style={{ background: '#ecfdf5', color: '#065f46', padding: '0.75rem 1rem', borderRadius: '6px', marginBottom: '1rem', fontSize: '0.9rem' }}>
          ✅ {notice}
        </div>
      )}

      {mode === 'list' ? (
        <IncidentTable
          items={items}
          loading={loading}
          error={error}
          onOpen={(inc) => navigate(`/incidents/${inc.id}`)}
          onEdit={(inc) => {
            setEditing(inc)
            setMode('edit')
          }}
          onDelete={async (id) => {
            await deleteIncident(id)
            refresh()
          }}
        />
      ) : (
        <IncidentForm
          incident={editing}
          onCancel={() => {
            setMode('list')
            setEditing(null)
          }}
          onSaved={(msg) => {
            setMode('list')
            setEditing(null)
            if (msg) setNotice(msg)
            refresh()
          }}
        />
      )}
    </div>
  )
}

// ===================== Alerts View =====================

function AlertsView() {
  const navigate = useNavigate()
  const [items, setItems] = React.useState<Alert[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [mode, setMode] = React.useState<'list' | 'create' | 'edit'>('list')
  const [editing, setEditing] = React.useState<Alert | null>(null)
  const [fSeverity, setFSeverity] = React.useState('')
  const [fStatus, setFStatus] = React.useState('')
  const [lastAction, setLastAction] = React.useState<string | null>(null)

  const refresh = React.useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setItems(
        await listAlerts({
          ...(fSeverity ? { severity: fSeverity } : {}),
          ...(fStatus ? { status: fStatus } : {}),
        })
      )
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load')
    } finally {
      setLoading(false)
    }
  }, [fSeverity, fStatus])

  React.useEffect(() => {
    refresh()
  }, [refresh])

  const stats = {
    total: items.length,
    critical: items.filter((i) => i.severity === 'critical').length,
    new_: items.filter((i) => i.status === 'new').length,
  }

  return (
    <div>
      <ViewStats
        totalLabel="Total Alerts"
        total={stats.total}
        critLabel="Critical"
        crit={stats.critical}
        openLabel="New"
        open={stats.new_}
        onCreate={() => {
          setEditing(null)
          setMode('create')
        }}
        createLabel="+ New Alert"
      />

      <FilterBar
        severity={fSeverity}
        status={fStatus}
        statusOptions={ALERT_STATUS_OPTIONS}
        onSeverity={setFSeverity}
        onStatus={setFStatus}
      />

      {lastAction && (
        <div
          style={{
            background: '#ecfdf5',
            color: '#065f46',
            padding: '0.75rem 1rem',
            borderRadius: '6px',
            marginBottom: '1rem',
          }}
        >
          {lastAction}
        </div>
      )}

      {mode === 'list' ? (
        <AlertTable
          items={items}
          loading={loading}
          error={error}
          onOpen={(a) => navigate(`/alerts/${a.id}`)}
          onEdit={(a) => {
            setEditing(a)
            setMode('edit')
          }}
          onDelete={async (id) => {
            await deleteAlert(id)
            refresh()
          }}
          onPromote={async (a) => {
            const res = await promoteAlert(a.id)
            setLastAction(
              `Alert ${a.number} promoted to incident ${res.incident_number}`
            )
            refresh()
          }}
        />
      ) : (
        <AlertForm
          alert={editing}
          onCancel={() => {
            setMode('list')
            setEditing(null)
          }}
          onSaved={(msg) => {
            setMode('list')
            setEditing(null)
            if (msg) setLastAction(msg)
            refresh()
          }}
        />
      )}
    </div>
  )
}

// ===================== Shared UI =====================

function ViewStats({
  totalLabel,
  total,
  critLabel,
  crit,
  openLabel,
  open,
  onCreate,
  createLabel,
}: {
  totalLabel: string
  total: number
  critLabel: string
  crit: number
  openLabel: string
  open: number
  onCreate: () => void
  createLabel: string
}) {
  return (
    <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
      <StatCard label={totalLabel} value={total} color="#111827" />
      <StatCard label={critLabel} value={crit} color="#dc2626" />
      <StatCard label={openLabel} value={open} color="#2563eb" />
      <button
        onClick={onCreate}
        style={{
          background: '#2563eb',
          color: '#fff',
          border: 'none',
          padding: '0 1.25rem',
          borderRadius: '8px',
          fontWeight: 600,
          cursor: 'pointer',
          fontSize: '0.95rem',
        }}
      >
        {createLabel}
      </button>
    </div>
  )
}

function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div
      style={{
        flex: 1,
        background: '#fff',
        borderRadius: '8px',
        padding: '1rem 1.25rem',
        boxShadow: '0 1px 2px rgba(0,0,0,0.06)',
      }}
    >
      <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{label}</div>
      <div style={{ fontSize: '1.75rem', fontWeight: 700, color }}>{value}</div>
    </div>
  )
}

function FilterBar({
  severity,
  status,
  statusOptions,
  onSeverity,
  onStatus,
}: {
  severity: string
  status: string
  statusOptions: string[]
  onSeverity: (v: string) => void
  onStatus: (v: string) => void
}) {
  return (
    <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}>
      <select value={severity} onChange={(e) => onSeverity(e.target.value)} style={filterSelectStyle}>
        <option value="">All severities</option>
        {SEVERITY_OPTIONS.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
      <select value={status} onChange={(e) => onStatus(e.target.value)} style={filterSelectStyle}>
        <option value="">All statuses</option>
        {statusOptions.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
    </div>
  )
}

function IncidentTable({
  items,
  loading,
  error,
  onOpen,
  onEdit,
  onDelete,
}: {
  items: Incident[]
  loading: boolean
  error: string | null
  onOpen: (inc: Incident) => void
  onEdit: (inc: Incident) => void
  onDelete: (id: number) => void
}) {
  if (loading) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>Loading…</div>
  }
  if (error) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#dc2626' }}>Error: {error}</div>
  }
  if (items.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>
        No incidents found. Click “+ New Incident” to create one.
      </div>
    )
  }

  return (
    <TableWrapper>
      <thead>
        <tr style={{ background: '#f9fafb', textAlign: 'left' }}>
          <Th>Number</Th>
          <Th>Title</Th>
          <Th>Severity</Th>
          <Th>Status</Th>
          <Th>Source</Th>
          <Th>Created</Th>
          <Th></Th>
        </tr>
      </thead>
      <tbody>
        {items.map((inc) => (
          <tr key={inc.id} style={{ borderTop: '1px solid #e5e7eb' }}>
            <Td>
              <span style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{inc.number}</span>
            </Td>
            <Td>
              <div
                onClick={() => onOpen(inc)}
                style={{ fontWeight: 600, color: '#2563eb', cursor: 'pointer' }}
                title="View details"
              >
                {inc.title}
              </div>
              {inc.description && (
                <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>
                  {inc.description.slice(0, 60)}
                </div>
              )}
            </Td>
            <Td>
              <Badge text={inc.severity ?? '—'} color={SEVERITY_COLORS[inc.severity] ?? '#6b7280'} />
            </Td>
            <Td>
              <span style={{ fontSize: '0.85rem' }}>{inc.status}</span>
            </Td>
            <Td>
              <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>{inc.source_type}</span>
            </Td>
            <Td>
              <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                {new Date(inc.created_at).toLocaleString()}
              </span>
            </Td>
            <Td style={{ padding: '0.5rem', textAlign: 'right', whiteSpace: 'nowrap' }}>
              <button onClick={() => onEdit(inc)} style={actionBtnStyle}>
                Edit
              </button>
              <button
                onClick={() => {
                  if (confirm(`Delete ${inc.number}?`)) onDelete(inc.id)
                }}
                style={{ ...actionBtnStyle, color: '#dc2626' }}
              >
                Delete
              </button>
            </Td>
          </tr>
        ))}
      </tbody>
    </TableWrapper>
  )
}

function AlertTable({
  items,
  loading,
  error,
  onOpen,
  onEdit,
  onDelete,
  onPromote,
}: {
  items: Alert[]
  loading: boolean
  error: string | null
  onOpen: (a: Alert) => void
  onEdit: (a: Alert) => void
  onDelete: (id: number) => void
  onPromote: (a: Alert) => void
}) {
  if (loading) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>Loading…</div>
  }
  if (error) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#dc2626' }}>Error: {error}</div>
  }
  if (items.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>
        No alerts found. Click “+ New Alert” to create one.
      </div>
    )
  }

  return (
    <TableWrapper>
      <thead>
        <tr style={{ background: '#f9fafb', textAlign: 'left' }}>
          <Th>Number</Th>
          <Th>Title</Th>
          <Th>Severity</Th>
          <Th>Status</Th>
          <Th>Source</Th>
          <Th>Created</Th>
          <Th></Th>
        </tr>
      </thead>
      <tbody>
        {items.map((a) => (
          <tr key={a.id} style={{ borderTop: '1px solid #e5e7eb' }}>
            <Td>
              <span style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{a.number}</span>
            </Td>
            <Td>
              <div
                onClick={() => onOpen(a)}
                style={{ fontWeight: 600, color: '#2563eb', cursor: 'pointer' }}
                title="View details"
              >
                {a.title}
              </div>
              {a.description && (
                <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>
                  {a.description.slice(0, 60)}
                </div>
              )}
            </Td>
            <Td>
              <Badge text={a.severity ?? '—'} color={SEVERITY_COLORS[a.severity] ?? '#6b7280'} />
            </Td>
            <Td>
              <span style={{ fontSize: '0.85rem' }}>{a.status}</span>
              {a.incident_id && (
                <div style={{ fontSize: '0.75rem', color: '#2563eb' }}>
                  → incident #{a.incident_id}
                </div>
              )}
            </Td>
            <Td>
              <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>{a.source_type}</span>
            </Td>
            <Td>
              <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                {new Date(a.created_at).toLocaleString()}
              </span>
            </Td>
            <Td style={{ padding: '0.5rem', textAlign: 'right', whiteSpace: 'nowrap' }}>
              {!a.incident_id && (
                <button onClick={() => onPromote(a)} style={promoteBtnStyle}>
                  Promote
                </button>
              )}
              <button onClick={() => onEdit(a)} style={actionBtnStyle}>
                Edit
              </button>
              <button
                onClick={() => {
                  if (confirm(`Delete ${a.number}?`)) onDelete(a.id)
                }}
                style={{ ...actionBtnStyle, color: '#dc2626' }}
              >
                Delete
              </button>
            </Td>
          </tr>
        ))}
      </tbody>
    </TableWrapper>
  )
}

function IncidentDetailRoute() {
  const { id } = useParams()
  const navigate = useNavigate()
  const incidentId = Number(id)
  if (!Number.isFinite(incidentId)) {
    return <div style={{ color: '#dc2626' }}>Invalid incident id</div>
  }
  return <IncidentDetailView id={incidentId} onBack={() => navigate('/incidents')} />
}

function AlertDetailRoute() {
  const { id } = useParams()
  const navigate = useNavigate()
  const alertId = Number(id)
  if (!Number.isFinite(alertId)) {
    return <div style={{ color: '#dc2626' }}>Invalid alert id</div>
  }
  return <AlertDetailView id={alertId} onBack={() => navigate('/alerts')} />
}

function IncidentDetailView({
  id,
  onBack,
}: {
  id: number
  onBack: () => void
}) {
  const [detail, setDetail] = React.useState<IncidentDetail | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [status, setStatus] = React.useState('')
  const [eventTitle, setEventTitle] = React.useState('')
  const [commentText, setCommentText] = React.useState('')
  const [obsType, setObsType] = React.useState('ip')
  const [obsValue, setObsValue] = React.useState('')
  const [extractMsg, setExtractMsg] = React.useState('')
  const [enrichMsg, setEnrichMsg] = React.useState('')
  const [aiSummary, setAiSummary] = React.useState<string | null>(null)
  const [aiLoading, setAiLoading] = React.useState(false)
  const [qa, setQa] = React.useState<{ question: string; answer: string }[]>([])
  const [question, setQuestion] = React.useState('')
  const [qaLoading, setQaLoading] = React.useState(false)

  const load = React.useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const d = await getIncidentDetail(id)
      setDetail(d)
      setStatus(d.status)
      setQa((d.qa_history || []).map((h) => ({ question: h.question, answer: h.answer })))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load')
    } finally {
      setLoading(false)
    }
  }, [id])

  React.useEffect(() => {
    load()
  }, [load])

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>Loading…</div>
  }
  if (error || !detail) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#dc2626' }}>Error: {error}</div>
  }

  const changeStatus = async (newStatus: string) => {
    await updateIncident(id, { status: newStatus })
    setStatus(newStatus)
    load()
  }

  const submitEvent = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!eventTitle.trim()) return
    await addIncidentEvent(id, { title: eventTitle })
    setEventTitle('')
    load()
  }

  const submitComment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!commentText.trim()) return
    await addIncidentComment(id, commentText)
    setCommentText('')
    load()
  }

  const handleExtract = async () => {
    const res = await extractObservables(id)
    setExtractMsg(`Extracted ${res.added} new observable(s)`)
    load()
  }

  const handleEnrich = async () => {
    const res = await enrichObservables(id)
    const malicious = res.results.filter((r) => r.reputation === 'malicious').length
    setEnrichMsg(`Enriched ${res.enriched} observable(s): ${malicious} malicious`)
    load()
  }

  const handleAnalyze = async () => {
    setAiLoading(true)
    setAiSummary(null)
    try {
      const res = await analyzeIncident(id)
      setAiSummary(res.summary)
    } catch (e) {
      setAiSummary(e instanceof Error ? `Analysis failed: ${e.message}` : 'Analysis failed')
    } finally {
      setAiLoading(false)
    }
  }

  const askQuestion = async (q: string) => {
    const trimmed = q.trim()
    if (!trimmed || qaLoading) return
    setQaLoading(true)
    try {
      const res = await askIncident(id, trimmed)
      setQa((prev) => [...prev, { question: trimmed, answer: res.answer }])
      setQuestion('')
    } catch (ex) {
      setQa((prev) => [...prev, { question: trimmed, answer: `Error: ${ex instanceof Error ? ex.message : 'failed'}` }])
    } finally {
      setQaLoading(false)
    }
  }

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault()
    await askQuestion(question)
  }

  const submitObservable = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!obsValue.trim()) return
    await addObservable(id, { observable_type: obsType, observable_value: obsValue })
    setObsValue('')
    load()
  }

  return (
    <div>
      <button onClick={onBack} style={{ ...secondaryBtnStyle, marginBottom: '1rem' }}>
        ← Back to Incidents
      </button>

      {/* Header card */}
      <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '0.5rem' }}>
          <span style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#6b7280' }}>{detail.number}</span>
          <Badge text={detail.severity ?? '—'} color={SEVERITY_COLORS[detail.severity] ?? '#6b7280'} />
          <Badge text={detail.priority ?? '—'} color="#6b7280" />
          <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>● {status}</span>
        </div>
        <h2 style={{ margin: '0 0 0.5rem 0' }}>{detail.title}</h2>
        {detail.description && (
          <p style={{ color: '#374151', lineHeight: 1.5, margin: '0 0 1rem 0' }}>{detail.description}</p>
        )}

        <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.85rem', color: '#6b7280', flexWrap: 'wrap' }}>
          <span>Source: <strong>{detail.source_type}</strong></span>
          {detail.detection_id && <span>Detection: <strong>{detail.detection_id}</strong></span>}
          <span>Created: <strong>{new Date(detail.created_at).toLocaleString()}</strong></span>
          <span>Updated: <strong>{new Date(detail.updated_at).toLocaleString()}</strong></span>
        </div>

        {detail.source_alert && (
          <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#fef3c7', borderRadius: '6px', fontSize: '0.85rem' }}>
            ⚠ Promoted from alert <strong>{detail.source_alert.number}</strong> — {detail.source_alert.title}
          </div>
        )}
      </div>

      {/* AI Analysis */}
      <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0 }}>AI Analysis Summary</h3>
          <button onClick={handleAnalyze} disabled={aiLoading} style={{ ...primaryBtnStyle, fontSize: '0.85rem' }}>
            {aiLoading ? 'Analyzing…' : aiSummary ? 'Re-run Analysis' : 'Analyze with AI'}
          </button>
        </div>
        {aiLoading && (
          <div style={{ marginTop: '0.75rem', color: '#6b7280', fontSize: '0.9rem' }}>
            Generating analysis… this may take a moment.
          </div>
        )}
        {aiSummary && !aiLoading && (
          <div style={{ marginTop: '0.75rem', whiteSpace: 'pre-wrap', lineHeight: 1.6, fontSize: '0.9rem', color: '#374151' }}>
            {aiSummary}
          </div>
        )}

        {/* Q&A: ask custom questions */}
        <div style={{ marginTop: '1rem', borderTop: '1px solid #f3f4f6', paddingTop: '1rem' }}>
          <div style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: '0.5rem' }}>
            Ask a follow-up question (uses full incident context)
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '0.75rem' }}>
            {INCIDENT_PRESET_QUESTIONS.map((preset) => (
              <button
                key={preset}
                type="button"
                onClick={() => askQuestion(preset)}
                disabled={qaLoading}
                style={{
                  background: '#eff6ff',
                  color: '#1d4ed8',
                  border: '1px solid #bfdbfe',
                  borderRadius: '999px',
                  padding: '0.25rem 0.75rem',
                  fontSize: '0.8rem',
                  cursor: qaLoading ? 'default' : 'pointer',
                  fontWeight: 500,
                }}
              >
                {preset}
              </button>
            ))}
          </div>

          {qa.map((item, idx) => (
            <div key={idx} style={{ marginBottom: '0.75rem' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#2563eb' }}>
                Q: {item.question}
              </div>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, fontSize: '0.85rem', color: '#374151', marginTop: '0.25rem' }}>
                {item.answer}
              </div>
            </div>
          ))}

          <form onSubmit={handleAsk} style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. What are the detection gaps? What should I contain first?"
              style={{ ...inputStyle, flex: 1 }}
            />
            <button type="submit" disabled={qaLoading} style={primaryBtnStyle}>
              {qaLoading ? 'Thinking…' : 'Ask'}
            </button>
          </form>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        {/* Timeline / events */}
        <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)' }}>
          <h3 style={{ marginTop: 0 }}>Timeline</h3>
          {detail.events.length === 0 ? (
            <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>No events yet.</p>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {detail.events.map((ev) => (
                <li key={ev.id} style={{ padding: '0.75rem 0', borderBottom: '1px solid #f3f4f6' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{ev.title}</div>
                  {ev.description && <div style={{ fontSize: '0.85rem', color: '#6b7280' }}>{ev.description}</div>}
                  <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                    {ev.timestamp ? new Date(ev.timestamp).toLocaleString() : ''}
                  </div>
                </li>
              ))}
            </ul>
          )}
          <form onSubmit={submitEvent} style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
            <input
              value={eventTitle}
              onChange={(e) => setEventTitle(e.target.value)}
              placeholder="Add event…"
              style={{ ...inputStyle, flex: 1 }}
            />
            <button type="submit" style={primaryBtnStyle}>Add</button>
          </form>
        </div>

        {/* Comments */}
        <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)' }}>
          <h3 style={{ marginTop: 0 }}>Comments</h3>
          {detail.comments.length === 0 ? (
            <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>No comments yet.</p>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {detail.comments.map((c) => (
                <li key={c.id} style={{ padding: '0.75rem 0', borderBottom: '1px solid #f3f4f6' }}>
                  <div style={{ fontSize: '0.9rem' }}>{c.content}</div>
                  <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                    {c.created_at ? new Date(c.created_at).toLocaleString() : ''}
                  </div>
                </li>
              ))}
            </ul>
          )}
          <form onSubmit={submitComment} style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
            <input
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Add comment…"
              style={{ ...inputStyle, flex: 1 }}
            />
            <button type="submit" style={primaryBtnStyle}>Post</button>
          </form>
        </div>
      </div>

      {/* Observables */}
      <div style={{ marginTop: '1rem', background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}>
          <h3 style={{ margin: 0 }}>Observables (IOCs)</h3>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button onClick={handleEnrich} style={{ ...secondaryBtnStyle, fontSize: '0.8rem' }}>
              Enrich
            </button>
            <button onClick={handleExtract} style={{ ...secondaryBtnStyle, fontSize: '0.8rem' }}>
              Extract from description
            </button>
          </div>
        </div>
        {extractMsg && <div style={{ marginTop: '0.5rem', color: '#065f46', fontSize: '0.85rem' }}>{extractMsg}</div>}
        {enrichMsg && <div style={{ marginTop: '0.5rem', color: '#065f46', fontSize: '0.85rem' }}>{enrichMsg}</div>}

        {detail.observables.length === 0 ? (
          <p style={{ color: '#6b7280', fontSize: '0.9rem', marginTop: '0.75rem' }}>
            No observables. Click “Extract from description” or add manually below.
          </p>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem' }}>
            {detail.observables.map((o) => {
              const rep = o.reputation
              const scoreColor =
                rep === 'malicious' ? '#dc2626' : rep === 'suspicious' ? '#d97706' : rep === 'clean' ? '#16a34a' : '#6b7280'
              const borderColor =
                rep === 'malicious' ? '#fecaca' : rep === 'suspicious' ? '#fde68a' : '#e5e7eb'
              return (
                <span
                  key={o.id}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    background: rep === 'malicious' ? '#fef2f2' : rep === 'suspicious' ? '#fffbeb' : '#f3f4f6',
                    border: `1px solid ${borderColor}`,
                    borderRadius: '6px',
                    padding: '0.3rem 0.6rem',
                    fontSize: '0.8rem',
                  }}
                >
                  <span
                    style={{
                      fontWeight: 700,
                      color: OBSERVABLE_COLORS[o.observable_type] ?? '#6b7280',
                      textTransform: 'uppercase',
                      fontSize: '0.7rem',
                    }}
                  >
                    {o.observable_type}
                  </span>
                  <span style={{ fontFamily: 'monospace' }}>{o.observable_value}</span>
                  {o.reputation && o.reputation !== 'unknown' && (
                    <span
                      style={{
                        fontWeight: 700,
                        fontSize: '0.7rem',
                        color: scoreColor,
                        border: `1px solid ${scoreColor}`,
                        borderRadius: '999px',
                        padding: '1px 6px',
                      }}
                    >
                      {o.reputation} {o.malicious_score ?? ''}
                    </span>
                  )}
                  <button
                    onClick={async () => {
                      await deleteObservable(id, o.id)
                      load()
                    }}
                    style={{ background: 'none', border: 'none', color: '#dc2626', cursor: 'pointer', fontWeight: 700 }}
                    title="Remove"
                  >
                    ×
                  </button>
                </span>
              )
            })}
          </div>
        )}

        <form onSubmit={submitObservable} style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
          <select value={obsType} onChange={(e) => setObsType(e.target.value)} style={{ ...inputStyle, width: 'auto' }}>
            {OBSERVABLE_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <input
            value={obsValue}
            onChange={(e) => setObsValue(e.target.value)}
            placeholder="Add observable manually…"
            style={{ ...inputStyle, flex: 1 }}
          />
          <button type="submit" style={primaryBtnStyle}>Add</button>
        </form>
      </div>

      {/* Quick status change */}
      <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>Change status:</span>
        {INCIDENT_STATUS_OPTIONS.filter((s) => s !== status).map((s) => (
          <button
            key={s}
            onClick={() => changeStatus(s)}
            style={{ ...secondaryBtnStyle, fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}


function AlertDetailView({
  id,
  onBack,
}: {
  id: number
  onBack: () => void
}) {
  const [detail, setDetail] = React.useState<AlertDetail | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [obsType, setObsType] = React.useState('ip')
  const [obsValue, setObsValue] = React.useState('')
  const [msg, setMsg] = React.useState('')
  const [aiSummary, setAiSummary] = React.useState<string | null>(null)
  const [aiLoading, setAiLoading] = React.useState(false)
  const [qa, setQa] = React.useState<{ question: string; answer: string }[]>([])
  const [question, setQuestion] = React.useState('')
  const [qaLoading, setQaLoading] = React.useState(false)

  const load = React.useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const d = await getAlertDetail(id)
      setDetail(d)
      setQa((d.qa_history || []).map((h) => ({ question: h.question, answer: h.answer })))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load')
    } finally {
      setLoading(false)
    }
  }, [id])

  React.useEffect(() => {
    load()
  }, [load])

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>Loading…</div>
  }
  if (error || !detail) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#dc2626' }}>Error: {error}</div>
  }

  const handleExtract = async () => {
    const res = await extractAlertObservables(id)
    setMsg(`Extracted ${res.added} new observable(s)`)
    load()
  }

  const handleEnrich = async () => {
    const res = await enrichAlertObservables(id)
    const malicious = res.results.filter((r) => r.reputation === 'malicious').length
    setMsg(`Enriched ${res.enriched} observable(s): ${malicious} malicious`)
    load()
  }

  const handlePromote = async () => {
    const res = await promoteAlert(id)
    setMsg(`Promoted to incident ${res.incident_number}`)
    load()
  }

  const handleAnalyze = async () => {
    setAiLoading(true)
    setAiSummary(null)
    try {
      const res = await analyzeAlert(id)
      setAiSummary(res.summary)
    } catch (e) {
      setAiSummary(e instanceof Error ? `Analysis failed: ${e.message}` : 'Analysis failed')
    } finally {
      setAiLoading(false)
    }
  }

  const askQuestion = async (q: string) => {
    const trimmed = q.trim()
    if (!trimmed || qaLoading) return
    setQaLoading(true)
    try {
      const res = await askAlert(id, trimmed)
      setQa((prev) => [...prev, { question: trimmed, answer: res.answer }])
      setQuestion('')
    } catch (ex) {
      setQa((prev) => [...prev, { question: trimmed, answer: `Error: ${ex instanceof Error ? ex.message : 'failed'}` }])
    } finally {
      setQaLoading(false)
    }
  }

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault()
    await askQuestion(question)
  }

  const submitObservable = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!obsValue.trim()) return
    await addAlertObservable(id, { observable_type: obsType, observable_value: obsValue })
    setObsValue('')
    load()
  }

  return (
    <div>
      <button onClick={onBack} style={{ ...secondaryBtnStyle, marginBottom: '1rem' }}>
        ← Back to Alerts
      </button>

      {/* Header card */}
      <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '0.5rem' }}>
          <span style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#6b7280' }}>{detail.number}</span>
          <Badge text={detail.severity ?? '—'} color={SEVERITY_COLORS[detail.severity] ?? '#6b7280'} />
          <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>● {detail.status}</span>
        </div>
        <h2 style={{ margin: '0 0 0.5rem 0' }}>{detail.title}</h2>
        {detail.description && (
          <p style={{ color: '#374151', lineHeight: 1.5, margin: '0 0 1rem 0' }}>{detail.description}</p>
        )}

        <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.85rem', color: '#6b7280', flexWrap: 'wrap' }}>
          <span>Source: <strong>{detail.source_type}</strong></span>
          {detail.source_id && <span>Source ID: <strong>{detail.source_id}</strong></span>}
          <span>Created: <strong>{new Date(detail.created_at).toLocaleString()}</strong></span>
        </div>

        {detail.incident_id ? (
          <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#ecfdf5', borderRadius: '6px', fontSize: '0.85rem' }}>
            ✓ Promoted to incident #{detail.incident_id}
          </div>
        ) : (
          <div style={{ marginTop: '1rem' }}>
            <button onClick={handlePromote} style={promoteBtnStyle}>
              Promote to Incident
            </button>
          </div>
        )}
      </div>

      {/* AI Analysis */}
      <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0 }}>AI Analysis Summary</h3>
          <button onClick={handleAnalyze} disabled={aiLoading} style={{ ...primaryBtnStyle, fontSize: '0.85rem' }}>
            {aiLoading ? 'Analyzing…' : aiSummary ? 'Re-run Analysis' : 'Analyze with AI'}
          </button>
        </div>
        {aiLoading && (
          <div style={{ marginTop: '0.75rem', color: '#6b7280', fontSize: '0.9rem' }}>
            Generating analysis… this may take a moment.
          </div>
        )}
        {aiSummary && !aiLoading && (
          <div style={{ marginTop: '0.75rem', whiteSpace: 'pre-wrap', lineHeight: 1.6, fontSize: '0.9rem', color: '#374151' }}>
            {aiSummary}
          </div>
        )}

        {/* Q&A: ask custom questions */}
        <div style={{ marginTop: '1rem', borderTop: '1px solid #f3f4f6', paddingTop: '1rem' }}>
          <div style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: '0.5rem' }}>
            Ask a follow-up question (uses full alert context)
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '0.75rem' }}>
            {ALERT_PRESET_QUESTIONS.map((preset) => (
              <button
                key={preset}
                type="button"
                onClick={() => askQuestion(preset)}
                disabled={qaLoading}
                style={{
                  background: '#eff6ff',
                  color: '#1d4ed8',
                  border: '1px solid #bfdbfe',
                  borderRadius: '999px',
                  padding: '0.25rem 0.75rem',
                  fontSize: '0.8rem',
                  cursor: qaLoading ? 'default' : 'pointer',
                  fontWeight: 500,
                }}
              >
                {preset}
              </button>
            ))}
          </div>

          {qa.map((item, idx) => (
            <div key={idx} style={{ marginBottom: '0.75rem' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#2563eb' }}>
                Q: {item.question}
              </div>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, fontSize: '0.85rem', color: '#374151', marginTop: '0.25rem' }}>
                {item.answer}
              </div>
            </div>
          ))}

          <form onSubmit={handleAsk} style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. Is this a true positive? What triage steps do you recommend?"
              style={{ ...inputStyle, flex: 1 }}
            />
            <button type="submit" disabled={qaLoading} style={primaryBtnStyle}>
              {qaLoading ? 'Thinking…' : 'Ask'}
            </button>
          </form>
        </div>
      </div>

      {/* Observables */}
      <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}>
          <h3 style={{ margin: 0 }}>Observables (IOCs)</h3>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button onClick={handleEnrich} style={{ ...secondaryBtnStyle, fontSize: '0.8rem' }}>Enrich</button>
            <button onClick={handleExtract} style={{ ...secondaryBtnStyle, fontSize: '0.8rem' }}>Extract from description</button>
          </div>
        </div>
        {msg && <div style={{ marginTop: '0.5rem', color: '#065f46', fontSize: '0.85rem' }}>{msg}</div>}

        {detail.observables.length === 0 ? (
          <p style={{ color: '#6b7280', fontSize: '0.9rem', marginTop: '0.75rem' }}>
            No observables. Click “Extract from description” or add manually below.
          </p>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem' }}>
            {detail.observables.map((o) => {
              const rep = o.reputation
              const scoreColor =
                rep === 'malicious' ? '#dc2626' : rep === 'suspicious' ? '#d97706' : rep === 'clean' ? '#16a34a' : '#6b7280'
              const borderColor =
                rep === 'malicious' ? '#fecaca' : rep === 'suspicious' ? '#fde68a' : '#e5e7eb'
              return (
                <span
                  key={o.id}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    background: rep === 'malicious' ? '#fef2f2' : rep === 'suspicious' ? '#fffbeb' : '#f3f4f6',
                    border: `1px solid ${borderColor}`,
                    borderRadius: '6px',
                    padding: '0.3rem 0.6rem',
                    fontSize: '0.8rem',
                  }}
                >
                  <span style={{ fontWeight: 700, color: OBSERVABLE_COLORS[o.observable_type] ?? '#6b7280', textTransform: 'uppercase', fontSize: '0.7rem' }}>
                    {o.observable_type}
                  </span>
                  <span style={{ fontFamily: 'monospace' }}>{o.observable_value}</span>
                  {o.reputation && o.reputation !== 'unknown' && (
                    <span style={{ fontWeight: 700, fontSize: '0.7rem', color: scoreColor, border: `1px solid ${scoreColor}`, borderRadius: '999px', padding: '1px 6px' }}>
                      {o.reputation} {o.malicious_score ?? ''}
                    </span>
                  )}
                  <button
                    onClick={async () => {
                      await deleteAlertObservable(id, o.id)
                      load()
                    }}
                    style={{ background: 'none', border: 'none', color: '#dc2626', cursor: 'pointer', fontWeight: 700 }}
                    title="Remove"
                  >
                    ×
                  </button>
                </span>
              )
            })}
          </div>
        )}

        <form onSubmit={submitObservable} style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
          <select value={obsType} onChange={(e) => setObsType(e.target.value)} style={{ ...inputStyle, width: 'auto' }}>
            {OBSERVABLE_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <input
            value={obsValue}
            onChange={(e) => setObsValue(e.target.value)}
            placeholder="Add observable manually…"
            style={{ ...inputStyle, flex: 1 }}
          />
          <button type="submit" style={primaryBtnStyle}>Add</button>
        </form>
      </div>
    </div>
  )
}


function IncidentForm({
  incident,
  onCancel,
  onSaved,
}: {
  incident: Incident | null
  onCancel: () => void
  onSaved: (message?: string) => void
}) {
  const [form, setForm] = React.useState<IncidentInput>({
    title: incident?.title ?? '',
    description: incident?.description ?? '',
    severity: incident?.severity ?? 'medium',
    status: incident?.status ?? 'open',
    priority: incident?.priority ?? 'medium',
    source_type: incident?.source_type ?? 'manual',
    auto_enrich: false,
  })
  const [saving, setSaving] = React.useState(false)
  const [err, setErr] = React.useState<string | null>(null)

  const set = (key: keyof IncidentInput, value: string) =>
    setForm((prev) => ({ ...prev, [key]: value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setErr(null)
    try {
      if (incident) {
        await updateIncident(incident.id, form)
        onSaved()
      } else {
        const created = await createIncident(form)
        const n = created.auto_extracted ?? 0
        const e = created.auto_enriched ?? 0
        const msg =
          n > 0
            ? `Auto-extracted ${n} IOC(s)${e > 0 ? `, auto-enriched ${e}` : ''}`
            : undefined
        onSaved(msg)
      }
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <FormCard title={incident ? `Edit Incident ${incident.number}` : 'Create New Incident'}>
      <form onSubmit={handleSubmit}>
        <Field label="Title *">
          <input required value={form.title} onChange={(e) => set('title', e.target.value)} style={inputStyle} placeholder="e.g. Suspicious PowerShell Execution" />
        </Field>
        <Field label="Description">
          <textarea value={form.description ?? ''} onChange={(e) => set('description', e.target.value)} style={{ ...inputStyle, minHeight: '80px' }} placeholder="What was detected…" />
        </Field>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <Field label="Severity">
            <select value={form.severity} onChange={(e) => set('severity', e.target.value)} style={inputStyle}>
              {SEVERITY_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </Field>
          <Field label="Status">
            <select value={form.status} onChange={(e) => set('status', e.target.value)} style={inputStyle}>
              {INCIDENT_STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </Field>
          <Field label="Priority">
            <select value={form.priority} onChange={(e) => set('priority', e.target.value)} style={inputStyle}>
              {['low', 'medium', 'high'].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </Field>
          <Field label="Source Type">
            <select value={form.source_type} onChange={(e) => set('source_type', e.target.value)} style={inputStyle}>
              {SOURCE_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </Field>
        </div>

        {!incident && (
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', fontSize: '0.9rem', color: '#374151' }}>
            <input
              type="checkbox"
              checked={form.auto_enrich ?? false}
              onChange={(e) => setForm((prev) => ({ ...prev, auto_enrich: e.target.checked }))}
            />
            Auto-enrich extracted indicators (threat intel lookup)
          </label>
        )}

        {err && <div style={{ color: '#dc2626', marginTop: '0.75rem' }}>{err}</div>}

        <FormActions onCancel={onCancel} saving={saving} saveLabel={incident ? 'Save Changes' : 'Create Incident'} />
      </form>
    </FormCard>
  )
}

function AlertForm({
  alert,
  onCancel,
  onSaved,
}: {
  alert: Alert | null
  onCancel: () => void
  onSaved: (message?: string) => void
}) {
  const [form, setForm] = React.useState<AlertInput>({
    title: alert?.title ?? '',
    description: alert?.description ?? '',
    severity: alert?.severity ?? 'medium',
    status: alert?.status ?? 'new',
    source_type: alert?.source_type ?? 'manual',
    source_id: alert?.source_id ?? '',
    detection_id: alert?.detection_id ?? '',
    auto_enrich: false,
  })
  const [saving, setSaving] = React.useState(false)
  const [err, setErr] = React.useState<string | null>(null)

  const set = (key: keyof AlertInput, value: string) =>
    setForm((prev) => ({ ...prev, [key]: value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setErr(null)
    try {
      if (alert) {
        await updateAlert(alert.id, form)
        onSaved()
      } else {
        const created = await createAlert(form)
        const n = created.auto_extracted ?? 0
        const e = created.auto_enriched ?? 0
        onSaved(
          n > 0
            ? `Auto-extracted ${n} IOC(s)${e > 0 ? `, auto-enriched ${e}` : ''}`
            : undefined
        )
      }
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <FormCard title={alert ? `Edit Alert ${alert.number}` : 'Create New Alert'}>
      <form onSubmit={handleSubmit}>
        <Field label="Title *">
          <input required value={form.title} onChange={(e) => set('title', e.target.value)} style={inputStyle} placeholder="e.g. Brute Force Login Detected" />
        </Field>
        <Field label="Description">
          <textarea value={form.description ?? ''} onChange={(e) => set('description', e.target.value)} style={{ ...inputStyle, minHeight: '80px' }} placeholder="Detection details…" />
        </Field>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <Field label="Severity">
            <select value={form.severity} onChange={(e) => set('severity', e.target.value)} style={inputStyle}>
              {SEVERITY_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </Field>
          <Field label="Status">
            <select value={form.status} onChange={(e) => set('status', e.target.value)} style={inputStyle}>
              {ALERT_STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </Field>
          <Field label="Source Type">
            <select value={form.source_type} onChange={(e) => set('source_type', e.target.value)} style={inputStyle}>
              {SOURCE_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </Field>
          <Field label="Source ID">
            <input value={form.source_id ?? ''} onChange={(e) => set('source_id', e.target.value)} style={inputStyle} placeholder="e.g. 203.0.113.5" />
          </Field>
        </div>

        {!alert && (
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', fontSize: '0.9rem', color: '#374151' }}>
            <input
              type="checkbox"
              checked={form.auto_enrich ?? false}
              onChange={(e) => setForm((prev) => ({ ...prev, auto_enrich: e.target.checked }))}
            />
            Auto-enrich extracted indicators (threat intel lookup)
          </label>
        )}

        {err && <div style={{ color: '#dc2626', marginTop: '0.75rem' }}>{err}</div>}

        <FormActions onCancel={onCancel} saving={saving} saveLabel={alert ? 'Save Changes' : 'Create Alert'} />
      </form>
    </FormCard>
  )
}

// ===================== Small helpers =====================

function TableWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ background: '#fff', borderRadius: '8px', boxShadow: '0 1px 2px rgba(0,0,0,0.06)', overflow: 'hidden' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>{children}</table>
    </div>
  )
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th style={{ padding: '0.75rem', fontSize: '0.75rem', textTransform: 'uppercase', color: '#6b7280', fontWeight: 600 }}>
      {children}
    </th>
  )
}

function Td({ children }: { children: React.ReactNode }) {
  return <td style={{ padding: '0.75rem', verticalAlign: 'top' }}>{children}</td>
}

function Badge({ text, color }: { text: string; color: string }) {
  return (
    <span style={{ display: 'inline-block', padding: '2px 8px', borderRadius: '999px', fontSize: '0.75rem', fontWeight: 600, color, background: color + '20' }}>
      {text}
    </span>
  )
}

function FormCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ background: '#fff', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.06)', maxWidth: '640px' }}>
      <h2 style={{ marginTop: 0 }}>{title}</h2>
      {children}
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: '1rem' }}>
      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>{label}</label>
      {children}
    </div>
  )
}

function FormActions({ onCancel, saving, saveLabel }: { onCancel: () => void; saving: boolean; saveLabel: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
      <button type="button" onClick={onCancel} style={secondaryBtnStyle}>
        Cancel
      </button>
      <button type="submit" disabled={saving} style={primaryBtnStyle}>
        {saving ? 'Saving…' : saveLabel}
      </button>
    </div>
  )
}

const filterSelectStyle: React.CSSProperties = {
  padding: '0.5rem',
  border: '1px solid #d1d5db',
  borderRadius: '6px',
  background: '#fff',
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.5rem',
  border: '1px solid #d1d5db',
  borderRadius: '6px',
  fontSize: '0.9rem',
  boxSizing: 'border-box',
}

const primaryBtnStyle: React.CSSProperties = {
  background: '#2563eb',
  color: '#fff',
  border: 'none',
  padding: '0.5rem 1rem',
  borderRadius: '6px',
  fontWeight: 600,
  cursor: 'pointer',
}

const secondaryBtnStyle: React.CSSProperties = {
  background: '#fff',
  color: '#374151',
  border: '1px solid #d1d5db',
  padding: '0.5rem 1rem',
  borderRadius: '6px',
  cursor: 'pointer',
}

const actionBtnStyle: React.CSSProperties = {
  background: 'transparent',
  border: 'none',
  color: '#2563eb',
  cursor: 'pointer',
  fontSize: '0.85rem',
  padding: '0.25rem 0.5rem',
  fontWeight: 600,
}

const promoteBtnStyle: React.CSSProperties = {
  background: '#059669',
  color: '#fff',
  border: 'none',
  cursor: 'pointer',
  fontSize: '0.8rem',
  padding: '0.3rem 0.6rem',
  borderRadius: '4px',
  fontWeight: 600,
}

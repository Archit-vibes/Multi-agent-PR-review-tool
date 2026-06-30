import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  GitMerge,
  GitPullRequest,
  Activity,
  Zap,
  Clock,
  Hash,
  BookOpen,
  AlertCircle,
  CheckCircle2,
  XCircle,
  GitBranch,
  Cpu,
  ChevronRight,
  Sparkles,
  ShieldAlert,
  Bug,
  Code
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import toast, { Toaster } from 'react-hot-toast'
import { formatDistanceToNow } from 'date-fns'

const API_BASE_URL = 'http://localhost:8000'

/* ─── Skeleton Loader ─────────────────────────────────────────── */
function SkeletonLoader() {
  return (
    <div className="skeleton-wrap">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.08 }}
          className="skel-card"
        >
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div className="skel" style={{ width: 45 }} />
            <div className="skel" style={{ width: 52, borderRadius: 999 }} />
          </div>
          <div className="skel" style={{ width: '88%' }} />
          <div className="skel" style={{ width: '60%' }} />
        </motion.div>
      ))}
    </div>
  )
}

/* ─── Status Badge ────────────────────────────────────────────── */
function StatusBadge({ state }) {
  const s = state?.toLowerCase() || 'open'
  const icons = {
    open:   <CheckCircle2 size={10} />,
    closed: <XCircle size={10} />,
    merged: <GitMerge size={10} />,
  }
  return (
    <span className={`status-badge ${s}`}>
      <span className="status-dot" />
      {icons[s]}
      {s}
    </span>
  )
}

/* ─── Relative Time ───────────────────────────────────────────── */
function RelativeTime({ isoString }) {
  if (!isoString) return null
  try {
    return (
      <span className="pr-card-time" title={new Date(isoString).toLocaleString()}>
        <Clock size={10} />
        {formatDistanceToNow(new Date(isoString), { addSuffix: true })}
      </span>
    )
  } catch { return null }
}

/* ─── PR Card ─────────────────────────────────────────────────── */
function PrCard({ pr, isSelected, isNewest, onClick }) {
  return (
    <motion.div
      layout
      className={`pr-card ${isSelected ? 'active' : ''}`}
      onClick={onClick}
      transition={{ type: 'spring', stiffness: 500, damping: 40 }}
    >
      <div className="pr-card-top">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span className="pr-number">
            #{pr.number}
          </span>
          {isNewest && <span className="pr-newest-badge">New</span>}
        </div>
        <StatusBadge state={pr.state} />
      </div>

      <p className="pr-card-title">{pr.title || 'Untitled Pull Request'}</p>

      <div className="pr-card-meta">
        <span className="pr-card-repo">
          <GitBranch size={10} />
          {pr.repo_id || 'unknown repo'}
        </span>
        <RelativeTime isoString={pr.created_at} />
      </div>
    </motion.div>
  )
}

/* ─── Code Block ──────────────────────────────────────────────── */
function CodeBlock({ children, className }) {
  const match = /language-(\w+)/.exec(className || '')
  const lang = match ? match[1] : ''
  const code = String(children).replace(/\n$/, '')

  if (!match) return <code className={className}>{children}</code>

  return (
    <div className="code-block-wrapper">
      {lang && <span className="code-block-lang">{lang}</span>}
      <SyntaxHighlighter
        style={oneLight}
        language={lang}
        PreTag="div"
        customStyle={{
          margin: 0,
          background: 'transparent',
          border: 'none',
          padding: '1.2rem 1rem',
        }}
        codeTagProps={{ style: { fontFamily: "'JetBrains Mono', 'Fira Code', monospace" } }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  )
}

/* ─── Processing State ────────────────────────────────────────── */
function ProcessingState() {
  return (
    <motion.div
      className="processing-state"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div style={{
        width: 48, height: 48,
        borderRadius: 12,
        background: 'var(--canvas-soft)',
        border: '1px solid var(--hairline)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: 'var(--shadow-1)'
      }}>
        <Cpu size={20} color="var(--primary)" />
      </div>
      <div className="processing-dots">
        {[0, 1, 2].map((i) => (
          <div key={i} className="processing-dot" />
        ))}
      </div>
      <div>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: 'var(--ink)', marginBottom: 4 }}>
          Agent is analyzing…
        </h3>
        <p style={{ color: 'var(--ink-muted)', fontSize: 14 }}>
          The multi-agent pipeline is reviewing this PR.
        </p>
      </div>
    </motion.div>
  )
}

/* ─── Empty State ─────────────────────────────────────────────── */
function EmptyState() {
  return (
    <motion.div
      className="empty-state"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
    >
      <div className="empty-state-icon">
        <GitPullRequest size={32} color="var(--primary)" />
        <div className="empty-state-dot d1" />
        <div className="empty-state-dot d2" />
        <div className="empty-state-dot d3" />
      </div>

      <div>
        <h2 className="empty-state-heading">Select a Pull Request</h2>
        <p className="empty-state-body">
          Pick a PR from the sidebar to view the AI-generated multi-agent review and code analysis.
        </p>
      </div>

      <div className="feature-chips">
        {['Code Review', 'Security Scan', 'Bug Detection', 'Best Practices'].map((chip) => (
          <span key={chip} className="feature-chip">
            {chip}
          </span>
        ))}
      </div>
    </motion.div>
  )
}

/* ─── PR Detail View ──────────────────────────────────────────── */
function PrDetail({ pr }) {
  const [activeTab, setActiveTab] = useState('final')
  
  const renderAgentFindings = (findings, icon, emptyMsg) => {
    if (!findings || findings.length === 0) {
      return <p style={{ color: 'var(--ink-muted)' }}>{emptyMsg}</p>
    }
    return (
      <div className="agent-finding-list">
        {findings.map((f, i) => {
          // Fallback if finding is just a string (old data)
          if (typeof f === 'string') {
            return (
              <div key={i} className="agent-finding-item">
                <div className="agent-finding-icon">{icon}</div>
                <div>{f}</div>
              </div>
            )
          }
          // New structured data
          return (
            <div key={i} className="agent-finding-item">
              <div className="agent-finding-icon">{icon}</div>
              <div style={{ flex: 1 }}>
                <strong style={{ display: 'block', marginBottom: '4px' }}>{f.issue}</strong>
                {f.file && f.line && (
                  <div style={{ fontSize: '13px', color: 'var(--ink-muted)', marginBottom: '8px' }}>
                    {f.file}:{f.line}
                  </div>
                )}
                <div style={{ marginBottom: '8px' }}>{f.reason}</div>
                {f.replacement && (
                  <div style={{ 
                    background: '#f6f8fa', 
                    border: '1px solid var(--hairline)', 
                    borderRadius: '6px', 
                    padding: '8px',
                    fontFamily: 'monospace',
                    fontSize: '13px',
                    whiteSpace: 'pre-wrap'
                  }}>
                    <strong style={{ display: 'block', marginBottom: '4px', color: 'var(--ink-muted)' }}>Suggested Fix:</strong>
                    {f.replacement}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <motion.div
      key={pr.id}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
    >
      {/* Header */}
      <div className="pr-detail-header">
        <div className="pr-detail-eyebrow">
          <GitPullRequest size={14} /> Pull Request Review
        </div>
        <h2 className="pr-detail-title">{pr.title || 'Untitled Pull Request'}</h2>
        
        <div className="pr-detail-meta-row">
          <span className="pr-meta-chip">
            <Hash size={14} /> <strong>#{pr.number}</strong>
          </span>
          <StatusBadge state={pr.state} />
          <span className="pr-meta-chip">
            <GitBranch size={14} /> <strong>{pr.repo_id || '—'}</strong>
          </span>
          {pr.created_at && (
            <span className="pr-meta-chip">
              <Clock size={14} /> <RelativeTime isoString={pr.created_at} />
            </span>
          )}
        </div>
      </div>

      {/* AI Review Banner */}
      <div className="ai-review-banner">
        <div className="ai-review-icon">
          <Zap size={18} color="var(--primary)" />
        </div>
        <div>
          <div className="ai-review-label">Multi-Agent Analysis</div>
          <div className="ai-review-desc">
            AI agents have analyzed the code for quality, security, and best practices.
          </div>
        </div>
      </div>

      {/* Tabs */}
      {pr.final_review ? (
        <>
          <div className="tabs-nav">
            <button 
              className={`tab-button ${activeTab === 'final' ? 'active' : ''}`}
              onClick={() => setActiveTab('final')}
            >
              Aggregated Review
            </button>
            {pr.agent_reviews && pr.agent_reviews.security && (
              <button 
                className={`tab-button ${activeTab === 'security' ? 'active' : ''}`}
                onClick={() => setActiveTab('security')}
              >
                Security Findings
              </button>
            )}
            {pr.agent_reviews && pr.agent_reviews.bug && (
              <button 
                className={`tab-button ${activeTab === 'bug' ? 'active' : ''}`}
                onClick={() => setActiveTab('bug')}
              >
                Bug Findings
              </button>
            )}
            {pr.agent_reviews && pr.agent_reviews.quality && (
              <button 
                className={`tab-button ${activeTab === 'quality' ? 'active' : ''}`}
                onClick={() => setActiveTab('quality')}
              >
                Quality Findings
              </button>
            )}
          </div>

          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {activeTab === 'final' && (
              <div className="markdown-body">
                <ReactMarkdown components={{ code: CodeBlock }}>
                  {pr.final_review}
                </ReactMarkdown>
              </div>
            )}
            {activeTab === 'security' && renderAgentFindings(pr.agent_reviews.security, <ShieldAlert size={16} color="var(--accent-orange)" />, "No security issues detected.")}
            {activeTab === 'bug' && renderAgentFindings(pr.agent_reviews.bug, <Bug size={16} color="var(--accent-pink)" />, "No bugs detected.")}
            {activeTab === 'quality' && renderAgentFindings(pr.agent_reviews.quality, <Code size={16} color="var(--accent-teal)" />, "No quality issues detected.")}
          </motion.div>
        </>
      ) : (
        <ProcessingState />
      )}
    </motion.div>
  )
}

/* ─── App Root ────────────────────────────────────────────────── */
function App() {
  const [prs, setPrs] = useState([])
  const [selectedPr, setSelectedPr] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchPrs = useCallback(async (isBackground = false) => {
    try {
      if (!isBackground) setLoading(true)
      const res = await fetch(`${API_BASE_URL}/api/prs`)
      if (!res.ok) throw new Error('Failed to fetch Pull Requests')
      const data = await res.json()

      setPrs((prev) => {
        if (data.length > 0 && (!prev.length || data[0].id !== prev[0].id)) {
          if (prev.length > 0) {
            toast(`New PR #${data[0].number} arrived!`, {
              style: {
                background: 'var(--surface)',
                border: '1px solid var(--hairline)',
                color: 'var(--ink)',
                fontSize: '14px',
                boxShadow: 'var(--shadow-1)',
              },
            })
          }
          setSelectedPr(data[0])
        } else {
          setSelectedPr((prevSel) => {
            if (!prevSel) return data.length > 0 ? data[0] : null
            const updated = data.find((p) => p.id === prevSel.id)
            return updated || prevSel
          })
        }
        return data
      })
    } catch (err) {
      if (!isBackground) setError(err.message)
    } finally {
      if (!isBackground) setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchPrs()
    const id = setInterval(() => fetchPrs(true), 5000)
    return () => clearInterval(id)
  }, [fetchPrs])

  const openCount = prs.filter((p) => p.state?.toLowerCase() === 'open').length

  return (
    <div className="app-root">
      <Toaster position="top-right" />

      {/* ── Header ── */}
      <header className="header">
        <div className="header-left">
          <div className="header-logo-wrap">
            <GitMerge size={18} color="white" />
          </div>
          <div>
            <h1 className="header-title">Agentic AI PR Reviewer</h1>
            <div className="header-tagline">Multi-agent · Real-time · AI-powered</div>
          </div>
        </div>

        <div className="header-right">
          {openCount > 0 && (
            <span className="badge-pill-dark">
              <Activity size={12} /> {openCount} open
            </span>
          )}
          <span className="btn-utility-dark">
            <div className="live-dot" /> Live
          </span>
        </div>
      </header>

      <div className="body-area">
        {/* ── Sidebar ── */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <div className="sidebar-label">Pull Requests</div>
          </div>
          <div className="sidebar-list">
            {loading ? (
              <SkeletonLoader />
            ) : error ? (
              <div className="error-msg">
                <AlertCircle size={16} />
                {error}
              </div>
            ) : prs.length === 0 ? (
              <div className="no-prs-msg">
                <GitPullRequest size={24} color="var(--hairline)" style={{ margin: '0 auto 8px' }} />
                <p>No pull requests yet.</p>
              </div>
            ) : (
              <AnimatePresence mode="popLayout">
                {prs.map((pr, index) => (
                  <motion.div
                    key={pr.id}
                    layout
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <PrCard
                      pr={pr}
                      isSelected={selectedPr?.id === pr.id}
                      isNewest={index === 0}
                      onClick={() => setSelectedPr(pr)}
                    />
                  </motion.div>
                ))}
              </AnimatePresence>
            )}
          </div>
        </aside>

        {/* ── Main Content ── */}
        <main className="main-content">
          <AnimatePresence mode="wait">
            {!selectedPr
              ? <EmptyState key="empty" />
              : <PrDetail key={selectedPr.id} pr={selectedPr} />
            }
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}

export default App

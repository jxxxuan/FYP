'use client'
 
import { useState, useEffect, useRef, useCallback } from 'react'
 
const API = 'http://localhost:8000'
 
const MAPS = {
  Town03: { label: 'Town 03', desc: '环形交叉路口 · 隧道 · 高速入口', color: '#00d4ff' },
  Town04: { label: 'Town 04', desc: '高速公路 · 郊区道路', color: '#00ff9d' },
  Town05: { label: 'Town 05', desc: '方格网络 · 多车道城市', color: '#ff6b35' },
}
 
export default function Home() {
  const [phase, setPhase] = useState('config') // config | running
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)
  const [logs, setLogs] = useState([])
  const logsEndRef = useRef(null)
  const eventSourceRef = useRef(null)
 
  const [config, setConfig] = useState({
    map: 'Town03',
    spawn_point_index: 0,
    num_vehicles: 20,
    prediction_horizon: 50,
    confidence_threshold: 0.5,
    max_speed: 30,
    seed: 42,
  })
 
  const [spawnPoints, setSpawnPoints] = useState([])
  const [loadingSpawns, setLoadingSpawns] = useState(false)
 
  // 加载 spawn points
  useEffect(() => {
    setLoadingSpawns(true)
    fetch(`${API}/api/maps/${config.map}/spawn-points`)
      .then(r => r.json())
      .then(d => { setSpawnPoints(d.spawn_points); setLoadingSpawns(false) })
      .catch(() => setLoadingSpawns(false))
  }, [config.map])
 
  // 自动滚动日志
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])
 
  const startSession = async () => {
    setError(null)
    setLogs([])
    try {
      const res = await fetch(`${API}/api/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })
      if (!res.ok) {
        const d = await res.json()
        throw new Error(d.detail)
      }
      setPhase('running')
      setStatus('starting')
      startSSE()
    } catch (e) {
      setError(e.message)
    }
  }
 
  const stopSession = async () => {
    eventSourceRef.current?.close()
    await fetch(`${API}/api/session/stop`, { method: 'POST' }).catch(() => {})
    setStatus('idle')
    setPhase('config')
  }
 
  const startSSE = useCallback(() => {
    eventSourceRef.current?.close()
    const es = new EventSource(`${API}/api/session/logs/stream`)
    es.onmessage = (e) => {
      const data = JSON.parse(e.data)
      if (data.log) setLogs(prev => [...prev, data.log])
      if (data.status) setStatus(data.status)
      if (data.done) es.close()
    }
    es.onerror = () => { setStatus('error'); es.close() }
    eventSourceRef.current = es
  }, [])
 
  const set = (k, v) => setConfig(prev => ({ ...prev, [k]: v }))
 
  return (
    <main className="app">
      <header className="header">
        <div className="header-left">
          <div className="logo">
            <span className="logo-icon">◈</span>
            <span className="logo-text">AUTOPILOT<span className="logo-accent">DEMO</span></span>
          </div>
        </div>
        <div className="header-status">
          <span className={`status-dot ${status}`} />
          <span className="status-label">
            {{ idle: '待机', starting: '启动中', running: '推理中', stopping: '停止中', error: '错误' }[status] || status}
          </span>
        </div>
      </header>
 
      <div className="layout">
        {/* ── 左侧配置面板 ── */}
        <aside className="sidebar">
          <div className="sidebar-inner">
 
            {/* 地图选择 */}
            <section className="section">
              <h2 className="section-title"><span className="section-num">01</span>选择场景地图</h2>
              <div className="map-grid">
                {Object.entries(MAPS).map(([id, m]) => (
                  <button
                    key={id}
                    className={`map-card ${config.map === id ? 'active' : ''}`}
                    onClick={() => set('map', id)}
                    disabled={phase === 'running'}
                    style={{ '--accent': m.color }}
                  >
                    <div className="map-card-tag">{id}</div>
                    <div className="map-card-name">{m.label}</div>
                    <div className="map-card-desc">{m.desc}</div>
                    {config.map === id && <div className="map-card-check">✓</div>}
                  </button>
                ))}
              </div>
            </section>
 
            {/* Spawn Point */}
            <section className="section">
              <h2 className="section-title"><span className="section-num">02</span>起始位置</h2>
              <div className="spawn-row">
                <label className="field-label">Spawn Point 索引</label>
                <div className="spawn-input-row">
                  <input
                    type="range"
                    min={0}
                    max={Math.max(0, spawnPoints.length - 1)}
                    value={config.spawn_point_index}
                    onChange={e => set('spawn_point_index', +e.target.value)}
                    disabled={phase === 'running'}
                    className="slider"
                  />
                  <span className="spawn-index">#{config.spawn_point_index}</span>
                </div>
                {spawnPoints[config.spawn_point_index] && (
                  <div className="spawn-coords">
                    x: {spawnPoints[config.spawn_point_index].x} &nbsp;
                    y: {spawnPoints[config.spawn_point_index].y} &nbsp;
                    yaw: {spawnPoints[config.spawn_point_index].yaw}°
                  </div>
                )}
                {loadingSpawns && <div className="loading-text">加载中...</div>}
              </div>
            </section>
 
            {/* 场景参数 */}
            <section className="section">
              <h2 className="section-title"><span className="section-num">03</span>场景参数</h2>
              <div className="fields">
                <div className="field">
                  <label className="field-label">其他车辆数量 <span className="field-val">{config.num_vehicles}</span></label>
                  <input type="range" min={0} max={100} value={config.num_vehicles}
                    onChange={e => set('num_vehicles', +e.target.value)}
                    disabled={phase === 'running'} className="slider" />
                </div>
              </div>
            </section>
 
            {/* 模型参数 */}
            <section className="section">
              <h2 className="section-title"><span className="section-num">04</span>模型参数</h2>
              <div className="fields">
                <div className="field">
                  <label className="field-label">预测步长 <span className="field-val">{config.prediction_horizon}</span></label>
                  <input type="range" min={10} max={200} step={10} value={config.prediction_horizon}
                    onChange={e => set('prediction_horizon', +e.target.value)}
                    disabled={phase === 'running'} className="slider" />
                </div>
                <div className="field">
                  <label className="field-label">置信度阈值 <span className="field-val">{config.confidence_threshold.toFixed(2)}</span></label>
                  <input type="range" min={0} max={1} step={0.05} value={config.confidence_threshold}
                    onChange={e => set('confidence_threshold', +e.target.value)}
                    disabled={phase === 'running'} className="slider" />
                </div>
                <div className="field">
                  <label className="field-label">最大速度 <span className="field-val">{config.max_speed} km/h</span></label>
                  <input type="range" min={10} max={120} step={5} value={config.max_speed}
                    onChange={e => set('max_speed', +e.target.value)}
                    disabled={phase === 'running'} className="slider" />
                </div>
                <div className="field">
                  <label className="field-label">随机种子 <span className="field-val">{config.seed}</span></label>
                  <input type="number" value={config.seed}
                    onChange={e => set('seed', +e.target.value)}
                    disabled={phase === 'running'} className="input-num" />
                </div>
              </div>
            </section>
 
            {/* 操作按钮 */}
            <div className="actions">
              {phase === 'config' ? (
                <button className="btn-start" onClick={startSession}>
                  <span className="btn-icon">▶</span> 开始仿真
                </button>
              ) : (
                <button className="btn-stop" onClick={stopSession}>
                  <span className="btn-icon">■</span> 停止仿真
                </button>
              )}
              {error && <div className="error-msg">⚠ {error}</div>}
            </div>
 
          </div>
        </aside>
 
        {/* ── 右侧主区域 ── */}
        <div className="main-area">
          {/* CarlaViz iframe */}
          <div className="viz-container">
            <div className="viz-header">
              <span className="viz-title">CarlaViz 实时视图</span>
              <a href="http://localhost:8080" target="_blank" rel="noreferrer" className="viz-link">↗ 独立窗口</a>
            </div>
            <div className="viz-frame-wrap">
              {phase === 'running' ? (
                <iframe
                  src="http://localhost:8080"
                  className="viz-frame"
                  title="CarlaViz"
                  allow="autoplay"
                />
              ) : (
                <div className="viz-placeholder">
                  <div className="placeholder-icon">◈</div>
                  <div className="placeholder-text">配置参数后点击「开始仿真」</div>
                  <div className="placeholder-sub">CarlaViz 将在此处嵌入显示</div>
                </div>
              )}
            </div>
          </div>
 
          {/* 日志面板 */}
          <div className="log-panel">
            <div className="log-header">
              <span className="log-title">运行日志</span>
              <span className="log-count">{logs.length} 条</span>
            </div>
            <div className="log-body">
              {logs.length === 0 && (
                <div className="log-empty">等待启动...</div>
              )}
              {logs.map((l, i) => (
                <div key={i} className={`log-line ${
                  l.includes('✓') ? 'ok' :
                  l.includes('✗') || l.includes('错误') ? 'err' :
                  l.includes('[Runner]') ? 'runner' : ''
                }`}>{l}</div>
              ))}
              <div ref={logsEndRef} />
            </div>
          </div>
        </div>
      </div>
 
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
 
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
 
        :root {
          --bg: #080c10;
          --bg2: #0d1117;
          --bg3: #131920;
          --border: #1e2730;
          --border2: #2a3540;
          --text: #c8d8e8;
          --text2: #6a8090;
          --text3: #3a5060;
          --accent: #00d4ff;
          --accent2: #00ff9d;
          --red: #ff4560;
          --yellow: #ffd460;
          --radius: 8px;
          --font-mono: 'Space Mono', monospace;
          --font-sans: 'DM Sans', sans-serif;
        }
 
        html, body { background: var(--bg); color: var(--text); font-family: var(--font-sans); height: 100%; }
 
        .app { display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
 
        /* Header */
        .header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 0 24px; height: 52px;
          background: var(--bg2); border-bottom: 1px solid var(--border);
          flex-shrink: 0;
        }
        .header-left { display: flex; align-items: center; gap: 32px; }
        .logo { display: flex; align-items: center; gap: 10px; }
        .logo-icon { color: var(--accent); font-size: 18px; }
        .logo-text { font-family: var(--font-mono); font-size: 13px; font-weight: 700; letter-spacing: 3px; color: var(--text); }
        .logo-accent { color: var(--accent); }
        .header-status { display: flex; align-items: center; gap: 8px; }
        .status-dot {
          width: 8px; height: 8px; border-radius: 50%;
          background: var(--text3); transition: background 0.3s;
        }
        .status-dot.running { background: var(--accent2); box-shadow: 0 0 8px var(--accent2); animation: pulse 1.5s infinite; }
        .status-dot.starting { background: var(--yellow); animation: pulse 1s infinite; }
        .status-dot.error { background: var(--red); }
        .status-label { font-family: var(--font-mono); font-size: 11px; color: var(--text2); letter-spacing: 1px; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
 
        /* Layout */
        .layout { display: flex; flex: 1; overflow: hidden; }
 
        /* Sidebar */
        .sidebar {
          width: 340px; flex-shrink: 0;
          background: var(--bg2); border-right: 1px solid var(--border);
          overflow-y: auto; overflow-x: hidden;
        }
        .sidebar::-webkit-scrollbar { width: 4px; }
        .sidebar::-webkit-scrollbar-track { background: transparent; }
        .sidebar::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }
        .sidebar-inner { padding: 20px 16px 32px; display: flex; flex-direction: column; gap: 4px; }
 
        /* Sections */
        .section { margin-bottom: 20px; }
        .section-title {
          font-family: var(--font-mono); font-size: 10px; font-weight: 700;
          letter-spacing: 2px; color: var(--text3); text-transform: uppercase;
          margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
        }
        .section-num { color: var(--accent); }
 
        /* Map Cards */
        .map-grid { display: flex; flex-direction: column; gap: 8px; }
        .map-card {
          position: relative; padding: 12px 14px;
          background: var(--bg3); border: 1px solid var(--border);
          border-radius: var(--radius); cursor: pointer;
          text-align: left; transition: all 0.15s;
          color: var(--text);
        }
        .map-card:hover:not(:disabled) { border-color: var(--border2); background: #161e26; }
        .map-card.active { border-color: var(--accent); background: rgba(0,212,255,0.05); }
        .map-card:disabled { opacity: 0.5; cursor: not-allowed; }
        .map-card-tag { font-family: var(--font-mono); font-size: 10px; color: var(--accent); margin-bottom: 3px; }
        .map-card.active .map-card-tag { color: var(--accent); }
        .map-card-name { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 3px; }
        .map-card-desc { font-size: 11px; color: var(--text2); line-height: 1.4; }
        .map-card-check {
          position: absolute; top: 10px; right: 12px;
          width: 18px; height: 18px; border-radius: 50%;
          background: var(--accent); color: #000;
          font-size: 10px; font-weight: 700;
          display: flex; align-items: center; justify-content: center;
        }
 
        /* Spawn */
        .spawn-row { display: flex; flex-direction: column; gap: 8px; }
        .spawn-input-row { display: flex; align-items: center; gap: 10px; }
        .spawn-index { font-family: var(--font-mono); font-size: 13px; color: var(--accent); min-width: 36px; }
        .spawn-coords { font-family: var(--font-mono); font-size: 10px; color: var(--text3); }
        .loading-text { font-size: 11px; color: var(--text3); }
 
        /* Fields */
        .fields { display: flex; flex-direction: column; gap: 14px; }
        .field { display: flex; flex-direction: column; gap: 6px; }
        .field-label { font-size: 11px; color: var(--text2); display: flex; justify-content: space-between; }
        .field-val { font-family: var(--font-mono); color: var(--accent); }
 
        /* Slider */
        .slider {
          width: 100%; height: 3px; appearance: none;
          background: var(--border2); border-radius: 2px; outline: none; cursor: pointer;
        }
        .slider::-webkit-slider-thumb {
          appearance: none; width: 14px; height: 14px;
          border-radius: 50%; background: var(--accent); cursor: pointer;
          box-shadow: 0 0 6px rgba(0,212,255,0.5);
        }
        .slider:disabled { opacity: 0.4; cursor: not-allowed; }
 
        /* Number input */
        .input-num {
          background: var(--bg3); border: 1px solid var(--border);
          color: var(--text); padding: 6px 10px; border-radius: var(--radius);
          font-family: var(--font-mono); font-size: 12px; width: 100%; outline: none;
        }
        .input-num:focus { border-color: var(--accent); }
 
        /* Buttons */
        .actions { margin-top: 8px; display: flex; flex-direction: column; gap: 10px; }
        .btn-start, .btn-stop {
          width: 100%; padding: 13px; border-radius: var(--radius);
          border: none; cursor: pointer; font-family: var(--font-mono);
          font-size: 12px; font-weight: 700; letter-spacing: 2px;
          display: flex; align-items: center; justify-content: center; gap: 8px;
          transition: all 0.15s;
        }
        .btn-start { background: var(--accent); color: #000; }
        .btn-start:hover { background: #33ddff; box-shadow: 0 0 20px rgba(0,212,255,0.3); }
        .btn-stop { background: rgba(255,69,96,0.15); color: var(--red); border: 1px solid var(--red); }
        .btn-stop:hover { background: rgba(255,69,96,0.25); }
        .btn-icon { font-size: 10px; }
        .error-msg { font-size: 11px; color: var(--red); background: rgba(255,69,96,0.1); padding: 8px 12px; border-radius: var(--radius); border: 1px solid rgba(255,69,96,0.3); }
 
        /* Main area */
        .main-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
 
        /* Viz */
        .viz-container { flex: 1; display: flex; flex-direction: column; min-height: 0; }
        .viz-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 10px 16px; background: var(--bg2); border-bottom: 1px solid var(--border);
          flex-shrink: 0;
        }
        .viz-title { font-family: var(--font-mono); font-size: 11px; color: var(--text2); letter-spacing: 1px; }
        .viz-link { font-family: var(--font-mono); font-size: 10px; color: var(--accent); text-decoration: none; opacity: 0.7; }
        .viz-link:hover { opacity: 1; }
        .viz-frame-wrap { flex: 1; position: relative; background: #000; }
        .viz-frame { width: 100%; height: 100%; border: none; display: block; }
        .viz-placeholder {
          position: absolute; inset: 0;
          display: flex; flex-direction: column; align-items: center; justify-content: center;
          gap: 10px; background: var(--bg);
        }
        .placeholder-icon { font-size: 48px; color: var(--text3); opacity: 0.3; }
        .placeholder-text { font-size: 14px; color: var(--text2); }
        .placeholder-sub { font-size: 12px; color: var(--text3); }
 
        /* Log panel */
        .log-panel {
          height: 180px; flex-shrink: 0;
          background: var(--bg2); border-top: 1px solid var(--border);
          display: flex; flex-direction: column;
        }
        .log-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 8px 16px; border-bottom: 1px solid var(--border); flex-shrink: 0;
        }
        .log-title { font-family: var(--font-mono); font-size: 10px; color: var(--text3); letter-spacing: 1px; text-transform: uppercase; }
        .log-count { font-family: var(--font-mono); font-size: 10px; color: var(--text3); }
        .log-body { flex: 1; overflow-y: auto; padding: 8px 16px; display: flex; flex-direction: column; gap: 2px; }
        .log-body::-webkit-scrollbar { width: 3px; }
        .log-body::-webkit-scrollbar-thumb { background: var(--border2); }
        .log-line { font-family: var(--font-mono); font-size: 11px; color: var(--text2); line-height: 1.6; }
        .log-line.ok { color: var(--accent2); }
        .log-line.err { color: var(--red); }
        .log-line.runner { color: var(--text); }
        .log-empty { font-family: var(--font-mono); font-size: 11px; color: var(--text3); padding: 8px 0; }
      `}</style>
    </main>
  )
}
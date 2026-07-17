"use client";

import Image from "next/image";
import { useCallback, useEffect, useRef, useState } from "react";
import { analyzeLocally } from "./lib/api";

const SOURCE_CONFIG = {
  text: ["TEXT", "Analyze your text", "Enter your text"],
  document: ["DOCUMENT", "Analyze a document", "Choose a document"],
  voice: ["VOICE", "Analyze your voice", "Record or edit a transcript"],
  social: ["SOCIAL POST", "Analyze a social post", "Add the post text"],
};
const SAMPLES = {
  Positive: "I absolutely love how this turned out. The whole experience was wonderful!",
  Neutral: "The delivery arrived on Tuesday. Everything was included in the box.",
  Negative: "I am really disappointed. Nothing worked and support never answered.",
};
const title = (value) => value.charAt(0).toUpperCase() + value.slice(1);

function SourceIcon({ type }) {
  const paths = {
    text: <><path d="M5 7h14M8 7v10m8-10v10M6 17h4m4 0h4" /></>,
    document: <><path d="M7 3h7l4 4v14H7z" /><path d="M14 3v5h5M10 12h6m-6 4h6" /></>,
    voice: <><rect x="9" y="3" width="6" height="12" rx="3" /><path d="M6 11a6 6 0 0 0 12 0m-6 6v4m-3 0h6" /></>,
    social: <><circle cx="6" cy="12" r="2.5" /><circle cx="18" cy="6" r="2.5" /><circle cx="18" cy="18" r="2.5" /><path d="m8.3 10.8 7.4-3.6m-7.4 6 7.4 3.6" /></>,
  };
  return <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{paths[type]}</svg>;
}

function getPolarityPresentation(result) {
  const ordered = Object.entries(result.scores).sort((a, b) => b[1] - a[1]);
  const gap = ordered[0][1] - ordered[1][1];
  const mixed = result.confidence < 60 || gap < 15;
  if (mixed) {
    return {
      label: `Mixed, leaning ${result.label}`,
      glyph: "≈",
      description: `The text contains competing cues, with a slight ${result.label} lean.`,
      mixed: true,
    };
  }
  return {
    positive: { label: "Positive", glyph: "☺", description: "The language reads as optimistic and favorable." },
    neutral: { label: "Neutral", glyph: "–", description: "The language reads as mostly factual or balanced." },
    negative: { label: "Negative", glyph: "☹", description: "The language carries critical or unfavorable cues." },
  }[result.label];
}

function Brand({ compact = false }) {
  return <span className={`brand ${compact ? "brand-compact" : "brand-large"}`}><span className="brand-mark" aria-hidden="true">✦</span><span>TONE<span>LEAF</span></span></span>;
}

function Welcome({ onStart }) {
  return <section className="welcome" aria-labelledby="welcomeTitle">
    <div className="welcome-copy"><Brand /><p className="eyebrow">Privacy-conscious emotion intelligence</p><h1 id="welcomeTitle">Read between<br /><em>the lines.</em></h1><p className="welcome-lede">Toneleaf turns everyday language into gentle, useful emotional signals without third-party AI inference or persistent text storage.</p><div className="welcome-actions"><button className="primary-button" onClick={onStart}>Explore your tone <span>→</span></button><span className="privacy-note"><span className="privacy-dot" /> No text history stored</span></div></div>
    <div className="welcome-art"><Image src="/assets/hero-toneleaf.png" width={1536} height={1024} alt="A calm person exploring abstract emotional signals" priority unoptimized /><div className="hero-chip hero-chip-top"><span>✦</span><div><strong>Gentle clarity</strong><small>Context before labels</small></div></div><div className="hero-chip hero-chip-bottom"><span>○</span><div><strong>Local analysis</strong><small>Your words stay with you</small></div></div></div>
  </section>;
}

function ResultPanel({ result, onCopy }) {
  if (!result) return <section className="results-panel panel"><div className="panel-heading"><div><span className="step">02</span><h3>Your result</h3></div></div><div className="empty-state"><div className="empty-glyph"><span /><span /><span /></div><h3>Ready when you are</h3><p>Add some text and run an analysis. Your results will appear here.</p></div></section>;
  const polarity = result.mode === "polarity";
  const info = polarity ? getPolarityPresentation(result) : result.label === "distress"
    ? { label: "Distress signal", glyph: "!", description: "The text includes language associated with emotional distress." }
    : { label: "No strong distress signal", glyph: "○", description: "No strong pattern was detected; this does not establish safety." };
  const scoreEntries = Object.entries(result.scores);
  const insight = result.cues.length ? `${polarity ? "The strongest cues included" : "The check noticed language such as"} “${result.cues.join("”, “")}”. Consider the full context and the person behind the words.` : polarity ? "The text contains few strongly emotional terms, so the analysis leans neutral." : "The check did not find direct high-risk phrases. Context can still matter more than wording alone.";
  return <section className="results-panel panel" aria-live="polite"><div className="panel-heading"><div><span className="step">02</span><h3>Your result</h3></div><button className="copy-button" onClick={onCopy}>Copy summary</button></div><div className="results"><div className={`result-hero ${result.label} ${info.mixed ? "mixed" : ""}`}><div className="result-face">{info.glyph}</div><div><p>PRIMARY SIGNAL</p><h3>{info.label}</h3><span>{info.description}</span></div><div className="result-strength"><strong>{result.confidence}%</strong><small>signal share</small></div></div><div className="score-list">{scoreEntries.map(([key, value]) => <div className={`score-row ${key === "supportive" ? "positive" : key === "distress" ? "negative" : key}`} key={key}><div><span>{key === "supportive" ? "No strong distress signal" : title(key)}</span><b>{value}%</b></div><div className="track"><i style={{ width: `${value}%` }} /></div></div>)}</div><div className="insight"><span>✦</span><div><strong>What shaped this result</strong><p>{insight}</p></div></div>{!polarity && <p className="safety-note">This tool cannot diagnose a mental-health condition. If you or someone else may be in immediate danger, contact local emergency services or a trusted crisis service.</p>}</div></section>;
}

export default function Home() {
  const [started, setStarted] = useState(false);
  const [source, setSource] = useState("text");
  const [mode, setMode] = useState("polarity");
  const [values, setValues] = useState({ text: "", document: "", voice: "", social: "" });
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [drawer, setDrawer] = useState(false);
  const [dark, setDark] = useState(false);
  const [toast, setToast] = useState("");
  const [recording, setRecording] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const recognitionRef = useRef(null);
  const currentText = values[source].trim();
  const config = SOURCE_CONFIG[source];

  useEffect(() => {
    setDark(localStorage.getItem("toneleaf-theme") === "dark");
    localStorage.removeItem("toneleaf-history");
    if (location.hash === "#analyze") setStarted(true);
  }, []);
  useEffect(() => { document.body.classList.toggle("dark", dark); localStorage.setItem("toneleaf-theme", dark ? "dark" : "light"); }, [dark]);
  useEffect(() => {
    if (!started) return;
    const frame = requestAnimationFrame(() => window.scrollTo({ top: 0, left: 0, behavior: "auto" }));
    return () => cancelAnimationFrame(frame);
  }, [started]);
  useEffect(() => { if (!toast) return; const timer = setTimeout(() => setToast(""), 2200); return () => clearTimeout(timer); }, [toast]);

  const changeValue = (key, value) => setValues((previous) => ({ ...previous, [key]: value.slice(0, 5000) }));
  const analyze = useCallback(async (override) => {
    const text = (override ?? values[source]).trim();
    if (!text) { setToast(source === "document" ? "Choose a text document first" : "Add some text first"); return; }
    setAnalyzing(true);
    try {
      const analysis = await analyzeLocally(text, mode);
      const next = { ...analysis, mode, source, text, time: Date.now() };
      setResult(next);
      setHistory((previous) => {
        const updated = [next, ...previous.filter((item) => item.text !== text || item.mode !== mode)].slice(0, 12);
        return updated;
      });
    } catch {
      setToast("Start the private Python service, then try again");
    } finally {
      setAnalyzing(false);
    }
  }, [mode, source, values]);

  const readFile = async (selected) => {
    if (!selected) return;
    if (selected.size > 2_000_000) { setToast("Please choose a file under 2 MB"); return; }
    try { const text = await selected.text(); setFile(selected); changeValue("document", text); setToast("Document ready to analyze"); } catch { setToast("This file could not be read"); }
  };
  const copyResult = async () => {
    const scores = Object.entries(result.scores).map(([key, value]) => `${title(key)} ${value}%`).join(", ");
    const resultLabel = result.mode === "polarity" ? getPolarityPresentation(result).label : result.label === "distress" ? "Distress signal" : "No strong distress signal";
    try { await navigator.clipboard.writeText(`Toneleaf: ${resultLabel} (${result.confidence}% signal share). ${scores}`); setToast("Summary copied"); } catch { setToast("Copy is not available here"); }
  };
  const startVoice = () => {
    if (recording) { recognitionRef.current?.stop(); return; }
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) { setToast("Speech recognition is not supported in this browser"); return; }
    const recognition = new Recognition(); recognition.continuous = true; recognition.interimResults = true; recognition.lang = "en-US";
    let finalText = values.voice;
    recognition.onstart = () => setRecording(true);
    recognition.onresult = (event) => { let interim = ""; for (let i = event.resultIndex; i < event.results.length; i++) { if (event.results[i].isFinal) finalText += `${finalText ? " " : ""}${event.results[i][0].transcript}`; else interim += event.results[i][0].transcript; } changeValue("voice", `${finalText}${interim ? ` ${interim}` : ""}`); };
    recognition.onend = () => setRecording(false); recognition.onerror = () => { setRecording(false); setToast("Voice recognition stopped"); }; recognitionRef.current = recognition; recognition.start();
  };
  const loadHistory = (item) => { setSource(item.source); setMode(item.mode); changeValue(item.source, item.text); setResult(item); setDrawer(false); };
  const start = () => { setStarted(true); window.history.replaceState(null, "", "#analyze"); window.scrollTo({ top: 0 }); };
  const goHome = () => { setStarted(false); window.history.replaceState(null, "", location.pathname); window.scrollTo({ top: 0 }); };

  if (!started) return <Welcome onStart={start} />;
  return <main className="workspace">
    <aside className="sidebar"><button onClick={goHome} className="brand-home" aria-label="Return home"><Brand compact /></button><nav className="source-nav" aria-label="Analysis source">{Object.keys(SOURCE_CONFIG).map((key) => <button aria-label={key === "document" ? "File" : title(key)} className={`nav-item ${source === key ? "active" : ""}`} onClick={() => { setSource(key); setResult(null); }} key={key}><span className="nav-icon"><SourceIcon type={key} /></span><span>{key === "document" ? "File" : title(key)}</span></button>)}</nav><button aria-label="Toggle color theme" className="theme-toggle" onClick={() => setDark((value) => !value)}><span className="theme-icon" aria-hidden="true">{dark ? "☀" : "☾"}</span><span>Theme</span></button></aside>
    <section className="content-area"><header className="topbar"><div><p className="breadcrumb">TONELEAF / <span>{config[0]}</span></p><h2>{config[1]}</h2></div><button className="history-button" onClick={() => setDrawer(true)}><span>↺</span> History <b>{history.length}</b></button></header>
      <div className={`mode-switch ${mode === "distress" ? "depression" : ""}`} role="tablist"><button className={`mode ${mode === "polarity" ? "active" : ""}`} onClick={() => { setMode("polarity"); setResult(null); }}>Polarity</button><button className={`mode ${mode === "distress" ? "active" : ""}`} onClick={() => { setMode("distress"); setResult(null); }}>Distress check</button><span className="mode-indicator" /></div>
      <div className="analysis-grid"><section className="input-panel panel"><div className="panel-heading"><div><span className="step">01</span><h3>{config[2]}</h3></div><span className="character-count"><b>{currentText.length}</b> / 5,000</span></div>
        {source === "text" && <div className="source-pane"><textarea maxLength={5000} value={values.text} onChange={(event) => changeValue("text", event.target.value)} placeholder="Type or paste something you want to understand…" /><div className="sample-row"><span>Try an example:</span>{Object.entries(SAMPLES).map(([label, sample]) => <button className="sample" key={label} onClick={() => { changeValue("text", sample); analyze(sample); }}>{label}</button>)}</div></div>}
        {source === "document" && <div className="source-pane"><label className="drop-zone" onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); readFile(event.dataTransfer.files[0]); }}><span className="upload-icon">⇧</span><strong>Drop a text file here</strong><small>or click to browse · TXT, MD, CSV, JSON</small><input type="file" accept=".txt,.md,.csv,.json,text/plain,text/markdown,text/csv,application/json" onChange={(event) => readFile(event.target.files[0])} /></label>{file && <div className="file-card"><span className="file-icon">▤</span><div><strong>{file.name}</strong><small>{(file.size / 1024).toFixed(1)} KB · {values.document.length.toLocaleString()} characters</small></div><button onClick={() => { setFile(null); changeValue("document", ""); }}>×</button></div>}</div>}
        {source === "voice" && <div className="source-pane"><div className="voice-box"><button className={`record-button ${recording ? "recording" : ""}`} onClick={startVoice}><span /></button><strong>{recording ? "Listening… tap to stop" : "Tap to start speaking"}</strong><small>Speech may use your browser provider. For sensitive text, paste a local transcript.</small></div><textarea maxLength={5000} value={values.voice} onChange={(event) => changeValue("voice", event.target.value)} placeholder="Your transcript will appear here…" /></div>}
        {source === "social" && <div className="source-pane"><div className="social-note"><span>⌁</span><div><strong>Analyze a social post</strong><small>Paste the post text below. Private or restricted links cannot be read automatically.</small></div></div><textarea maxLength={5000} value={values.social} onChange={(event) => changeValue("social", event.target.value)} placeholder="Paste the post or comment text here…" /></div>}
        <div className="input-footer"><p><span>i</span>{mode === "polarity" ? " Polarity scores reflect word choice and context cues." : " A screening signal, not a medical diagnosis."}</p><button className="analyze-button" disabled={analyzing} onClick={() => analyze()}>{analyzing ? "Analyzing locally…" : mode === "polarity" ? "Analyze sentiment" : "Check language"}<span>→</span></button></div></section><ResultPanel result={result} onCopy={copyResult} /></div>
      <footer className="app-footer"><span>Private by design · No text history stored</span><span>Designed for quiet, thoughtful reflection</span></footer></section>
    <aside className={`history-drawer ${drawer ? "open" : ""}`} aria-hidden={!drawer}><div className="drawer-head"><div><p>RECENT</p><h3>Analysis history</h3></div><button onClick={() => setDrawer(false)}>×</button></div><div className="history-list">{history.length ? history.map((item) => <div className="history-item" onClick={() => loadHistory(item)} key={`${item.time}-${item.text}`}><p>{item.text}</p><span>{item.source} · {item.mode === "distress" ? "distress check" : item.mode}<b>{item.confidence}% {item.mode === "polarity" ? getPolarityPresentation(item).label : item.label}</b></span></div>) : <p className="history-empty">Your recent analyses will appear here.</p>}</div><button className="clear-history" onClick={() => { localStorage.removeItem("toneleaf-history"); setHistory([]); setToast("History cleared"); }}>Clear history</button></aside><button className={`drawer-backdrop ${drawer ? "open" : ""}`} onClick={() => setDrawer(false)} aria-label="Close history" />
    <div className={`toast ${toast ? "show" : ""}`} role="status">{toast}</div>
  </main>;
}

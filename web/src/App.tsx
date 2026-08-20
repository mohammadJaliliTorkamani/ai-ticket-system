import { FormEvent, useEffect, useMemo, useState } from 'react'
import { AlertCircle, ArrowUpRight, Braces, Check, Code2, Copy, Globe2, KeyRound, LoaderCircle, Send, Terminal } from 'lucide-react'
import './styles.css'
import './workbench.css'
import './provenance.css'

type TranscriptEntry = {
  direction: 'browser_to_ticketifier'|'ticketifier_to_openai'|'openai_to_ticketifier'|'ticketifier_to_browser'
  method?: string; path?: string; status?: number; headers: Record<string,string>; body: Record<string,unknown>|string
}
type Result = {
  status:'completed'; request_id:string; provider_request_id?:string|null; model:string; latency_ms:number; output:string;
  usage:{input_tokens:number;output_tokens:number;total_tokens:number}; transcript:TranscriptEntry[]
}

const labels: Record<TranscriptEntry['direction'], string> = {
  browser_to_ticketifier:'Browser → Ticketifier', ticketifier_to_openai:'Ticketifier → OpenAI',
  openai_to_ticketifier:'OpenAI → Ticketifier', ticketifier_to_browser:'Ticketifier → Browser'
}

function json(value: unknown) { return JSON.stringify(value, null, 2) }

export default function App() {
  const [apiKey,setApiKey]=useState('')
  const [message,setMessage]=useState('Explain idempotency keys with a practical REST example.')
  const [model,setModel]=useState('gpt-5-mini')
  const [result,setResult]=useState<Result|null>(null)
  const [error,setError]=useState('')
  const [busy,setBusy]=useState(false)
  const [copied,setCopied]=useState(false)

  async function submit(event?: FormEvent) {
    event?.preventDefault()
    if (!apiKey.trim() || !message.trim() || busy) return
    setBusy(true); setError(''); setResult(null)
    const requestBody={api_key:apiKey,message:message.trim(),model}
    setApiKey('')
    try {
      const response=await fetch('/api/respond',{method:'POST',headers:{'Content-Type':'application/json','X-Request-ID':crypto.randomUUID()},body:JSON.stringify(requestBody)})
      const body=await response.json().catch(()=>({}))
      if(!response.ok) throw new Error(body.detail||`Request failed with HTTP ${response.status}`)
      setResult(body as Result)
    } catch (caught) { setError((caught as Error).message) } finally { setBusy(false) }
  }

  useEffect(()=>{const keydown=(event:KeyboardEvent)=>{if((event.metaKey||event.ctrlKey)&&event.key==='Enter'){event.preventDefault();void submit()}};addEventListener('keydown',keydown);return()=>removeEventListener('keydown',keydown)})

  const curl=useMemo(()=>`curl --request POST \\\n  --url https://ticketifier.mjalili.com/api/respond \\\n  --header 'Content-Type: application/json' \\\n  --data '${json({api_key:'YOUR_OPENAI_API_KEY',message,model}).replaceAll("'","'\\''")}'`,[message,model])
  async function copyCurl(){await navigator.clipboard.writeText(curl);setCopied(true);setTimeout(()=>setCopied(false),1600)}

  return <main>
    <nav><div className="identity"><a className="brand" href="/"><span>TF</span> Ticketifier</a><span className="project-by">an <a href="https://mjalili.com" target="_blank" rel="noreferrer">MJalili.com</a> project</span></div><div className="nav-meta"><i/> API operational <a href="#transcript">REST transcript</a><a className="source-link" href="https://github.com/MJaliliT/ai-ticket-system" target="_blank" rel="noreferrer"><Code2/> Source code <ArrowUpRight/></a></div></nav>
    <section className="hero"><div className="eyebrow"><Terminal/> LLM REQUEST WORKBENCH</div><h1>One request.<br/><em>Every detail visible.</em></h1><p>Send a message with your own OpenAI key. Ticketifier keeps the secret ephemeral and shows the complete, sanitized REST lifecycle.</p><div className="provenance"><a href="https://github.com/MJaliliT/ai-ticket-system" target="_blank" rel="noreferrer"><Code2/> Open source on GitHub</a><span/><a href="https://mjalili.com" target="_blank" rel="noreferrer"><Globe2/> Part of MJalili.com</a></div></section>
    <section className="workbench">
      <form className="composer" onSubmit={submit}>
        <header><div><span className="step">01</span><div><b>Compose request</b><small>Your key is discarded after submission</small></div></div><span className="secure"><KeyRound/> EPHEMERAL</span></header>
        <label>OpenAI API key<div className="input-shell"><input value={apiKey} onChange={e=>setApiKey(e.target.value)} type="password" autoComplete="off" minLength={20} maxLength={512} required placeholder="sk-proj-…" aria-describedby="key-note"/><span id="key-note">Never stored</span></div></label>
        <label>Message<textarea value={message} onChange={e=>setMessage(e.target.value)} rows={7} maxLength={10000} required/><small className="counter">{message.length.toLocaleString()} / 10,000</small></label>
        {error&&<div className="error" role="alert"><AlertCircle/>{error}</div>}
        <div className="options"><label>Model<select value={model} onChange={e=>setModel(e.target.value)}><option value="gpt-5-mini">gpt-5-mini</option><option value="gpt-5.2">gpt-5.2</option></select></label><button disabled={busy||!apiKey.trim()||!message.trim()}>{busy?<LoaderCircle className="spin"/>:<Send/>}{busy?'Waiting for response…':'Send request'} <kbd>⌘ ↵</kbd></button></div>
      </form>
      <div className={`response-card ${busy?'is-loading':''}`} aria-live="polite">
        <header><div><span className="step">02</span><div><b>Model response</b><small>{busy?'OpenAI is processing the message':result?`Ready in ${(result.latency_ms/1000).toFixed(2)} seconds`:'The result will appear here'}</small></div></div>{result&&<span className="complete"><Check/> 200 OK</span>}</header>
        {busy?<div className="response-wait"><LoaderCircle className="spin"/><b>Request in flight</b><p>The connection stays open until the bounded server timeout completes.</p><div><span/><span/><span/></div></div>:result?<article><pre className="model-output">{result.output}</pre><div className="usage"><span>INPUT <b>{result.usage.input_tokens}</b></span><span>OUTPUT <b>{result.usage.output_tokens}</b></span><span>TOTAL <b>{result.usage.total_tokens}</b></span><span>MODEL <b>{result.model}</b></span></div></article>:<div className="response-empty"><Braces/><b>Awaiting a request</b><p>Use your key and message to inspect a real Responses API round trip.</p></div>}
      </div>
    </section>
    <section className="transcript" id="transcript">
      <div className="section-title"><div><span className="step">03</span><div><b>REST transcript</b><small>Authorization is always replaced with [REDACTED]</small></div></div><button onClick={copyCurl}>{copied?<Check/>:<Copy/>}{copied?'Copied':'Copy as cURL'}</button></div>
      {result?<div className="trace-grid">{result.transcript.map((entry,index)=><article key={`${entry.direction}-${index}`}><header>{entry.method?<span className="method">{entry.method}</span>:<span className="status">{entry.status}</span>}<code>{entry.path}</code><span>{labels[entry.direction]}</span></header><div className="headers"><small>HEADERS</small><pre>{json(entry.headers)}</pre></div><div className="body"><small>BODY</small><pre>{typeof entry.body==='string'?entry.body:json(entry.body)}</pre></div></article>)}</div>:<div className="trace-placeholder"><Terminal/><p>Run a request to capture all four sanitized hops.</p><pre>{curl}</pre></div>}
    </section>
    <footer><span><Braces/> Ticketifier is an open-source <a href="https://mjalili.com" target="_blank" rel="noreferrer">MJalili.com</a> project</span><span><a href="https://github.com/MJaliliT/ai-ticket-system" target="_blank" rel="noreferrer"><Code2/> View source</a> · Keys are never logged or persisted</span></footer>
  </main>
}

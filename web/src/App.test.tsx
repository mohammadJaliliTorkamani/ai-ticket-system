import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'

afterEach(()=>{cleanup();vi.restoreAllMocks();vi.unstubAllGlobals()})

describe('Ticketifier request workbench', () => {
  it('presents the ephemeral BYOK request flow', () => {
    render(<App />)
    expect(screen.getByRole('heading',{name:/One request.*Every detail visible/i})).toBeInTheDocument()
    expect(screen.getByLabelText(/OpenAI API key/i)).toHaveAttribute('type','password')
    expect(screen.getByText(/Authorization is always replaced with \[REDACTED\]/i)).toBeInTheDocument()
    expect(screen.getAllByRole('link',{name:/Open source on GitHub|Source code|View source/i})[0]).toHaveAttribute('href','https://github.com/MJaliliT/ai-ticket-system')
    expect(screen.getAllByRole('link',{name:/MJalili\.com/i})[0]).toHaveAttribute('href','https://mjalili.com')
  })

  it('submits a request and clears the API key field', async () => {
    vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>({status:'completed',request_id:'req-local',model:'gpt-5-mini',latency_ms:123,output:'Hello',usage:{input_tokens:2,output_tokens:1,total_tokens:3},transcript:[]})}))
    render(<App />)
    const key=screen.getByLabelText(/OpenAI API key/i)
    fireEvent.change(key,{target:{value:'sk-test-key-that-is-long-enough'}})
    fireEvent.click(screen.getByRole('button',{name:/Send request/i}))
    await waitFor(()=>expect(screen.getByText('Hello')).toBeInTheDocument())
    expect(key).toHaveValue('')
  })
})

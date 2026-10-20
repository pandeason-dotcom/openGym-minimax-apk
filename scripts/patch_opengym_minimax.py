#!/usr/bin/env python3
"""Patch openGym MiniMax-M3 request schema, latency and one transient transport failure."""
from pathlib import Path
import sys

repo = Path(sys.argv[1] if len(sys.argv) > 1 else "openGym").resolve()
compatible = repo / "api/coach/core/adapters/compatible.js"
transport = repo / "api/coach/core/adapters/http.js"
if not compatible.is_file() or not transport.is_file():
    sys.exit("Missing upstream openGym adapter or transport. Refusing unsafe patch.")

s = compatible.read_text(encoding="utf-8")
needle = "export const compatibleSpec = chatCompletionsSpec('compatible', { maxTokensField: 'max_tokens', temperature: 0, versionlessFallback: true });"
patch = """// MiniMax-M3 does not currently accept response_format. Disable thinking on M3 to
// keep native non-streaming Android requests shorter and less likely to disconnect.
// The core's existing JSON parser and plan-safety validator still run normally.
const baseCompatibleSpec = chatCompletionsSpec('compatible', { maxTokensField: 'max_tokens', temperature: 0, versionlessFallback: true });
const isMiniMaxM3 = model => /^minimax-m3(?:$|[._-])/i.test(String(model || ''));
export const compatibleSpec = {
  ...baseCompatibleSpec,
  body: args => {
    const request = baseCompatibleSpec.body(args);
    if (!isMiniMaxM3(args.model)) return request;
    const { response_format: _unsupported, ...bodyWithoutResponseFormat } = request;
    return { ...bodyWithoutResponseFormat, thinking: { type: 'disabled' } };
  }
};"""
if "thinking: { type: 'disabled' }" in s:
    print("MiniMax adapter already patched")
elif s.count(needle) == 1:
    compatible.write_text(s.replace(needle, patch), encoding="utf-8")
    print("MiniMax schema and low-latency patch installed")
else:
    sys.exit("Unexpected upstream compatible.js; refusing unsafe modification.")

s = transport.read_text(encoding="utf-8")
old = """      let retriedWithoutJsonMode = false;
      let transientRetries = 0;
      for (;;) {"""
new = """      let retriedWithoutJsonMode = false;
      let transientRetries = 0;
      // One opt-in replay for MiniMax-M3 on interrupted sockets, never for HTTP 4xx.
      // An already-submitted request may still be billable even if its reply was lost.
      let minimaxTransportRetries = 0;
      for (;;) {"""
old2 = """        } catch (e) {
          if (e.name === 'AbortError') return { code: -1, text: '', stderr: 'timed out', timedOut: true };
          return { code: 1, text: '', stderr: `could not reach ${hostOf(base)}: ${trim(e.message, 200)}` };
        }
        const { data, text } = await readJson(res);"""
new2 = """        } catch (e) {
          if (e.name === 'AbortError') return { code: -1, text: '', stderr: 'timed out', timedOut: true };
          const interrupted = /Software caused connection abort|Connection reset|ECONNRESET|socket hang up|Broken pipe|unexpected end of stream/i.test(String(e.message || e));
          const miniM3 = id === 'compatible' && /^minimax-m3(?:$|[._-])/i.test(String(chosen));
          if (miniM3 && interrupted && minimaxTransportRetries < 1 && !(signal && signal.aborted)) {
            minimaxTransportRetries++;
            await sleep(1000, signal);
            if (!(signal && signal.aborted)) continue;
          }
          return { code: 1, text: '', stderr: `could not reach ${hostOf(base)}: ${trim(e.message, 200)}` };
        }
        const { data, text } = await readJson(res);"""
if "let minimaxTransportRetries = 0;" in s:
    print("Transport already patched")
elif s.count(old) == 1 and s.count(old2) == 1:
    transport.write_text(s.replace(old, new).replace(old2, new2), encoding="utf-8")
    print("MiniMax interrupted-connection retry patch installed")
else:
    sys.exit("Unexpected upstream HTTP transport; refusing unsafe modification.")

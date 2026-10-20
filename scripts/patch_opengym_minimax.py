#!/usr/bin/env python3
"""Remove unsupported response_format for MiniMax-M3 in openGym's compatible adapter."""
from pathlib import Path
import sys

repo = Path(sys.argv[1] if len(sys.argv) > 1 else "openGym").resolve()
path = repo / "api/coach/core/adapters/compatible.js"
if not path.is_file():
    sys.exit(f"Cannot find openGym adapter: {path}")
s = path.read_text(encoding="utf-8")
needle = "export const compatibleSpec = chatCompletionsSpec('compatible', { maxTokensField: 'max_tokens', temperature: 0, versionlessFallback: true });"
patch = """// MiniMax-M3 rejects json_schema / json_object response_format.
// The model still receives JSON-only instructions; downstream validation is unchanged.
const baseCompatibleSpec = chatCompletionsSpec('compatible', { maxTokensField: 'max_tokens', temperature: 0, versionlessFallback: true });
const isMiniMaxM3 = model => /^minimax-m3(?:$|[._-])/i.test(String(model || ''));
export const compatibleSpec = {
  ...baseCompatibleSpec,
  body: args => {
    const request = baseCompatibleSpec.body(args);
    if (!isMiniMaxM3(args.model)) return request;
    const { response_format: _unsupported, ...bodyWithoutResponseFormat } = request;
    return bodyWithoutResponseFormat;
  }
};"""
if "const isMiniMaxM3 =" in s:
    print(f"Already patched: {path}")
elif s.count(needle) == 1:
    path.write_text(s.replace(needle, patch), encoding="utf-8")
    print(f"Patched: {path}")
else:
    sys.exit("Upstream adapter changed; refusing to patch an unknown location.")

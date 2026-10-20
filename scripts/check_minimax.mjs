import assert from 'node:assert/strict';
import { compatibleSpec } from '../openGym/api/coach/core/adapters/compatible.js';
import compatible from '../openGym/api/coach/core/adapters/compatible.js';

const args = { model: 'MiniMax-M3', prompt: 'Please return JSON', system: '', schema: { type: 'object' }, maxTokens: 16000 };
const fixed = compatibleSpec.body(args);
assert.equal(fixed.model, 'MiniMax-M3');
assert.equal(Object.hasOwn(fixed, 'response_format'), false);
assert.deepEqual(fixed.thinking, { type: 'disabled' });
assert.ok(Array.isArray(fixed.messages));
assert.equal(fixed.max_tokens, 16000);
const normal = compatibleSpec.body({ ...args, model: 'qwen2.5:3b' });
assert.equal(normal.response_format?.type, 'json_schema');
assert.equal(Object.hasOwn(normal, 'thinking'), false);
const miniVariant = compatibleSpec.body({ ...args, model: 'minimax-m3-preview' });
assert.deepEqual(miniVariant.thinking, { type: 'disabled' });
const otherMini = compatibleSpec.body({ ...args, model: 'MiniMax-M2.7' });
assert.equal(otherMini.response_format?.type, 'json_schema');

const cfg = { providerOptions: { compatible: { baseUrl: 'https://api.minimaxi.com/v1' } } };
const env = { OPENAI_COMPAT_API_KEY: 'unit-test-key-not-real' };
const success = { choices: [{ message: { content: '{"coach_contract":1}' }, finish_reason: 'stop' }] };
let n = 0;
const fakeFetch = async (_url, req) => {
  n++;
  const body = JSON.parse(req.body);
  assert.equal(Object.hasOwn(body, 'response_format'), false);
  assert.deepEqual(body.thinking, { type: 'disabled' });
  if (n === 1) throw new Error('Software caused connection abort');
  return new Response(JSON.stringify(success), { status: 200, headers: { 'content-type': 'application/json' } });
};
const result = await compatible.invoke({
  cfg, env, model: 'MiniMax-M3', prompt: 'JSON', schema: args.schema,
  timeoutMs: 12000, fetch: fakeFetch
});
assert.equal(n, 2);
assert.equal(result.code, 0);
assert.equal(result.text, '{"coach_contract":1}');

// Authentication/validation HTTP errors must never be replayed.
let errors = 0;
const errorResult = await compatible.invoke({
  cfg, env, model: 'MiniMax-M3', prompt: 'JSON', timeoutMs: 12000,
  fetch: async () => {
    errors++;
    return new Response(JSON.stringify({ error: { message: 'invalid token' } }), { status: 401 });
  }
});
assert.equal(errors, 1);
assert.equal(errorResult.code, 1);
console.log('PASS: M3 request schema, low latency, one abort retry, and safe HTTP error handling.');

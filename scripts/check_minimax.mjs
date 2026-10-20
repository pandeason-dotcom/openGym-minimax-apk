import assert from 'node:assert/strict';
import { compatibleSpec } from '../openGym/api/coach/core/adapters/compatible.js';

const args = { model: 'MiniMax-M3', prompt: 'Please return JSON', system: '', schema: { type: 'object' }, maxTokens: 16000 };
const fixed = compatibleSpec.body(args);
assert.equal(fixed.model, 'MiniMax-M3');
assert.equal(Object.hasOwn(fixed, 'response_format'), false);
assert.ok(Array.isArray(fixed.messages));
assert.equal(fixed.max_tokens, 16000);
const normal = compatibleSpec.body({ ...args, model: 'qwen2.5:3b' });
assert.equal(normal.response_format?.type, 'json_schema');
const miniVariant = compatibleSpec.body({ ...args, model: 'minimax-m3-preview' });
assert.equal(Object.hasOwn(miniVariant, 'response_format'), false);
const otherMini = compatibleSpec.body({ ...args, model: 'MiniMax-M2.7' });
assert.equal(otherMini.response_format?.type, 'json_schema');
console.log('PASS: MiniMax-M3 removes only response_format; other models unchanged.');

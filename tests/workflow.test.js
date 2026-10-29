// Structural checks on the exported workflow so a bad edit is caught before import.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const file = path.join(__dirname, '..', 'workflow', 'meeting-to-tickets.json');
const wf = JSON.parse(fs.readFileSync(file, 'utf8'));
const byName = Object.fromEntries(wf.nodes.map((n) => [n.name, n]));
const stickies = wf.nodes.filter((n) => n.type === 'n8n-nodes-base.stickyNote');
const nodes = wf.nodes.filter((n) => n.type !== 'n8n-nodes-base.stickyNote');
const next = (name, out = 0) => (wf.connections[name]?.main?.[out] ?? []).map((c) => c.node);

test('every connection points at an existing node', () => {
  for (const [from, kinds] of Object.entries(wf.connections)) {
    assert.ok(byName[from], `source "${from}" missing`);
    for (const outs of Object.values(kinds)) for (const branch of outs) for (const c of branch) {
      assert.ok(byName[c.node], `"${from}" → "${c.node}" target missing`);
    }
  }
});

test('main chain: upload → config → transcribe → guard → summarize → extract → split → classify', () => {
  const chain = ['Upload Recording', 'Config', 'Sarvam: Transcribe', 'Heard Anything?', 'Summarize Meeting',
    'Extract Action Items', 'One Item per Action', 'Classify'];
  for (let i = 0; i < chain.length - 1; i += 1) {
    assert.ok(next(chain[i]).includes(chain[i + 1]), `${chain[i]} should connect to ${chain[i + 1]}`);
  }
  assert.deepEqual(next('Heard Anything?', 1), ["Couldn't Hear"], 'guard false branch → retry page');
});

test('classifier fans out: one branch per category plus other, all ending in the sheet', () => {
  const cats = byName['Classify'].parameters.categories.categories.map((c) => c.category);
  assert.deepEqual(cats, ['bug', 'feature', 'task', 'decision', 'followup']);
  assert.equal(byName['Classify'].parameters.options.fallback, 'other');
  const expected = ['GitHub: Bug Issue', 'GitHub: Feature Issue', 'Tag: Task', 'Tag: Decision', 'Tag: Follow-up', 'Tag: Other'];
  expected.forEach((target, i) => assert.ok(next('Classify', i).includes(target), `output ${i} → ${target}`));
  for (const t of expected) assert.deepEqual(next(t), ['Log to Sheet'], `${t} → Log to Sheet`);
  assert.ok(next('Classify', 2).includes('Jira: Task (disabled)'));
  assert.equal(byName['Jira: Task (disabled)'].disabled, true);
  assert.deepEqual(next('Log to Sheet'), ['Collect Results']);
  assert.deepEqual(next('Collect Results'), ['Show Results']);
});

test('one Sarvam-105B model node powers all three n8n AI nodes', () => {
  const llm = byName['Sarvam-105B'];
  assert.equal(llm.type, '@n8n/n8n-nodes-langchain.lmChatOpenAi');
  assert.match(llm.parameters.model.value, /^sarvam-105b/);
  const fed = wf.connections['Sarvam-105B'].ai_languageModel[0].map((c) => c.node).sort();
  assert.deepEqual(fed, ['Classify', 'Extract Action Items', 'Summarize Meeting']);
});

test('Sarvam nodes use valid community-node parameters', () => {
  for (const n of nodes.filter((n) => n.type === 'n8n-nodes-sarvam.sarvam')) {
    assert.ok(['speech', 'chat'].includes(n.parameters.resource), n.name);
    if (n.parameters.operation === 'speechToText') assert.equal(n.parameters.sttModel, 'saaras:v4');
    if (n.parameters.operation === 'textToSpeech') assert.equal(n.parameters.ttsModel, 'bulbul:v4-flash');
    if (n.parameters.operation === 'complete') assert.equal(n.parameters.chatModel, 'sarvam-105b');
  }
  assert.equal(byName['Sarvam: Transcribe'].parameters.binaryPropertyName, 'recording');
  assert.equal(byName['Upload Recording'].parameters.formFields.values[0].fieldName, 'recording');
});

test('extractor schema is valid JSON with the action_items array', () => {
  const schema = JSON.parse(byName['Extract Action Items'].parameters.inputSchema);
  assert.equal(schema.properties.action_items.type, 'array');
  assert.deepEqual(schema.properties.action_items.items.properties.priority.enum, ['P1', 'P2', 'P3', 'P4']);
  assert.equal(byName['One Item per Action'].parameters.fieldToSplitOut, 'output.action_items');
});

test('no credential ids or secrets are baked into the export', () => {
  const raw = fs.readFileSync(file, 'utf8');
  assert.doesNotMatch(raw, /sk_[A-Za-z0-9]{10,}/, 'Sarvam key leaked');
  assert.doesNotMatch(raw, /gh[pos]_[A-Za-z0-9]{10,}/, 'GitHub token leaked');
  for (const n of nodes) for (const cred of Object.values(n.credentials ?? {})) assert.equal(cred.id, undefined, n.name);
});

test('every node sits inside a sticky note panel (workshop layout)', () => {
  const inside = (n, s) => {
    const [x, y] = n.position; const [sx, sy] = s.position;
    return x >= sx && x + 100 <= sx + s.parameters.width && y >= sy && y + 100 <= sy + s.parameters.height;
  };
  for (const n of nodes) assert.ok(stickies.some((s) => inside(n, s)), `"${n.name}" is not inside any sticky panel`);
});

test('sticky images use URLs n8n will render (https:// or /static/) and the files exist', () => {
  const imgs = stickies.flatMap((n) => [...n.parameters.content.matchAll(/!\[[^\]]*\]\(([^)]+)\)/g)].map((m) => m[1]));
  assert.ok(imgs.length >= 4);
  for (const src of imgs) {
    assert.match(src, /^(https:\/\/|\/static\/).*\.(gif|png|jpe?g|webp)$/, `n8n would strip image ${src}`);
    if (src.startsWith('/static/workshop/')) assert.ok(fs.existsSync(path.join(__dirname, '..', 'assets', path.basename(src))));
  }
});

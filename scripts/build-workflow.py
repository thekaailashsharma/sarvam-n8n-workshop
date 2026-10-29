#!/usr/bin/env python3
"""Generates workflow/meeting-to-tickets.json: nodes, wiring, sticky notes.
`npm run build` runs make-assets.py → this → sync-code-node.mjs (no code node in this version; sync is a no-op)."""
import json, os, pathlib, uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "workflow" / "meeting-to-tickets.json"

# n8n's sticky sanitizer only renders images whose src is https://… or /static/… (data: URIs are stripped).
# docker-compose mounts ./assets at /static/workshop. ASSET_BASE=https://raw.githubusercontent.com/<owner>/<repo>/main/assets
# produces a JSON that works on any n8n.
ASSET_BASE = os.environ.get("ASSET_BASE", "/static/workshop").rstrip("/")
HERO = f"{ASSET_BASE}/hero.gif"
ICON = {k: f"{ASSET_BASE}/{k}.png" for k in ("hear", "think", "speak")}

GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "thekaailashsharma")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "sarvam-n8n-workshop")
SHEET_ID = os.environ.get("SHEET_ID", "1VMB0tBNve0teNcL176g5Yvo9ElCld657Ab0aPY72uZA")
# Spoken first name → GitHub login. Demo maps everyone to the repo owner (the only collaborator); edit for your team.
TEAM = {"arjun": GITHUB_OWNER, "neha": GITHUB_OWNER, "kabir": GITHUB_OWNER, "rahul": GITHUB_OWNER, "priya": GITHUB_OWNER}

def nid(): return str(uuid.uuid4())

nodes, connections = [], {}
def add(n): nodes.append(n); return n["name"]
def link(a, b, out=0, kind="main"):
    c = connections.setdefault(a, {}).setdefault(kind, [])
    while len(c) <= out: c.append([])
    c[out].append({"node": b, "type": kind, "index": 0})
def sticky(name, content, x, y, w, h, color):
    add({"parameters": {"content": content, "height": h, "width": w, "color": color}, "id": nid(), "name": name,
         "type": "n8n-nodes-base.stickyNote", "typeVersion": 1, "position": [x, y]})
def node(name, type_, version, params, x, y, **extra):
    n = {"parameters": params, "id": nid(), "name": name, "type": type_, "typeVersion": version, "position": [x, y]}
    n.update(extra); return add(n)
def sarvam(name, params, x, y): return node(name, "n8n-nodes-sarvam.sarvam", 1, params, x, y)
def manual(name, x, y): return node(name, "n8n-nodes-base.manualTrigger", 1, {}, x, y)
def tag(name, type_value, x, y):
    return node(name, "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [
        {"id": nid(), "name": "type", "value": type_value, "type": "string"}]}, "includeOtherFields": True, "options": {}}, x, y)

# ═══════════════════════════ HERO + WARM-UP ═══════════════════════════
sticky("Sticky: Hero", f"""# 🎙️ Meeting → Tickets
![pipeline]({HERO})
Speak in any Indian language. Every action item becomes a **GitHub issue** or a **sheet row**, sorted by what it is.
**Sarvam AI × n8n** · Saaras v4 hears · Sarvam-105B thinks · n8n routes
""", -20, -620, 820, 440, 7)

sticky("Sticky: Warm-up", "## 🧪 Warm-up · one node at a time\nThree Sarvam skills, three tiny chains. Open a node → **Test step**.", 880, -620, 1560, 100, 4)
WY = -440
sticky("Sticky: Warm-up STT", f"### 🎧 Hear · Saaras v4\n![hear]({ICON['hear']})\nHinglish stand-up → English transcript + detected language.", 880, WY - 60, 500, 340, 7)
a1 = manual("▶ Hear", 920, WY + 120)
a2 = node("Try: Read sample", "n8n-nodes-base.readWriteFile", 1, {"fileSelector": "/samples/standup-hinglish.wav", "options": {}}, 1080, WY + 120)
a3 = sarvam("Try: Speech to Text", {"resource": "speech", "operation": "speechToText", "binaryPropertyName": "data",
            "sttMode": "translate", "sttModel": "saaras:v4", "speechToTextOptions": {"language_code": "unknown"}}, 1240, WY + 120)
link(a1, a2); link(a2, a3)
sticky("Sticky: Warm-up Chat", f"### 🧠 Think · Sarvam-105B\n![think]({ICON['think']})\nAsk in Hinglish, answer in English. Reasoning off → fast.", 1400, WY - 60, 500, 340, 7)
b1 = manual("▶ Think", 1480, WY + 120)
b2 = sarvam("Try: Chat", {"resource": "chat", "operation": "complete", "chatModel": "sarvam-105b",
            "userMessage": "Is meeting note se action items nikaalo, English mein, bullet list: 'Arjun login bug aaj fix karega, Neha next sprint mein Hindi invoice design karegi.'",
            "systemMessage": "You are a concise assistant.", "chatOptions": {"temperature": 0, "max_tokens": 512, "reasoning_effort": "none"}}, 1700, WY + 120)
link(b1, b2)
sticky("Sticky: Warm-up TTS", f"### 🔊 Speak · Bulbul v4-flash\n![speak]({ICON['speak']})\nHindi text → MP3 you can play in the output panel.", 1920, WY - 60, 500, 340, 7)
c1 = manual("▶ Speak", 2000, WY + 120)
c2 = sarvam("Try: Text to Speech", {"resource": "speech", "operation": "textToSpeech", "ttsModel": "bulbul:v4-flash",
            "ttsSpeakerV4": "aarti_hi_customer", "ttsTargetLanguage": "hi-IN",
            "text": "नमस्ते! मीटिंग के सभी एक्शन आइटम गिटहब पर बना दिए गए हैं।",
            "textToSpeechOptions": {"output_audio_codec": "mp3"}}, 2220, WY + 120)
link(c1, c2)

# ═══════════════════════════ MAIN PIPELINE ═══════════════════════════
sticky("Sticky: Pipeline", "## 🚀 The workflow · recording → classified, assigned tickets\n**Upload Recording** → *Test step* → drop in `samples/standup-hinglish.wav` → watch the classifier fan out → open the results page.", -20, -120, 3200, 100, 5)

Y = 300
def X(i): return i * 300
def stage(i, name, title, body, color=7, w=260, h=420, dy=-160):
    sticky(name, f"### {title}\n{body}", X(i) - 40, Y + dy, w, h, color)

stage(0, "Sticky: Upload", "1 · Upload", "Any audio, ≤ 30 s. Optional meeting title.")
stage(1, "Sticky: Config", "2 · Config ✏️", "GitHub repo, sheet ID and the **team directory** (spoken name → GitHub login).", 5)
stage(2, "Sticky: Hear", "3 · Hear 🎧", "Saaras v4 translates any language to English and tells you which one it heard.")
stage(3, "Sticky: Guard", "4 · Guard 🛡️", "Silence or noise → a polite retry page, never a garbage ticket.", h=480)
stage(4, "Sticky: Summarize", "5 · Summarize 📝", "n8n Summarization Chain → 4-6 bullets for people who missed the meeting.", 6)
stage(5, "Sticky: Extract", "6 · Extract 🔍", "n8n Information Extractor + JSON schema → problem, expected, impact, acceptance criteria, owner, priority, due.", 6)
stage(6, "Sticky: Split", "7 · Split ✂️", "One item per action. From here on, each row is a ticket.")
stage(7, "Sticky: Assign", "8 · Assign 👤", "Looks the spoken name up in the team directory → GitHub login. Unknown names stay unassigned but are kept in the body.", 5)
stage(8, "Sticky: Classify", "9 · Classify 🏷️", "n8n Text Classifier: bug · feature · task · decision · follow-up. One output per class.", 6, h=620, dy=-360)

n0 = node("Upload Recording", "n8n-nodes-base.formTrigger", 2.5, {
    "formTitle": "Turn a meeting into tickets",
    "formDescription": "Upload a recording or voice note in any Indian language (up to 30 seconds for the real-time API).",
    "formFields": {"values": [
        {"fieldLabel": "Recording", "fieldName": "recording", "fieldType": "file",
         "acceptFileTypes": ".wav,.mp3,.m4a,.ogg,.webm,.aac,.flac", "multipleFiles": False, "requiredField": True},
        {"fieldLabel": "Meeting title", "fieldName": "meeting_title", "placeholder": "e.g. Payments stand-up"},
    ]},
    "options": {"buttonLabel": "Create tickets"},
}, X(0), Y, webhookId=nid())

n1 = node("Config", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [
    {"id": nid(), "name": "githubOwner", "value": GITHUB_OWNER, "type": "string"},
    {"id": nid(), "name": "githubRepo", "value": GITHUB_REPO, "type": "string"},
    {"id": nid(), "name": "sheetId", "value": SHEET_ID, "type": "string"},
    {"id": nid(), "name": "team", "value": json.dumps(TEAM), "type": "string"},
]}, "includeOtherFields": True, "options": {}}, X(1), Y)

n2 = sarvam("Sarvam: Transcribe", {"resource": "speech", "operation": "speechToText", "binaryPropertyName": "recording",
            "sttMode": "translate", "sttModel": "saaras:v4", "speechToTextOptions": {"language_code": "unknown"}}, X(2), Y)

n3 = node("Heard Anything?", "n8n-nodes-base.if", 2.4, {"conditions": {
    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 4},
    "conditions": [{"id": nid(), "leftValue": "={{ ($json.transcript || '').trim().length }}", "rightValue": 20,
                    "operator": {"type": "number", "operation": "gt"}}],
    "combinator": "and"}, "options": {}}, X(3), Y)

n3b = node("Couldn't Hear", "n8n-nodes-base.form", 2.5, {"operation": "completion", "respondWith": "text",
    "completionTitle": "We couldn't hear anything 🎧",
    "completionMessage": "The recording seems silent or too short. Please try again with a clearer file.", "options": {}},
    X(3), Y + 200, webhookId=nid())

n4 = node("Summarize Meeting", "@n8n/n8n-nodes-langchain.chainSummarization", 2.1, {
    "operationMode": "nodeInputJson", "chunkingMode": "simple", "chunkSize": 60000, "chunkOverlap": 0,
    "options": {"summarizationMethodAndPrompts": {"values": {"summarizationMethod": "stuff",
        "prompt": "Write a crisp meeting summary for people who were not there.\n4-6 short bullets: what was discussed, what was decided, blockers.\nPlain text bullets starting with '- '. No preamble.\n\nTranscript:\n\"{text}\"\n\nSUMMARY:"}}}},
    X(4), Y)

n5 = node("Extract Action Items", "@n8n/n8n-nodes-langchain.informationExtractor", 1.2, {
    "text": "={{ $('Sarvam: Transcribe').item.json.transcript }}",
    "schemaType": "manual",
    "inputSchema": json.dumps({
        "type": "object",
        "properties": {"action_items": {"type": "array", "description": "Every concrete action item, decision or follow-up mentioned. One entry each.",
            "items": {"type": "object", "properties": {
                "title": {"type": "string", "description": "Imperative, max 80 chars, e.g. 'Fix checkout crash on Android UPI'"},
                "problem": {"type": "string", "description": "One line: what is broken, missing or needed, as stated in the meeting"},
                "expected": {"type": "string", "description": "One line: what 'done' looks like / the expected behaviour or outcome"},
                "impact": {"type": "string", "description": "One line: who is affected and why it matters (release, customers, revenue). Empty if not stated"},
                "acceptance_criteria": {"type": "array", "items": {"type": "string"}, "description": "2-3 short, testable checks that would close this item. Infer sensibly from the problem; do not invent facts"},
                "owner": {"type": "string", "description": "Person named as responsible, else empty string"},
                "priority": {"type": "string", "enum": ["P1", "P2", "P3", "P4"], "description": "P1 blocker/outage, P2 urgent, P3 normal, P4 nice-to-have"},
                "due": {"type": "string", "description": "Deadline as spoken, e.g. 'Wednesday', 'before launch', else empty"}},
                "required": ["title", "problem", "expected", "impact", "acceptance_criteria", "owner", "priority", "due"]}}},
        "required": ["action_items"]}, indent=2),
    "options": {"systemPromptTemplate": "You are a senior product manager writing tickets from a meeting transcript. Extract every action item, decision and follow-up. Write like a PM: crisp one-liners, concrete expected outcome, testable acceptance criteria. Never invent names, dates or numbers that were not said. {format_instructions}"},
}, X(5), Y)

n6 = node("One Item per Action", "n8n-nodes-base.splitOut", 1, {"fieldToSplitOut": "output.action_items", "include": "noOtherFields", "options": {}}, X(6), Y)

CATS = [("bug", "Something is broken, crashing, failing or behaving wrongly and needs a fix."),
        ("feature", "New user-facing capability, enhancement or design work that customers would notice."),
        ("task", "Internal engineering or ops work to do: security hardening, config, setup, migration, runbook, docs."),
        ("decision", "Something the team agreed or settled ('we decided', 'will be', 'policy is'): a rule, timing or policy to record. No build work."),
        ("followup", "Chasing or waiting on someone: ask, remind, check back, get a reply or a document.")]
n6b = node("Resolve Owner", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [
    {"id": nid(), "name": "assignee", "type": "string",
     "value": "={{ (JSON.parse($('Config').item.json.team)[($json.owner || '').trim().toLowerCase().split(' ')[0]]) || '' }}"}]},
    "includeOtherFields": True, "options": {}}, X(7), Y)
n7 = node("Classify", "@n8n/n8n-nodes-langchain.textClassifier", 1.1, {
    "inputText": "={{ $json.title }} — {{ $json.problem }}",
    "categories": {"categories": [{"category": c, "description": d} for c, d in CATS]},
    "options": {"fallback": "other", "systemPromptTemplate": "Classify the meeting action item into exactly one category.\n{categories}\n\nJust the category label."}}, X(8), Y)

LLM = node("Sarvam-105B", "@n8n/n8n-nodes-langchain.lmChatOpenAi", 1.2,
           {"model": {"__rl": True, "mode": "id", "value": "sarvam-105b-conversations"}, "options": {"temperature": 0, "maxTokens": 2048}}, X(5) - 60, Y + 220)
sticky("Sticky: LLM", "### 🧠 Sarvam-105B is the brain\nOne OpenAI Chat Model node, Base URL `https://api.sarvam.ai/v1`, powers all three n8n AI nodes. `-conversations` answers directly; plain `sarvam-105b` thinks first and needs a bigger token budget.", X(4) - 40, Y + 170, 560, 220, 6)

# ── branches ──
BX = X(9) + 60
BYS = {"bug": Y - 320, "feature": Y - 160, "task": Y, "decision": Y + 160, "followup": Y + 320, "other": Y + 480}
sticky("Sticky: Branches", "### 10 · Branch out 🔀\n**bug / feature** → GitHub issues, labelled, assigned, with problem / expected / acceptance criteria · **task** → Jira (disabled, swap in yours) + sheet · **decision / follow-up** → sheet.", BX - 40, Y - 480, 600, 1100, 1)

def gh_issue(name, label, y, kind):
    return node(name, "n8n-nodes-base.github", 1.1, {
        "authentication": "accessToken", "resource": "issue", "operation": "create",
        "owner": {"__rl": True, "mode": "name", "value": "={{ $('Config').item.json.githubOwner }}"},
        "repository": {"__rl": True, "mode": "name", "value": "={{ $('Config').item.json.githubRepo }}"},
        "title": "={{ $json.title }}",
        "body": ("={{ [\n"
                 f"  '## {kind[0]}', $json.problem, '',\n"
                 f"  '## {kind[1]}', $json.expected, '',\n"
                 "  ...($json.impact ? ['## 📌 Impact', $json.impact, ''] : []),\n"
                 "  '## 🎯 Acceptance criteria', ...(($json.acceptance_criteria || []).map(c => '- [ ] ' + c)), '',\n"
                 "  '---',\n"
                 "  '**Owner** ' + ($json.owner || '—') + ($json.assignee ? ' (@' + $json.assignee + ')' : '') + ' · **Priority** ' + $json.priority + ' · **Due** ' + ($json.due || '—'),\n"
                 "  '**Meeting** ' + ($('Upload Recording').item.json.meeting_title || 'untitled') + ' · **Spoken language** ' + $('Sarvam: Transcribe').item.json.language_code,\n"
                 "  '', '_Created from a voice recording by Sarvam Saaras v4 + Sarvam-105B via n8n._'\n"
                 "].join('\\n') }}"),
        "labels": [{"label": label}],
        "assignees": "={{ $json.assignee ? [{ assignee: $json.assignee }] : [] }}"}, BX, y)

g1 = gh_issue("GitHub: Bug Issue", "bug", BYS["bug"], ("🐛 Problem", "✅ Expected behaviour"))
g2 = gh_issue("GitHub: Feature Issue", "enhancement", BYS["feature"], ("✨ What we need", "✅ Expected outcome"))
j1 = node("Jira: Task (disabled)", "n8n-nodes-base.jira", 1, {"resource": "issue", "operation": "create",
          "project": {"__rl": True, "mode": "list", "value": ""}, "issueType": {"__rl": True, "mode": "list", "value": ""},
          "summary": "={{ $json.title }}", "additionalFields": {"description": "={{ $json.problem }}\n\nExpected: {{ $json.expected }}"}}, BX + 220, BYS["task"] - 80, disabled=True)
t1 = tag("Tag: Task", "task", BX, BYS["task"])
t2 = tag("Tag: Decision", "decision", BX, BYS["decision"])
t3 = tag("Tag: Follow-up", "followup", BX, BYS["followup"])
t4 = tag("Tag: Other", "other", BX, BYS["other"])
for i, (c, _) in enumerate(CATS):
    link(n7, {"bug": g1, "feature": g2, "task": t1, "decision": t2, "followup": t3}[c], out=i)
link(n7, t4, out=len(CATS))
link(n7, j1, out=2)

# ── record + finish ──
RX = BX + 520
sticky("Sticky: Record", "### 11 · Record + report 📋\nBranches merge → one sheet row per item, GitHub link included → the uploader sees the summary and every ticket.", RX - 240, Y - 160, 1020, 420, 4)
ITEM = "$('One Item per Action').item.json"
COLS = [("Created", "={{ $now.toISO() }}"), ("Meeting", "={{ $('Upload Recording').item.json.meeting_title || 'untitled' }}"),
        ("Type", "={{ $json.type ?? ($json.labels && $json.labels[0] ? $json.labels[0].name : '') }}"),
        ("Title", f"={{{{ {ITEM}.title }}}}"), ("Problem", f"={{{{ {ITEM}.problem }}}}"), ("Expected", f"={{{{ {ITEM}.expected }}}}"),
        ("Owner", f"={{{{ {ITEM}.owner }}}}"), ("Assignee", f"={{{{ {ITEM}.assignee ? '@' + {ITEM}.assignee : '' }}}}"),
        ("Priority", f"={{{{ {ITEM}.priority }}}}"), ("Due", f"={{{{ {ITEM}.due }}}}"), ("Link", "={{ $json.html_url ?? '' }}"), ("Status", "Open")]
m1 = node("Merge Branches", "n8n-nodes-base.merge", 3.2, {"mode": "append", "numberInputs": 6}, RX - 200, Y)
s1 = node("Log to Sheet", "n8n-nodes-base.googleSheets", 4.7, {
    "operation": "append",
    "documentId": {"__rl": True, "mode": "id", "value": "={{ $('Config').item.json.sheetId }}"},
    "sheetName": {"__rl": True, "mode": "name", "value": "Tickets"},
    "columns": {"mappingMode": "defineBelow", "value": dict(COLS), "matchingColumns": [],
                "schema": [{"id": c, "displayName": c, "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True} for c, _ in COLS]},
    "options": {"cellFormat": "USER_ENTERED"}}, RX, Y)
for i, src in enumerate((g1, g2, t1, t2, t3, t4)):
    connections.setdefault(src, {}).setdefault("main", [[]])[0].append({"node": m1, "type": "main", "index": i})
link(m1, s1)

s2 = node("Collect Results", "n8n-nodes-base.aggregate", 1, {"aggregate": "aggregateAllItemData", "options": {}}, RX + 240, Y)
link(s1, s2)

RESULT_HTML = """={{ (() => {
  const items = $json.data || [];
  const summary = ($('Summarize Meeting').first().json.response?.text ?? $('Summarize Meeting').first().json.output?.text ?? '').toString();
  const lang = $('Sarvam: Transcribe').first().json.language_code;
  const row = (i) => `<li><b>${i.Type}</b> · ${i.Link ? `<a href="${i.Link}" target="_blank">${i.Title}</a>` : i.Title} <small>${i.Priority}${i.Owner ? ' · ' + i.Owner : ''}${i.Assignee ? ' ' + i.Assignee : ''}</small></li>`;
  return `<div style="font-family:system-ui;max-width:720px;margin:40px auto;line-height:1.5">
    <h1>✅ ${items.length} item${items.length === 1 ? '' : 's'} created</h1>
    <p style="color:#666">Spoken language: ${lang} · transcribed by Sarvam Saaras v4 · triaged by Sarvam-105B</p>
    <h3>Summary</h3><pre style="white-space:pre-wrap;background:#f6f6f8;padding:12px;border-radius:8px">${summary}</pre>
    <h3>Tickets</h3><ul>${items.map(row).join('')}</ul></div>`;
})() }}"""
s3 = node("Show Results", "n8n-nodes-base.form", 2.5, {"operation": "completion", "respondWith": "showText",
          "responseText": RESULT_HTML, "options": {}}, RX + 480, Y, webhookId=nid())
link(s2, s3)

# ── main chain wiring ──
for a, b in [(n0, n1), (n1, n2), (n2, n3), (n4, n5), (n5, n6), (n6, n6b), (n6b, n7)]: link(a, b)
link(n3, n4, out=0); link(n3, n3b, out=1)
for consumer in (n4, n5, n7): link(LLM, consumer, kind="ai_languageModel")

wf = {"name": "Meeting → Tickets (Sarvam AI)", "nodes": nodes, "connections": connections,
      "settings": {"executionOrder": "v1"}, "pinData": {}, "meta": {"templateCredsSetupCompleted": False}, "tags": []}
OUT.write_text(json.dumps(wf, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {OUT.relative_to(ROOT)}: {len(nodes)} nodes, {OUT.stat().st_size // 1024} KB")

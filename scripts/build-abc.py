#!/usr/bin/env python3
"""workflow/abcs-of-n8n.json — a spacious, visual node reference. Each section is self-contained
(its own ▶ Run trigger where runnable). Original content by Abhay (abhay.co/go)."""
import json, os, pathlib, uuid
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "workflow" / "abcs-of-n8n.json"
A = os.environ.get("ASSET_BASE", "/static/workshop").rstrip("/") + "/abc"
def nid(): return str(uuid.uuid4())
nodes, connections = [], {}
def add(n): nodes.append(n); return n["name"]
def link(a, b, out=0, kind="main", idx=0):
    c = connections.setdefault(a, {}).setdefault(kind, [])
    while len(c) <= out: c.append([])
    c[out].append({"node": b, "type": kind, "index": idx})
def sticky(name, content, x, y, w, h, color=7):
    add({"parameters": {"content": content, "height": h, "width": w, "color": color}, "id": nid(), "name": name,
         "type": "n8n-nodes-base.stickyNote", "typeVersion": 1, "position": [x, y]})
def node(name, type_, version, params, x, y, **extra):
    n = {"parameters": params, "id": nid(), "name": name, "type": type_, "typeVersion": version, "position": [x, y]}; n.update(extra); return add(n)

# ── grid: wide pitch, tall cards, big gaps ──
X0, PITCH, CW, CH = 0, 360, 300, 330
SAMPLE = "return [\n  { json: { name: 'Priya', score: 92, isActive: true,  tags: ['n8n', 'ai'] } },\n  { json: { name: 'Arjun', score: 67, isActive: true,  tags: ['automation'] } },\n  { json: { name: 'Neha',  score: 48, isActive: false, tags: ['design', 'ux'] } },\n  { json: { name: 'Kabir', score: 88, isActive: true,  tags: ['backend'] } },\n];"

def section(key, y): sticky(f"Section {key}", f"![{key}]({A}/{key}.gif)", X0, y, 2560, 220, 7)
_cards = {}
def card(title, pic, line, col, y, w=CW, h=CH):
    x = X0 + col * PITCH
    _cards[title] = _cards.get(title, 0) + 1
    name = f"Card: {title}" + (f" {_cards[title]}" if _cards[title] > 1 else "")
    sticky(name, f"![{pic}]({A}/{pic}.png)\n### {title}\n{line}", x, y, w, h, 7)
    return x + 100, y + 190       # node position inside the card
def runner(col, y, key):
    """▶ Run + Sample data pair that starts a self-contained chain."""
    x, ny = card("▶ Run", "bolt", "press Execute", col, y); t = node(f"Run {key}", "n8n-nodes-base.manualTrigger", 1, {}, x, ny)
    x, ny = card("Sample data", "code-" + key, "4 people, scores, tags", col + 1, y); s = node(f"Sample data ({key})", "n8n-nodes-base.code", 2, {"jsCode": SAMPLE}, x, ny)
    link(t, s); return s

# ═════════ HERO ═════════
sticky("Hero", f"![hero]({A}/hero.gif)\nBased on Abhay's node reference · abhay.co/go · remixed for the Sarvam × n8n workshop", X0, -420, 2560, 330, 7)

Y = 0
# ═════════ A · TRIGGERS (shown, not wired) ═════════
section("triggers", Y); Y += 280
x, y = card("Manual", "bolt", "you press Execute", 0, Y); node("Manual Trigger", "n8n-nodes-base.manualTrigger", 1, {}, x, y)
x, y = card("Schedule", "clock", "every hour, cron, daily", 1, Y); node("Schedule Trigger", "n8n-nodes-base.scheduleTrigger", 1.3, {"rule": {"interval": [{"field": "hours"}]}}, x, y)
x, y = card("Webhook", "hook", "an app calls your URL", 2, Y); node("Webhook Trigger", "n8n-nodes-base.webhook", 2.1, {"httpMethod": "POST", "path": "abc-n8n", "responseMode": "lastNode", "options": {}}, x, y, webhookId=nid())
x, y = card("Form", "form", "a hosted web form", 3, Y); node("Form Trigger", "n8n-nodes-base.formTrigger", 2.5, {"formTitle": "Contact form", "formFields": {"values": [{"fieldLabel": "Name", "fieldName": "name", "requiredField": True}, {"fieldLabel": "Email", "fieldName": "email"}]}, "options": {}}, x, y, webhookId=nid())
x, y = card("Gmail", "mail", "a new email arrives", 4, Y); node("Gmail Trigger", "n8n-nodes-base.gmailTrigger", 1.3, {"pollTimes": {"item": [{"mode": "everyMinute"}]}, "filters": {}}, x, y)
x, y = card("Sub-workflow", "loop", "another workflow calls this", 5, Y); node("Called by Another Workflow", "n8n-nodes-base.executeWorkflowTrigger", 1.1, {"inputSource": "passthrough"}, x, y)
x, y = card("Chat", "chat-trigger", "a message in the chat UI", 6, Y); node("Chat Trigger (ref)", "@n8n/n8n-nodes-langchain.chatTrigger", 1.3, {"public": True, "options": {}}, x, y, webhookId=nid())
Y += CH + 160

# ═════════ B · DATA (runnable) ═════════
section("data", Y); Y += 280
s = runner(0, Y, "data")
x, y = card("Edit Fields", "pencil", "add greeting + level", 2, Y); d1 = node("Edit Fields", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [{"id": nid(), "name": "greeting", "value": "=Hello {{ $json.name }}!", "type": "string"}, {"id": nid(), "name": "level", "value": "={{ $json.score >= 80 ? 'gold' : 'silver' }}", "type": "string"}]}, "includeOtherFields": True, "options": {}}, x, y)
x, y = card("Date & Time", "cal", "stamp today's date", 3, Y); d2 = node("Date & Time", "n8n-nodes-base.dateTime", 2, {"operation": "formatDate", "date": "={{ $now }}", "format": "yyyy-MM-dd", "outputFieldName": "today", "options": {"includeInputFields": True}}, x, y)
x, y = card("Filter", "funnel", "keep score ≥ 50", 4, Y); d3 = node("Filter", "n8n-nodes-base.filter", 2.2, {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2}, "conditions": [{"id": nid(), "leftValue": "={{ $json.score }}", "rightValue": 50, "operator": {"type": "number", "operation": "gte"}}], "combinator": "and"}, "options": {}}, x, y)
x, y = card("Split Out", "scissors", "one item per tag", 5, Y); d4 = node("Split Out", "n8n-nodes-base.splitOut", 1, {"fieldToSplitOut": "tags", "include": "allOtherFields", "options": {}}, x, y)
x, y = card("Aggregate", "box", "collect tags back", 6, Y); d5 = node("Aggregate", "n8n-nodes-base.aggregate", 1, {"aggregate": "aggregateIndividualFields", "fieldsToAggregate": {"fieldToAggregate": [{"fieldToAggregate": "tags"}]}, "options": {}}, x, y)
for a, b in [(s, d1), (d1, d2), (d2, d3), (d3, d4), (d4, d5)]: link(a, b)
Y += CH + 160

# ═════════ C · FLOW CONTROL (runnable) ═════════
section("flow", Y); Y += 280
s = runner(0, Y, "flow")
x, y = card("IF", "fork", "score ≥ 80 ?", 2, Y); f1 = node("IF", "n8n-nodes-base.if", 2.4, {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 4}, "conditions": [{"id": nid(), "leftValue": "={{ $json.score }}", "rightValue": 80, "operator": {"type": "number", "operation": "gte"}}], "combinator": "and"}, "options": {}}, x, y)
x, y = card("Two paths", "pencil-flow", "grade A or grade B", 3, Y)
f2 = node("Grade A", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [{"id": nid(), "name": "grade", "value": "A", "type": "string"}]}, "includeOtherFields": True, "options": {}}, x, y - 50)
f3 = node("Grade B", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [{"id": nid(), "name": "grade", "value": "B", "type": "string"}]}, "includeOtherFields": True, "options": {}}, x, y + 50)
x, y = card("Merge", "merge", "back to one stream", 4, Y); f4 = node("Merge", "n8n-nodes-base.merge", 3.2, {"mode": "append", "numberInputs": 2}, x, y)
x, y = card("Loop", "cycle", "2 items per batch", 5, Y); f5 = node("Loop Over Items", "n8n-nodes-base.splitInBatches", 3, {"batchSize": 2, "options": {}}, x, y)
x, y = card("Batch · Done", "box-flow", "work, then finish", 6, Y)
f6 = node("Process Batch", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [{"id": nid(), "name": "batchDone", "value": True, "type": "boolean"}]}, "includeOtherFields": True, "options": {}}, x, y + 50)
f7 = node("All Done", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [{"id": nid(), "name": "summary", "value": "=All {{ $input.all().length }} items processed", "type": "string"}]}, "options": {}}, x, y - 50)
link(s, f1); link(f1, f2, 0); link(f1, f3, 1); link(f2, f4, idx=0); link(f3, f4, idx=1); link(f4, f5); link(f5, f7, 0); link(f5, f6, 1); link(f6, f5)
Y += CH + 160

# ═════════ D · AI AGENT (runnable via chat) ═════════
section("ai", Y); Y += 280
x, y = card("Chat Trigger", "chat-trigger", "open chat → ask anything", 0, Y); ct = node("Chat Trigger", "@n8n/n8n-nodes-langchain.chatTrigger", 1.3, {"public": True, "options": {}}, x, y, webhookId=nid())
x, y = card("AI Agent", "brain", "reasons, then answers", 1, Y); ag = node("AI Agent", "@n8n/n8n-nodes-langchain.agent", 3.1, {"options": {"systemMessage": "You are a concise, friendly assistant for an n8n workshop in India. Reply in the language the user writes in."}}, x, y)
x, y = card("Respond to Chat", "chat", "reply in the chat UI", 2, Y); rc = node("Respond to Chat", "@n8n/n8n-nodes-langchain.chat", 1.3, {"message": "={{ $json.output }}", "options": {}}, x, y)
x, y = card("Model", "chip", "Sarvam-105B · OpenAI-compatible", 1, Y + CH + 40); lm = node("Sarvam-105B", "@n8n/n8n-nodes-langchain.lmChatOpenAi", 1.2, {"model": {"__rl": True, "mode": "id", "value": "sarvam-105b-conversations"}, "options": {"temperature": 0.2, "maxTokens": 1024}}, x, y)
x, y = card("Tool", "wrench", "Calculator · off (Sarvam API rejects tool messages)", 2, Y + CH + 40); tool = node("Calculator", "@n8n/n8n-nodes-langchain.toolCalculator", 1, {}, x, y, disabled=True)
link(ct, ag); link(ag, rc); link(lm, ag, kind="ai_languageModel"); link(tool, ag, kind="ai_tool")
Y += 2 * CH + 200

# ═════════ E · APPS (shown, not wired) ═════════
section("apps", Y); Y += 280
x, y = card("Sarvam AI", "mic", "speech, chat, 22 languages", 0, Y); node("Sarvam AI", "n8n-nodes-sarvam.sarvam", 1, {"resource": "speech", "operation": "textToSpeech", "ttsModel": "bulbul:v4-flash", "ttsSpeakerV4": "aarti_hi_customer", "ttsTargetLanguage": "hi-IN", "text": "नमस्ते! n8n वर्कशॉप में आपका स्वागत है।", "textToSpeechOptions": {}}, x, y)
x, y = card("Gmail", "gmail", "send, read, label", 1, Y); node("Gmail", "n8n-nodes-base.gmail", 2.1, {"sendTo": "someone@example.com", "subject": "Hello from n8n", "message": "Hi there", "options": {}}, x, y)
x, y = card("Google Sheets", "sheet", "append, read, update", 2, Y); node("Google Sheets", "n8n-nodes-base.googleSheets", 4.7, {"operation": "append", "documentId": {"__rl": True, "mode": "list", "value": ""}, "sheetName": {"__rl": True, "mode": "list", "value": ""}}, x, y)
x, y = card("Notion", "page", "pages and databases", 3, Y); node("Notion", "n8n-nodes-base.notion", 2.2, {"pageId": {"__rl": True, "mode": "url", "value": ""}, "options": {}}, x, y)
x, y = card("Telegram", "plane", "bot messages", 4, Y); node("Telegram", "n8n-nodes-base.telegram", 1.2, {"chatId": "123456789", "text": "Hello from n8n!", "additionalFields": {}}, x, y)
x, y = card("Slack", "hash", "channels and DMs", 5, Y); node("Slack", "n8n-nodes-base.slack", 2.4, {"select": "channel", "channelId": {"__rl": True, "mode": "name", "value": "general"}, "text": "Workflow complete!", "otherOptions": {}}, x, y)
x, y = card("Execute Workflow", "subflow", "run another workflow", 6, Y); node("Execute Workflow", "n8n-nodes-base.executeWorkflow", 1.2, {"options": {}}, x, y)
Y += CH + 160

# ═════════ F · HUMAN IN THE LOOP (shown, not wired) ═════════
section("human", Y); Y += 280
x, y = card("Respond to Webhook", "reply", "answer the caller", 0, Y); node("Respond to Webhook", "n8n-nodes-base.respondToWebhook", 1.4, {"options": {}}, x, y)
x, y = card("Gmail · wait", "mail-wait", "approve by email", 1, Y); node("Gmail: Send & Wait", "n8n-nodes-base.gmail", 2.1, {"operation": "sendAndWait", "sendTo": "approver@example.com", "subject": "Approve?", "message": "Please approve this action.", "options": {}}, x, y)
x, y = card("Slack · wait", "hash-wait", "approve with a button", 2, Y); node("Slack: Send & Wait", "n8n-nodes-base.slack", 2.4, {"operation": "sendAndWait", "select": "channel", "channelId": {"__rl": True, "mode": "name", "value": "approvals"}, "message": "Approve this?", "options": {}}, x, y)
x, y = card("Form page", "hand", "ask the user mid-flow", 3, Y); node("Form: Next Page", "n8n-nodes-base.form", 2.5, {"operation": "page", "formFields": {"values": [{"fieldLabel": "Approve?", "fieldName": "approve", "fieldType": "dropdown", "fieldOptions": {"values": [{"option": "Yes"}, {"option": "No"}]}}]}, "options": {}}, x, y, webhookId=nid())
Y += CH + 160

# ═════════ G · ADVANCED (runnable) ═════════
section("advanced", Y); Y += 280
s = runner(0, Y, "advanced")
x, y = card("Code", "code", "stats over all items", 2, Y); c1 = node("Code: Stats", "n8n-nodes-base.code", 2, {"jsCode": "const items = $input.all().map(i => i.json);\nconst scores = items.map(i => i.score);\nreturn [{ json: {\n  count: items.length,\n  average: Math.round(scores.reduce((a, b) => a + b, 0) / scores.length),\n  max: Math.max(...scores),\n  active: items.filter(i => i.isActive).length,\n} }];"}, x, y)
x, y = card("HTTP Request", "globe", "POST to any API", 3, Y); h1 = node("HTTP Request", "n8n-nodes-base.httpRequest", 4.2, {"method": "POST", "url": "https://httpbin.org/post", "sendBody": True, "specifyBody": "json", "jsonBody": "={{ JSON.stringify($json) }}", "options": {}}, x, y)
x, y = card("MCP Client", "plug", "tools from any MCP server", 4, Y); node("MCP Client", "@n8n/n8n-nodes-langchain.mcpClientTool", 1.1, {"endpointUrl": "https://example.com/mcp", "options": {}}, x, y)
link(s, c1); link(c1, h1)

# pictogram aliases used above
wf = {"name": "ABCs of n8n", "nodes": nodes, "connections": connections,
      "settings": {"executionOrder": "v1"}, "pinData": {}, "meta": {"templateCredsSetupCompleted": False}, "tags": []}
OUT.write_text(json.dumps(wf, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {OUT.relative_to(ROOT)}: {len(nodes)} nodes ({sum(1 for n in nodes if not n['type'].endswith('stickyNote'))} real)")

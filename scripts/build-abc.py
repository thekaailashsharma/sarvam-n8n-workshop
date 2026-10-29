#!/usr/bin/env python3
"""Generates workflow/abcs-of-n8n.json: a visual, runnable node reference. Original content by Abhay (abhay.co/go)."""
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

CW, CH, GAP = 240, 250, 270          # card width/height, column pitch
def section(key, y, color, tagline, h=130):
    sticky(f"Section: {key}", f"![{key}]({A}/{key}.gif)\n{tagline}", -240, y, 2560, h, color)
def card(name, pic, line, col, y, color=7, w=CW, h=CH):
    """A node card: pictogram + one line. The node itself is placed inside at (x+20, y+120)."""
    x = -240 + col * GAP
    sticky(f"Card: {name}", f"![{pic}]({A}/{pic}.png)\n**{name}** · {line}", x, y, w, h, color)
    return x + 20, y + 120

# ═══════════ HEADER ═══════════
sticky("Header", "# 📘 ABCs of n8n · every node, one canvas\nBased on Abhay's node reference (abhay.co/go) · remixed for the **Sarvam × n8n** workshop. "
       "Three chains are **runnable**: hit *Execute* on a Manual Trigger and watch data flow. Hover any node for its one-liner.", -240, -200, 2560, 120, 7)

# ═══════════ 1 · TRIGGERS ═══════════
Y = -40; section("triggers", Y, 7, "Nothing runs until one of these fires. All of them hand off to **Sample Data** below.")
Y += 150
x, y = card("Manual Trigger", "bolt", "click Execute", 0, Y); t_manual = node("Manual Trigger", "n8n-nodes-base.manualTrigger", 1, {}, x, y)
x, y = card("Schedule", "clock", "every hour", 1, Y); t_sched = node("Schedule Trigger", "n8n-nodes-base.scheduleTrigger", 1.3, {"rule": {"interval": [{"field": "hours"}]}}, x, y)
x, y = card("Webhook", "hook", "POST /abc-n8n", 2, Y); t_hook = node("Webhook Trigger", "n8n-nodes-base.webhook", 2.1, {"httpMethod": "POST", "path": "abc-n8n", "responseMode": "lastNode", "options": {}}, x, y, webhookId=nid())
x, y = card("Form", "form", "hosted web form", 3, Y); t_form = node("Form Trigger", "n8n-nodes-base.formTrigger", 2.5, {"formTitle": "Contact form", "formFields": {"values": [{"fieldLabel": "Name", "fieldName": "name", "requiredField": True}, {"fieldLabel": "Email", "fieldName": "email"}]}, "options": {}}, x, y, webhookId=nid())
x, y = card("Gmail Trigger", "mail", "new email arrives", 4, Y); node("Gmail Trigger", "n8n-nodes-base.gmailTrigger", 1.3, {"pollTimes": {"item": [{"mode": "everyMinute"}]}, "filters": {}}, x, y)
x, y = card("Sub-workflow", "loop", "called by another flow", 5, Y); node("Called by Another Workflow", "n8n-nodes-base.executeWorkflowTrigger", 1.1, {"inputSource": "passthrough"}, x, y)
x, y = card("Chat Trigger", "chat-trigger", "public chat UI", 6, Y); t_chat = node("Chat Trigger", "@n8n/n8n-nodes-langchain.chatTrigger", 1.3, {"public": True, "options": {}}, x, y, webhookId=nid())

# sample data hub
Y += CH + 30
sticky("Card: Sample Data", f"![code]({A}/code.png)\n**Sample Data** · 4 people with scores and tags. Every runnable chain starts here.", -240, Y, 520, 160, 1)
hub = node("Sample Data", "n8n-nodes-base.code", 2, {"jsCode": "return [\n  { json: { name: 'Priya',  score: 92, isActive: true,  tags: ['n8n', 'ai'] } },\n  { json: { name: 'Arjun',  score: 67, isActive: true,  tags: ['automation'] } },\n  { json: { name: 'Neha',   score: 48, isActive: false, tags: ['design', 'ux'] } },\n  { json: { name: 'Kabir',  score: 88, isActive: true,  tags: ['backend'] } },\n];"}, -220, Y + 50)
for t in (t_manual, t_sched, t_hook, t_form): link(t, hub)

# ═══════════ 2 · DATA MANIPULATION (runnable) ═══════════
Y += 200; section("data", Y, 5, "Reshape, filter, split and collect. **Runnable:** Execute → open each node to see items change.")
Y += 150
x, y = card("Edit Fields", "pencil", "add greeting + level", 0, Y, 5); d1 = node("Edit Fields", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [{"id": nid(), "name": "greeting", "value": "=Hello {{ $json.name }}!", "type": "string"}, {"id": nid(), "name": "level", "value": "={{ $json.score >= 80 ? 'gold' : 'silver' }}", "type": "string"}]}, "includeOtherFields": True, "options": {}}, x, y)
x, y = card("Date & Time", "cal", "stamp today", 1, Y, 5); d2 = node("Date & Time", "n8n-nodes-base.dateTime", 2, {"operation": "formatDate", "date": "={{ $now }}", "format": "yyyy-MM-dd", "outputFieldName": "today", "options": {"includeInputFields": True}}, x, y)
x, y = card("Filter", "funnel", "keep score ≥ 50", 2, Y, 5); d3 = node("Filter", "n8n-nodes-base.filter", 2.2, {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2}, "conditions": [{"id": nid(), "leftValue": "={{ $json.score }}", "rightValue": 50, "operator": {"type": "number", "operation": "gte"}}], "combinator": "and"}, "options": {}}, x, y)
x, y = card("Split Out", "scissors", "one item per tag", 3, Y, 5); d4 = node("Split Out", "n8n-nodes-base.splitOut", 1, {"fieldToSplitOut": "tags", "include": "allOtherFields", "options": {}}, x, y)
x, y = card("Aggregate", "box", "collect tags back", 4, Y, 5); d5 = node("Aggregate", "n8n-nodes-base.aggregate", 1, {"aggregate": "aggregateIndividualFields", "fieldsToAggregate": {"fieldToAggregate": [{"fieldToAggregate": "tags"}]}, "options": {}}, x, y)
for a, b in [(hub, d1), (d1, d2), (d2, d3), (d3, d4), (d4, d5)]: link(a, b)

# ═══════════ 3 · FLOW CONTROL (runnable) ═══════════
Y += CH + 60; section("flow", Y, 6, "Branch, merge, loop. **Runnable:** Priya and Kabir go the TRUE way, the rest FALSE, then 2 per batch.")
Y += 150
x, y = card("IF", "fork", "score ≥ 80 ?", 0, Y, 6); f1 = node("IF Condition", "n8n-nodes-base.if", 2.4, {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 4}, "conditions": [{"id": nid(), "leftValue": "={{ $json.score }}", "rightValue": 80, "operator": {"type": "number", "operation": "gte"}}], "combinator": "and"}, "options": {}}, x, y)
x, y = card("TRUE / FALSE", "pencil", "tag the grade", 1, Y, 6)
f2 = node("TRUE — Grade A", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [{"id": nid(), "name": "grade", "value": "A ✅", "type": "string"}]}, "includeOtherFields": True, "options": {}}, x, y - 40)
f3 = node("FALSE — Grade B", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [{"id": nid(), "name": "grade", "value": "B ⚠️", "type": "string"}]}, "includeOtherFields": True, "options": {}}, x, y + 60)
x, y = card("Merge", "merge", "branches → one stream", 2, Y, 6); f4 = node("Merge (Append)", "n8n-nodes-base.merge", 3.2, {"mode": "append", "numberInputs": 2}, x, y)
x, y = card("Loop Over Items", "cycle", "2 per batch", 3, Y, 6); f5 = node("Loop Over Items", "n8n-nodes-base.splitInBatches", 3, {"batchSize": 2, "options": {}}, x, y)
x, y = card("Batch / Done", "box", "process, then finish", 4, Y, 6)
f6 = node("Process Batch", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [{"id": nid(), "name": "batchDone", "value": True, "type": "boolean"}]}, "includeOtherFields": True, "options": {}}, x, y + 60)
f7 = node("All Batches Done", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [{"id": nid(), "name": "summary", "value": "=All {{ $input.all().length }} items processed", "type": "string"}]}, "options": {}}, x, y - 40)
link(hub, f1); link(f1, f2, 0); link(f1, f3, 1); link(f2, f4, idx=0); link(f3, f4, idx=1); link(f4, f5); link(f5, f7, 0); link(f5, f6, 1); link(f6, f5)

# ═══════════ 4 · AI AGENT (runnable on Sarvam) ═══════════
Y += CH + 60; section("ai", Y, 3, "An LLM that reasons and calls tools. **Runnable on Sarvam-105B:** open Chat Trigger → *Open chat* → ask anything in Hindi, Hinglish or English.")
Y += 150
x, y = card("AI Agent", "brain", "reasons, picks tools", 1, Y, 3); ag = node("AI Agent", "@n8n/n8n-nodes-langchain.agent", 3.1, {"options": {"systemMessage": "You are a concise, friendly assistant for an n8n workshop in India. Use the Calculator tool for any arithmetic. Reply in the language the user writes in."}}, x, y)
x, y = card("Language Model", "chip", "Sarvam-105B, OpenAI-compatible", 2, Y + 160, 3); lm = node("Sarvam-105B", "@n8n/n8n-nodes-langchain.lmChatOpenAi", 1.2, {"model": {"__rl": True, "mode": "id", "value": "sarvam-105b-conversations"}, "options": {"temperature": 0.2, "maxTokens": 1024}}, x, y)
x, y = card("Tool", "wrench", "Calculator · off: Sarvam's API rejects tool messages, enable with an OpenAI/Gemini model", 3, Y + 160, 3); tool = node("Calculator", "@n8n/n8n-nodes-langchain.toolCalculator", 1, {}, x, y, disabled=True)
x, y = card("Respond to Chat", "chat", "reply in the chat UI", 2, Y, 3); rc = node("Respond to Chat", "@n8n/n8n-nodes-langchain.chat", 1.3, {"message": "={{ $json.output }}", "options": {}}, x, y)
link(t_chat, ag); link(ag, rc); link(lm, ag, kind="ai_languageModel"); link(tool, ag, kind="ai_tool")

# ═══════════ 5 · APP INTEGRATIONS ═══════════
Y += CH + 220; section("apps", Y, 4, "Hundreds of apps, auth handled by n8n. These are illustrative: connect a credential and they work.")
Y += 150
x, y = card("Sarvam AI", "mic", "speech ↔ text, chat, 22 languages", 0, Y, 4); node("Sarvam AI", "n8n-nodes-sarvam.sarvam", 1, {"resource": "speech", "operation": "textToSpeech", "ttsModel": "bulbul:v4-flash", "ttsSpeakerV4": "aarti_hi_customer", "ttsTargetLanguage": "hi-IN", "text": "नमस्ते! n8n वर्कशॉप में आपका स्वागत है।", "textToSpeechOptions": {}}, x, y)
x, y = card("Gmail", "gmail", "send, read, label", 1, Y, 4); node("Gmail — Send Email", "n8n-nodes-base.gmail", 2.1, {"sendTo": "someone@example.com", "subject": "Hello from n8n", "message": "=Hi {{ $json.name }}", "options": {}}, x, y)
x, y = card("Google Sheets", "sheet", "append, read, update", 2, Y, 4); node("Google Sheets — Append", "n8n-nodes-base.googleSheets", 4.7, {"operation": "append", "documentId": {"__rl": True, "mode": "list", "value": ""}, "sheetName": {"__rl": True, "mode": "list", "value": ""}}, x, y)
x, y = card("Notion", "page", "pages & databases", 3, Y, 4); node("Notion — Create Page", "n8n-nodes-base.notion", 2.2, {"pageId": {"__rl": True, "mode": "url", "value": ""}, "options": {}}, x, y)
x, y = card("Telegram", "plane", "bot messages", 4, Y, 4); node("Telegram — Send Message", "n8n-nodes-base.telegram", 1.2, {"chatId": "123456789", "text": "Hello from n8n!", "additionalFields": {}}, x, y)
x, y = card("Slack", "hash", "channels & DMs", 5, Y, 4); node("Slack — Post Message", "n8n-nodes-base.slack", 2.4, {"select": "channel", "channelId": {"__rl": True, "mode": "name", "value": "general"}, "text": "Workflow complete!", "otherOptions": {}}, x, y)
x, y = card("Execute Workflow", "subflow", "run another flow", 6, Y, 4); node("Execute Sub-Workflow", "n8n-nodes-base.executeWorkflow", 1.2, {"options": {}}, x, y)

# ═══════════ 6 · HUMAN IN THE LOOP ═══════════
Y += CH + 60; section("human", Y, 2, "Pause until a person answers. Essential for AI approval flows.")
Y += 150
x, y = card("Respond to Webhook", "reply", "answer the caller", 0, Y, 2); node("Respond to Webhook", "n8n-nodes-base.respondToWebhook", 1.4, {"options": {}}, x, y)
x, y = card("Gmail · Send & Wait", "mail-wait", "approve by email", 1, Y, 2); node("Gmail — Send & Wait", "n8n-nodes-base.gmail", 2.1, {"operation": "sendAndWait", "sendTo": "approver@example.com", "subject": "Approve?", "message": "Please approve this action.", "options": {}}, x, y)
x, y = card("Slack · Send & Wait", "hash-wait", "approve by button", 2, Y, 2); node("Slack — Send & Wait", "n8n-nodes-base.slack", 2.4, {"operation": "sendAndWait", "select": "channel", "channelId": {"__rl": True, "mode": "name", "value": "approvals"}, "message": "Approve this?", "options": {}}, x, y)
x, y = card("Form · next page", "hand", "ask the user mid-flow", 3, Y, 2); node("Form — Next Page", "n8n-nodes-base.form", 2.5, {"operation": "page", "formFields": {"values": [{"fieldLabel": "Approve?", "fieldName": "approve", "fieldType": "dropdown", "fieldOptions": {"values": [{"option": "Yes"}, {"option": "No"}]}}]}, "options": {}}, x, y, webhookId=nid())

# ═══════════ 7 · ADVANCED (runnable) ═══════════
Y += CH + 60; section("advanced", Y, 7, "Power patterns. **Runnable:** Code computes stats over all items in one go.")
Y += 150
x, y = card("Code", "code", "stats over all items", 0, Y); c1 = node("Code — Aggregate Stats", "n8n-nodes-base.code", 2, {"jsCode": "const items = $input.all().map(i => i.json);\nconst scores = items.map(i => i.score);\nreturn [{ json: {\n  count: items.length,\n  average: Math.round(scores.reduce((a, b) => a + b, 0) / scores.length),\n  max: Math.max(...scores),\n  active: items.filter(i => i.isActive).length,\n} }];"}, x, y)
x, y = card("HTTP Request", "globe", "call any API", 1, Y); node("HTTP POST to API", "n8n-nodes-base.httpRequest", 4.2, {"method": "POST", "url": "https://httpbin.org/post", "sendBody": True, "specifyBody": "json", "jsonBody": "={{ JSON.stringify($json) }}", "options": {}}, x, y)
x, y = card("MCP Client", "plug", "tools from any MCP server", 2, Y); node("MCP Client", "@n8n/n8n-nodes-langchain.mcpClientTool", 1.1, {"endpointUrl": "https://example.com/mcp", "options": {}}, x, y)
link(hub, c1); link(c1, "HTTP POST to API")

wf = {"name": "ABCs of n8n — Nodes (visual, runnable)", "nodes": nodes, "connections": connections,
      "settings": {"executionOrder": "v1"}, "pinData": {}, "meta": {"templateCredsSetupCompleted": False}, "tags": []}
OUT.write_text(json.dumps(wf, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {OUT.relative_to(ROOT)}: {len(nodes)} nodes ({sum(1 for n in nodes if not n['type'].endswith('stickyNote'))} real)")

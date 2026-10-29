#!/usr/bin/env python3
"""End-to-end test with real API calls, no browser: builds a headless copy of the workflow
(Manual Trigger + Read File instead of the form, no form-ending nodes), imports it into the
running container, executes it and prints every node's status. Usage: npm run e2e [-- samples/x.wav]"""
import json, os, pathlib, subprocess, sys, tempfile, uuid
ROOT = pathlib.Path(__file__).resolve().parent.parent
SAMPLE = "/samples/" + pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "samples/standup-hinglish.wav").name
WF_ID = "HeadlessTestWf0001"
NEEDS = {"n8n-nodes-sarvam.sarvam": "sarvamApi", "n8n-nodes-base.github": "githubApi",
         "n8n-nodes-base.googleSheets": "googleSheetsOAuth2Api", "@n8n/n8n-nodes-langchain.lmChatOpenAi": "openAiApi"}
def dx(*args, **kw): return subprocess.run(["docker", "exec", *args], capture_output=True, text=True, **kw)

creds = json.loads(dx("sarvam-n8n", "n8n", "export:credentials", "--all").stdout)
by_type = {}
for c in creds: by_type.setdefault(c["type"], {"id": c["id"], "name": c["name"]})

wf = json.loads((ROOT / "workflow" / "meeting-to-tickets.json").read_text())
drop = {"Show Results", "Couldn't Hear"}
skip = lambda n: n in drop or n.startswith(("Try:", "▶", "Sticky"))
wf["nodes"] = [n for n in wf["nodes"] if not skip(n["name"])]
for n in wf["nodes"]:
    if n["name"] == "Upload Recording":
        n.update({"type": "n8n-nodes-base.readWriteFile", "typeVersion": 1,
                  "parameters": {"fileSelector": SAMPLE, "options": {"dataPropertyName": "recording"}}})
        n.pop("webhookId", None)
    t = NEEDS.get(n["type"])
    if t and t in by_type: n["credentials"] = {t: by_type[t]}
wf = json.loads(json.dumps(wf).replace("$('Upload Recording').item.json.meeting_title || 'untitled'", "'e2e test run'"))
wf["nodes"].append({"parameters": {}, "id": str(uuid.uuid4()), "name": "Start", "type": "n8n-nodes-base.manualTrigger", "typeVersion": 1, "position": [-300, 300]})
conns = {k: v for k, v in wf["connections"].items() if not skip(k)}
for v in conns.values():
    for kind in v: v[kind] = [[c for c in branch if c["node"] not in drop] for branch in v[kind]]
conns["Start"] = {"main": [[{"node": "Upload Recording", "type": "main", "index": 0}]]}
wf.update({"connections": conns, "name": "Meeting → Tickets · HEADLESS TEST", "id": WF_ID})

with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f: json.dump(wf, f); tmp = f.name
os.chmod(tmp, 0o644)
subprocess.run(["docker", "cp", tmp, "sarvam-n8n:/tmp/wf-e2e.json"], check=True)
assert "Successfully" in dx("sarvam-n8n", "n8n", "import:workflow", "--input=/tmp/wf-e2e.json").stdout
print(f"▶ executing {wf['name']} on {SAMPLE} (real API calls)…")
r = dx("-e", "N8N_RUNNERS_BROKER_PORT=5680", "sarvam-n8n", "n8n", "execute", f"--id={WF_ID}", "--rawOutput")
raw = r.stdout; i = raw.find("{")
d, _ = json.JSONDecoder().raw_decode(raw[i:]) if i >= 0 else ({}, 0)
res = d.get("data", {}).get("resultData", {})
err = res.get("error") or d.get("error")
if not res.get("runData"):
    print("✖ no node results returned by the CLI\n", (json.dumps(d.get("error"), ensure_ascii=False)[:1500] if d.get("error") else raw[-1500:]))
    sys.exit(1)
for name, runs in res.get("runData", {}).items():
    for run in runs:
        mains = run.get("data", {}).get("main") or []
        counts = [len(b) if b else 0 for b in mains]
        status = run.get("executionStatus", "?")
        print(f"  {'✔' if status == 'success' else '✖'} {name:26} items/output={counts}")
        if name == "Sarvam: Transcribe" and mains and mains[0]:
            j = mains[0][0]["json"]; print(f"      lang={j.get('language_code')} · {j.get('transcript', '')[:140]}…")
        if name == "Summarize Meeting" and mains and mains[0]:
            print("      " + str(mains[0][0]["json"].get("output", {}).get("text", ""))[:300].replace("\n", "\n      "))
        if name == "One Item per Action" and mains and mains[0]:
            for it in mains[0]: print(f"      · {it['json'].get('priority')} {it['json'].get('title')}  [{it['json'].get('owner') or '—'}]")
        if name.startswith("GitHub") and mains and mains[0]:
            for it in mains[0]: print(f"      → {it['json'].get('html_url')}")
if err:
    print(f"\n✖ FAILED at {err.get('node', {}).get('name')}: {err.get('message')}\n   {str(err.get('description'))[:500]}")
    sys.exit(1)
print("\n✔ end-to-end run succeeded")

#!/usr/bin/env python3
"""Imports workflow/meeting-to-tickets.json into the running container, attaching credentials by type
(so nodes come up ready) and keeping a stable workflow id. Usage: npm run import"""
import json, pathlib, subprocess, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
WF_ID = "cto0htST9qyowFcF"
creds = json.loads(subprocess.check_output(["docker", "exec", "sarvam-n8n", "n8n", "export:credentials", "--all"], stderr=subprocess.DEVNULL))
by_type = {}
for c in creds: by_type.setdefault(c["type"], {"id": c["id"], "name": c["name"]})
NEEDS = {"n8n-nodes-sarvam.sarvam": "sarvamApi", "n8n-nodes-base.github": "githubApi",
         "n8n-nodes-base.googleSheets": "googleSheetsOAuth2Api", "@n8n/n8n-nodes-langchain.lmChatOpenAi": "openAiApi"}
wf = json.loads((ROOT / "workflow" / "meeting-to-tickets.json").read_text())
wf["id"] = WF_ID
attached = 0
for n in wf["nodes"]:
    t = NEEDS.get(n["type"])
    if t and t in by_type:
        n["credentials"] = {t: by_type[t]}; attached += 1
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump(wf, f); tmp = f.name
import os; os.chmod(tmp, 0o644)  # docker cp keeps the mode; the n8n user must be able to read it
subprocess.run(["docker", "cp", tmp, "sarvam-n8n:/tmp/wf.json"], check=True)
out = subprocess.run(["docker", "exec", "sarvam-n8n", "n8n", "import:workflow", "--input=/tmp/wf.json"], capture_output=True, text=True)
print(f"attached credentials to {attached} nodes ·", [l for l in out.stdout.splitlines() if "import" in l.lower()][-1])

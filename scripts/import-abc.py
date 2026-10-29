#!/usr/bin/env python3
"""Imports workflow/abcs-of-n8n.json into the running container (stable id, credentials attached by type)."""
import json, os, pathlib, subprocess, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
WF_ID = os.environ.get("ABC_WF_ID", "NspES53w6oBlbIHT")
NEEDS = {"n8n-nodes-sarvam.sarvam": "sarvamApi", "@n8n/n8n-nodes-langchain.lmChatOpenAi": "openAiApi", "n8n-nodes-base.googleSheets": "googleSheetsOAuth2Api"}
creds = json.loads(subprocess.check_output(["docker", "exec", "sarvam-n8n", "n8n", "export:credentials", "--all"], stderr=subprocess.DEVNULL))
by = {}
for c in creds: by.setdefault(c["type"], {"id": c["id"], "name": c["name"]})
wf = json.loads((ROOT / "workflow" / "abcs-of-n8n.json").read_text()); wf["id"] = WF_ID
n = 0
for node in wf["nodes"]:
    t = NEEDS.get(node["type"])
    if t and t in by: node["credentials"] = {t: by[t]}; n += 1
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f: json.dump(wf, f); tmp = f.name
os.chmod(tmp, 0o644)
subprocess.run(["docker", "cp", tmp, "sarvam-n8n:/tmp/abc.json"], check=True)
out = subprocess.run(["docker", "exec", "sarvam-n8n", "n8n", "import:workflow", "--input=/tmp/abc.json"], capture_output=True, text=True).stdout
print(f"credentials on {n} nodes ·", [l for l in out.splitlines() if "import" in l.lower()][-1])

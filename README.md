# Meeting → Tickets (Sarvam AI × n8n)

Upload a meeting recording or voice note in **any Indian language**. Sarvam transcribes it, Sarvam-105B
summarises it and pulls out every action item, n8n classifies each one and sends it where it belongs:
**bugs and features become GitHub issues, tasks, decisions and follow-ups land in a Google Sheet**.
Every class is a branch, so swapping in Jira, Linear, Trello or Notion is one node.

```
Upload → Sarvam STT (Saaras v4, → English) → guard → Summarization Chain → Information Extractor
       → Split Out → Text Classifier ─┬─ bug / feature → GitHub issue ─┐
                                      ├─ task → Jira (disabled) + sheet │→ Google Sheet row → results page
                                      └─ decision / follow-up → sheet ─┘
```

All three n8n AI nodes run on **Sarvam-105B** through the OpenAI-compatible chat model node.

## 1. Run n8n

```bash
docker compose up -d        # http://localhost:5678
```

## 2. Install the Sarvam node

Settings → Community Nodes → Install → `n8n-nodes-sarvam`.

## 3. Import

Workflows → Import from file → `workflow/meeting-to-tickets.json` (or `npm run import` with the container running).

## 4. Credentials

| Credential in n8n | Used by | Get it |
|---|---|---|
| **Sarvam AI API** | Sarvam: Transcribe, warm-up nodes | https://dashboard.sarvam.ai → API keys |
| **OpenAI** (Base URL `https://api.sarvam.ai/v1`, API key = the same Sarvam key) | Sarvam-105B model node | same key |
| **GitHub** (access token, `repo` scope) | GitHub: Bug Issue, GitHub: Feature Issue | https://github.com/settings/tokens/new?description=n8n-workshop&scopes=repo |
| **Google Sheets OAuth2** | Log to Sheet | https://docs.n8n.io/integrations/builtin/credentials/google/oauth-single-service/ |

Create them at http://localhost:5678/home/credentials, then pick them on the nodes with a red border.

## 5. Config node

`githubOwner`, `githubRepo`, `sheetId`. Defaults point at this repo and the workshop sheet.

## 6. Try it

| Sample | What to expect |
|---|---|
| `samples/standup-english.wav` | 5 items: 2 bugs → GitHub, 1 feature → GitHub, 1 task, 1 decision, 1 follow-up → sheet |
| `samples/standup-hindi.wav` | Hindi stand-up, same flow, `language_code = hi-IN` |
| `samples/voice-note-bug-report.wav` | one bug → one GitHub issue |

Warm-up row on the canvas: three single-node demos (Hear / Think / Speak) that need only the Sarvam credential.

## Developing

```bash
npm test          # structural tests on the workflow JSON
npm run build     # regenerate hero GIF + icons and the workflow JSON
npm run samples   # regenerate sample recordings (macOS `say`)
npm run import    # push the JSON into the running container
```

Sticky-note images are served from `/static/workshop` (mounted by compose). To ship a standalone JSON:
`ASSET_BASE=https://raw.githubusercontent.com/<owner>/<repo>/main/assets npm run build`.

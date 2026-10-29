#!/usr/bin/env bash
# Generates sample recordings with macOS text-to-speech so the workflow can be tested
# without a real meeting. Output: samples/*.wav (16 kHz mono PCM).
# Keep every clip under 30 s: Sarvam's real-time STT endpoint rejects longer audio (use the Batch API for those).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p samples
rm -f samples/*.wav

gen() { # gen <voice> <outfile> <text>
  local voice="$1" out="$2" text="$3" tmp
  tmp="$(mktemp -t vn).aiff"
  say -v "$voice" -r 195 -o "$tmp" "$text"
  afconvert -f WAVE -d LEI16@16000 -c 1 "$tmp" "samples/$out"
  rm -f "$tmp"
  echo "wrote samples/$out"
}

gen Rishi standup-english.wav \
  "Quick sync on the payments app. One, the checkout page crashes on Android when UPI is selected, that blocks Friday's release, Arjun takes it today. Two, design wants a dark mode toggle in settings, Neha writes the spec for next sprint. Three, we decided to move the database backup window to two a.m. Four, I still need the vendor contract from legal, I will chase them tomorrow. Five, add rate limiting to the OTP endpoint before launch, Kabir owns it."

gen Lekha standup-hindi.wav \
  "ठीक है, आज की मीटिंग के पॉइंट्स। पहला, लॉगिन पेज पर ओटीपी दो बार आ रहा है, यह एक बग है और अर्जुन इसे आज ठीक करेगा। दूसरा, ग्राहकों ने हिंदी में इनवॉइस डाउनलोड करने की सुविधा मांगी है, नेहा अगले स्प्रिंट में इसका डिज़ाइन बनाएगी। तीसरा, हमने तय किया है कि सपोर्ट का समय सुबह नौ से रात नौ बजे तक रहेगा। चौथा, राहुल बुधवार तक नया सर्वर सेटअप पूरा करेगा। बस इतना ही।"

gen Aman voice-note-bug-report.wav \
  "Hey team, Arjun here. The export to CSV button on the reports page does nothing when the date range is more than ninety days. No error, just nothing. Can someone look at it this week, a customer asked twice."

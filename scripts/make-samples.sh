#!/usr/bin/env bash
# Generates sample recordings with macOS text-to-speech so the workflow can be tested
# without a real meeting. Output: samples/*.wav (16 kHz mono PCM).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p samples
rm -f samples/*.wav

gen() { # gen <voice> <outfile> <text>
  local voice="$1" out="$2" text="$3" tmp
  tmp="$(mktemp -t vn).aiff"
  say -v "$voice" -r 185 -o "$tmp" "$text"
  afconvert -f WAVE -d LEI16@16000 -c 1 "$tmp" "samples/$out"
  rm -f "$tmp"
  echo "wrote samples/$out"
}

gen Rishi standup-english.wav \
  "Okay, quick sync on the payments app. First, Priya found that the checkout page crashes on Android when the UPI option is selected, it is happening for about five percent of users, that is a blocker for the Friday release. Arjun, can you take that today. Second, the design team wants a dark mode toggle in settings, Neha will write the spec and we will put it into next sprint. Third, we decided to move the production database backup window to two a.m. India time, Rahul will update the runbook by Wednesday. Fourth, I still need the vendor contract from legal, I will follow up with them tomorrow. And finally, let us add rate limiting to the OTP endpoint before launch, that is a must have, Kabir owns it. That is all."

gen Lekha standup-hindi.wav \
  "ठीक है, आज की मीटिंग के पॉइंट्स। पहला, लॉगिन पेज पर ओटीपी दो बार आ रहा है, यह एक बग है और अर्जुन इसे आज ठीक करेगा। दूसरा, ग्राहकों ने हिंदी में इनवॉइस डाउनलोड करने की सुविधा मांगी है, नेहा अगले स्प्रिंट में इसका डिज़ाइन बनाएगी। तीसरा, हमने तय किया है कि सपोर्ट का समय सुबह नौ से रात नौ बजे तक रहेगा। चौथा, राहुल बुधवार तक नया सर्वर सेटअप पूरा करेगा। बस इतना ही।"

gen Aman voice-note-bug-report.wav \
  "Hey team, Arjun here. The export to CSV button on the reports page does nothing when the date range is more than ninety days. No error, just nothing. Can someone look at it this week, a customer asked twice."

#!/usr/bin/env python3
"""Generates samples/standup-hinglish.wav with Sarvam Bulbul v4-flash: a code-mixed Hindi/English
stand-up, the showcase recording for the workshop. Needs SARVAM_API_KEY. Keep it under 30 s."""
import base64, json, os, pathlib, sys, urllib.request
KEY = os.environ.get("SARVAM_API_KEY") or sys.exit("set SARVAM_API_KEY")
OUT = pathlib.Path(__file__).resolve().parent.parent / "samples" / "standup-hinglish.wav"
TEXT = ("ठीक है team, quick payments stand-up. पहला: checkout page Android पे UPI select करते ही crash हो रहा है, "
        "Friday release block है, Arjun आज fix करेगा। दूसरा: customers Hindi में invoice download चाहते हैं, "
        "Neha next sprint में design बनाएगी। तीसरा: हमने decide किया है कि support timing सुबह नौ से रात नौ रहेगी। "
        "चौथा: legal से vendor contract अभी तक नहीं आया, मैं कल follow-up करूँगा। "
        "और last, OTP endpoint पे rate limiting launch से पहले चाहिए, Kabir owner है।")
body = {"model": "bulbul:v4-flash", "text": TEXT, "language_code": "hi-IN", "speaker": "aditya_hi_conversational",
        "pace": 1.15, "output_audio_codec": "wav", "speech_sample_rate": 16000}
req = urllib.request.Request("https://api.sarvam.ai/text-to-speech", data=json.dumps(body).encode(),
                             headers={"api-subscription-key": KEY, "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=120) as r: resp = json.load(r)
OUT.write_bytes(base64.b64decode(resp["audios"][0]))
print(f"wrote {OUT.relative_to(OUT.parent.parent)} ({OUT.stat().st_size // 1024} KB)")

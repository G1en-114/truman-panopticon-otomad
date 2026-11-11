import whisper, sys, json
m = whisper.load_model("turbo", device="cuda")
for p in sys.argv[1:]:
    r = m.transcribe(p, language="en", word_timestamps=False, condition_on_previous_text=False, verbose=None)
    print('==',p)
    for s in r['segments']: print(f"{s['start']:6.1f} {s['text'].strip()}")

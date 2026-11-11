import whisper, json, sys
m = whisper.load_model("turbo", device="cuda")
r = m.transcribe(sys.argv[1], language="en", word_timestamps=True, condition_on_previous_text=False, verbose=False)
json.dump(r, open(sys.argv[2], "w"), ensure_ascii=False)
print(len(r["segments"]), "segments")

from faster_whisper import WhisperModel

model = WhisperModel(
    "./whisper-large-v3-ct2",
    device="cuda",
    compute_type="float16"
)

segments, info = model.transcribe(
    "recording.mpeg",
    language="ta",
    vad_filter=True,
    beam_size=5
)

for segment in segments:
    print(segment.text)
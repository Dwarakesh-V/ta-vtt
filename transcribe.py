import whisperx
import gc
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
audio_file = "rec2.mpeg" 

model = whisperx.load_model(
    "./whisper-large-v2",
    device, 
    compute_type="float16", 
    language="ta",
    vad_options={
        "vad_onset": 0.800,
        "vad_offset": 0.363
    }
)

result = model.transcribe(
    audio_file, 
    batch_size=8,
    language="ta",
    chunk_size=5,
)

del model
gc.collect()
torch.cuda.empty_cache()

for seg in result["segments"]:
    text = seg.get("text", "").strip()
    if text:
        print(text)
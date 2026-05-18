import whisperx
import gc
import torch

device = "cuda"
audio_file = "rec2.mpeg" 

print("Loading Whisper model...")
model = whisperx.load_model(
    "./whisper-large-v2",
    device, 
    compute_type="float16", 
    language="ta",
    vad_options={
        "vad_onset": 0.400,
        "vad_offset": 0.363
    }
)

print("Transcribing...")
result = model.transcribe(
    audio_file, 
    batch_size=8,
    language="ta",
    chunk_size=5,
)

del model
gc.collect()
torch.cuda.empty_cache()

print("Loading alignment model...")
model_a, metadata = whisperx.load_align_model(
    language_code="ta", 
    device=device,
    model_name="./wav2vec2-large-xlsr-53-tamil"
)

print("Aligning timestamps...")
result = whisperx.align(
    result["segments"], 
    model_a, 
    metadata, 
    audio_file, 
    device, 
    return_char_alignments=False
)

del model_a
gc.collect()
torch.cuda.empty_cache()

print("Outputting text...")
# Print line by line based on the aligned segments
for seg in result["segments"]:
    text = seg.get("text", "").strip()
    if text:
        print(text)
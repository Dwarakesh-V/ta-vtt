import whisperx
import gc
import torch
import pandas as pd
from pyannote.audio import Pipeline
import os
from dotenv import load_dotenv

load_dotenv()

hf_token = os.getenv("hf_token")

device = "cuda"
audio_file = "rec2.mpeg" 

print("Loading Whisper model...")
model = whisperx.load_model(
    "large-v2", 
    device, 
    compute_type="float16", 
    language="ta",
    vad_options={
        "vad_onset": 0.500,    # Make it harder to trigger speech detection (ignores background noise)
        "vad_offset": 0.363    # Default offset
    }
)

print("Transcribing...")
result = model.transcribe(
    audio_file, 
    batch_size=8,
    language="ta",
    chunk_size=5, # Smaller chunks prevent the model from drifting out of context
)
# print("Transcribing...")
# result = model.transcribe(
#     audio_file, 
#     batch_size=8,
#     chunk_size=10, # Smaller chunks prevent the model from drifting out of context
#     language="ta",
#     print_progress=True
# )

# Free GPU memory before loading the next models
del model
gc.collect()
torch.cuda.empty_cache()

# This forces the text to align perfectly with the audio at the word level.
print("Loading alignment model...")
model_a, metadata = whisperx.load_align_model(
    language_code="ta", 
    device=device,
    model_name="Amrrs/wav2vec2-large-xlsr-53-tamil" 
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

# Free GPU memory again
del model_a
gc.collect()
torch.cuda.empty_cache()

print("Loading local Pyannote model...")
pipeline = Pipeline.from_pretrained(
    "./speaker-diarization-3.1",
    token=hf_token
)
pipeline.to(torch.device(device))

print("Diarizing...")
# Providing min/max speakers still works natively with Pyannote and drastically improves accuracy
diarization = pipeline(audio_file, min_speakers=2, max_speakers=5)

# Convert Pyannote's 'Annotation' object into a Pandas DataFrame
# This is the exact format WhisperX expects internally
# Extract the actual Annotation object from the new DiarizeOutput wrapper
annotation = diarization.speaker_diarization

diarize_data = []
for turn, track, speaker in annotation.itertracks(yield_label=True):
    diarize_data.append({
        "start": turn.start,
        "end": turn.end,
        "speaker": speaker
    })

diarize_df = pd.DataFrame(diarize_data)


print("Assigning speakers to words...")
result = whisperx.assign_word_speakers(diarize_df, result)

for seg in result["segments"]:
    speaker = seg.get("speaker", "UNKNOWN")
    text = seg.get("text", "").strip()
    
    if text:
        print(f"[{speaker}] {text}")
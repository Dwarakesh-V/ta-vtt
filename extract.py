import whisperx
import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

device = "cuda"

audio_file = "recording2.wav"

model = whisperx.load_model(
    "./whisper-large-v3",
    device,
    compute_type="float16",
    language="ta"
)

audio = whisperx.load_audio(audio_file)

result = model.transcribe(
    audio,
    batch_size=8
)

for seg in result["segments"]:
    print(seg["text"])
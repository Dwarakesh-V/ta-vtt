def transcribe(model,audio_file):
    result = model.transcribe(
        audio_file, 
        batch_size=4,
        language="ta",
        chunk_size=20,
    )

    transcription = ""
    for seg in result["segments"]:
        text = seg.get("text", "").strip()
        transcription+=f"{text}\n"
    return transcription
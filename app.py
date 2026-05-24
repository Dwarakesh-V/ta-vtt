# Custom
from transcribe import transcribe
from generate import generate_llm_out
from call_record import make_call, is_call_connecting, is_call_active, end_call, play_audio, copy_recording, RecordingNotFound
from write_to_csv import process_phone_csv

# Libraries
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import whisperx
import torch
import pandas as pd
import time
from random import randint

# Audio transcription
transcribe_model = whisperx.load_model(
    "./whisper-large-v2",
    device="auto", 
    compute_type="float16", 
    language="ta",
    vad_options={
        "vad_onset": 0.800,
        "vad_offset": 0.363
    }
)

# Text model
language_model_name = "./Qwen3-8B"

# 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

language_tokenizer = AutoTokenizer.from_pretrained(language_model_name)

language_model = AutoModelForCausalLM.from_pretrained(
    language_model_name,
    quantization_config=bnb_config,
    device_map="auto",
    attn_implementation="flash_attention_2",
)

numbers = list(pd.read_excel("numbers.xlsx")["phone"])

with open("sys_prompt.txt") as f:
    system_prompt = f.read()

for number in numbers:
    make_call(number)
    initmsg = False
    for i in range(60):
        if is_call_connecting() or is_call_active(): # If call isnt active, break out
            time.sleep(1)
            if is_call_active() and not initmsg:
                play_audio("init_message.mp3")
                initmsg = True
        else:
            break
    end_call()
    time.sleep(5) # Wait for write complete

    try:
        path = copy_recording(number)
        time.sleep(2) # Copy wait

        call_vc = transcribe(path)
        content = generate_llm_out(language_model,language_tokenizer,system_prompt,call_vc)
        process_phone_csv(number,content)
        
    except RecordingNotFound:
        pass
    
    time.sleep(randint(10,20))


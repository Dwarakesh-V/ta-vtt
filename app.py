# Custom
from transcribe import transcribe
from generate import generate_llm_out
from call_record import make_call, call_status, end_call, play_audio, copy_recording, RecordingNotFound
from write_to_csv import process_phone_csv

# Libraries
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import whisperx
import torch
import pandas as pd
import time
from random import randint
import warnings
warnings.filterwarnings("ignore")

# Audio transcription
transcribe_model = whisperx.load_model(
    "./whisper-large-v2",
    device="cpu",
    compute_type="int8", 
    language="ta",
    vad_options={
        "vad_onset": 0.800,
        "vad_offset": 0.363
    }
)

print("Loaded whisper model")

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

print("Loaded language model")

numbers = list(pd.read_excel("numbers.xlsx")["phone"])

with open("sys_prompt.txt") as f:
    system_prompt = f.read()

for number in numbers:
    make_call(number)
    print(f"Calling {number}")
    time.sleep(2) # Delay for call to happen
    initmsg = False
    for i in range(60):
        if call_status() in [1,2]: # If call isnt active, break out
            time.sleep(1)
            if call_status() == 2 and not initmsg:
                play_audio("init_message.m4a")
                initmsg = True
        else:
            print("Call has ended")
            break
    end_call()
    print("Call has ended")
    time.sleep(5) # Wait for write complete

    try:
        path = copy_recording(number)
        time.sleep(2) # Copy wait

        call_vc = transcribe(path)
        content = generate_llm_out(language_model,language_tokenizer,system_prompt,call_vc)
        process_phone_csv(number,content)

    except RecordingNotFound:
        print("Recording not found")
        pass
    
    time.sleep(randint(10,20))


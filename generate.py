from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
import time

def generate_llm_out(model,tokenizer,system_prompt,user_prompt,log=True):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True 
    )

    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    gen_start = time.time()
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=1024
    )
    torch.cuda.synchronize()
    gen_end = time.time()

    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

    # thinking content
    try:
        index = len(output_ids) - output_ids[::-1].index(151668) # This is where thinking context ends, this is a special value used by qwen models
    except ValueError:
        index = 0 # Case when thinking is set to false

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

    # token counts
    total_output_tokens = len(output_ids)
    thinking_tokens = index  # 'index' is where the </think> token was found
    content_tokens = total_output_tokens - thinking_tokens

    if log:
        with open("logs.txt","a") as f:
            f.write(f"System prompt: {system_prompt}\n------\nUser prompt: {user_prompt}\n------\nGeneration time: {gen_end-gen_start:.2f}\n------\nThinking token count: {thinking_tokens}\n------\nContent token count: {content_tokens}\n------\nTotal token count: {total_output_tokens}\nThinking content: {thinking_content}\n------\nOutput content: {content}\n======\n")

    return content

if __name__ == "__main__": # Testing file
    model_start = time.time()
    model_name = "./Qwen3-8B"

    # 4-bit quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        attn_implementation="flash_attention_2",
    )

    model_end = time.time()
    print(f"model load time: {model_end-model_start:.2f}")

    system_prompt = """You will be given a poor quality tamil conversation transcription that may contain mixed languages of someone who attended a job fair but did not accept the job. You need to filter out the reason and output ONLY the reason in english, like 'Not interested in the job' or 'Salary was too low' etc. Avoid greetings or explanations."""

    user_prompt1 = """சொல்லுங்க எனக்கு அந்த ஜாப்ப்பேரில் அந்த டிஸ்டின்ஸ் ரொம்ப ஜெஸ்டியா இருக்கிறது. அதனால் நான் செல்லவில்லை."""

    reason1 = generate_llm_out(model,tokenizer,system_prompt,user_prompt1)

    user_prompt2 = """ஹலோ! ஹலோ! சொல்லுங்க! என்மேன் செப்மி? நான் அந்த வாடிக்கையாளரை அடுத்தினேன், எனக்கு விருப்பமில்லை. சரி."""

    reason2 = generate_llm_out(model,tokenizer,system_prompt,user_prompt2)
    print(f"Reason 1: {reason1}\n---\nReason2: {reason2}")
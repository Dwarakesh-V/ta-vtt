#!/usr/bin/env bash
set -euo pipefail

sudo usermod -aG plugdev "$LOGNAME"
sudo apt-get install -y android-sdk-platform-tools-common

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install flash-attn --no-build-isolation

# Original dir
ORIG_DIR="$(pwd)"
OUTPUT_DIR="$ORIG_DIR/whisper-large-v2"

# If folder already exists, stop
if [[ -d "$OUTPUT_DIR" ]]; then
    echo "Error: $OUTPUT_DIR already exists"
    exit 1
fi

# Temp dir
TMP_DIR="$(mktemp -d)"
echo "Using temp directory: $TMP_DIR"

cleanup() {
    rm -rf "$TMP_DIR"
}

trap cleanup EXIT

cd "$TMP_DIR"

BASE_URL="https://huggingface.co/openai/whisper-large-v2/resolve/main"

FILES=(
    model.safetensors
    added_tokens.json
    config.json
    generation_config.json
    merges.txt
    normalizer.json
    preprocessor_config.json
    special_tokens_map.json
    tokenizer.json
    tokenizer_config.json
    vocab.json
)

for file in "${FILES[@]}"; do
    echo "Downloading $file..."
    curl -L "${BASE_URL}/${file}?download=true" -o "$file"
done

echo "Running conversion..."

ct2-transformers-converter \
    --model . \
    --output_dir whisper-large-v2 \
    --copy_files tokenizer.json preprocessor_config.json

mv whisper-large-v2 "$OUTPUT_DIR"

echo "Done: $OUTPUT_DIR"
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import torch
import nemo.collections.asr as nemo_asr

print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))

model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.restore_from(
    restore_path="indicconformer_ta.nemo",
    map_location="cpu"
)

model.freeze()
model = model.to("cuda")

result = model.transcribe(
    ["recording2.wav"],
    batch_size=1,
    language_id="ta"
)

print(result[0])
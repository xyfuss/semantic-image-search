import open_clip
import torch
from PIL import Image as PILImage

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32", pretrained="laion2b_s34b_b79k"
)
tokenizer = open_clip.get_tokenizer("ViT-B-32")
model.eval()


def embed_image(pil_image) -> list[float]:
    with torch.no_grad():
        x = preprocess(pil_image).unsqueeze(0)
        vec = model.encode_image(x)
        vec = vec / vec.norm(dim=-1, keepdim=True)
    return vec[0].tolist()


def embed_text(text: str) -> list[float]:
    with torch.no_grad():
        tokens = tokenizer([text])
        vec = model.encode_text(tokens)
        vec = vec / vec.norm(dim=-1, keepdim=True)
    return vec[0].tolist()

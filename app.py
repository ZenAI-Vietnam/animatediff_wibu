from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from webui import inference_api, get_prompt

def base64_to_pil_image(base64_string):
    import base64
    from PIL import Image
    from io import BytesIO
    image = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image))
    return image

app = FastAPI()

class AnimateRequest(BaseModel):
    image: str 
    prompt: str = ""
    ratio: str = "square"
    duration: float = 1.6


@app.post("/animate")
async def animate(data: AnimateRequest):
    image = base64_to_pil_image(data.image)
    if not data.prompt:
        data.prompt = get_prompt(image)

    return inference_api(data.prompt, image, data.ratio, data.duration)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
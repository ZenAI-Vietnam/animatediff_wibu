import gradio as gr
from PIL import Image
from core import zen_img2gif, save_gif_from_bytes
import requests
import json


def pil_image_to_base64(image):
    import base64
    from io import BytesIO
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def center_crop_image(image, ratio):
    # Load the image
    width, height = image.size

    # Determine new dimensions based on the ratio
    if ratio == "square":
        new_size = min(width, height)
        left = (width - new_size)/2
        top = (height - new_size)/2
        right = (width + new_size)/2
        bottom = (height + new_size)/2
    elif ratio == "wide":
        # Assuming a 16:9 ratio for "wide"
        if width / height > 16/9:
            new_width = height * 16/9
            new_height = height
        else:
            new_width = width
            new_height = width * 9/16
        left = (width - new_width)/2
        top = (height - new_height)/2
        right = (width + new_width)/2
        bottom = (height + new_height)/2
    elif ratio == "tall":
        # Assuming a 9:16 ratio for "tall"
        if height / width > 16/9:
            new_height = width * 16/9
            new_width = width
        else:
            new_height = height
            new_width = height * 9/16
        left = (width - new_width)/2
        top = (height - new_height)/2
        right = (width + new_width)/2
        bottom = (height + new_height)/2
    else:
        raise ValueError("Unsupported ratio. Choose 'square', 'wide', or 'tall'.")

    # Crop the image
    cropped_image = image.crop((left, top, right, bottom))

    return cropped_image
def process(prompt, image, ratio, duration):
    image = center_crop_image(image, ratio)
    print(image.size)
    gif_bytes_str = zen_img2gif(prompt, image, duration)
    print("GIF Generated...")
    file = "/tmp/generated.gif"
    save_gif_from_bytes(gif_bytes_str, file)
    return file

def inference_api(prompt, image, ratio, duration):
    image = center_crop_image(image, ratio)
    gif_bytes_str = zen_img2gif(prompt, image, duration)
    print("GIF Generated...", flush=True)
    return str(gif_bytes_str)

def get_prompt(image: Image.Image):
    url = "https://ai-api.sankakucomplex.com/sdapi/v1/tagging"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "input_image": pil_image_to_base64(image)
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    tokens = response.json()
    sorted_tokens = dict(sorted(tokens.items(), key=lambda item: item[1], reverse=True))
    top_k_tokens = list(sorted_tokens.keys())[:10]
    return ','.join(top_k_tokens)
if __name__ == "__main__":
    with gr.Blocks() as app:
        with gr.Row():
            with gr.Column():
                reference_image = gr.Image(label="Reference Image", type='pil')
                prompt = gr.Textbox(placeholder="Write a prompt here...", label="Prompt")
                gen_prompt_btn = gr.Button("Generate Prompt")
                ratio = gr.Dropdown(["square", "wide", "tall"], value="square")
                duration = gr.Slider(label="Duration (s)", minimum=1.0, maximum=10.0, value=2.0)
            with gr.Column():
                generated_image = gr.Image(label="Generated Image")
                start_generate = gr.Button("Generate Image")
        
        gen_prompt_btn.click(
            get_prompt,
            inputs=[reference_image],
            outputs=[prompt]
        )
        start_generate.click(
            process,
            inputs=[prompt, reference_image, ratio, duration],
            outputs=[generated_image]
        )

    app.queue().launch(share=False, server_port=4449, server_name="0.0.0.0", debug=True, show_error=True)
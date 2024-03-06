#This is an example that uses the websockets api to know when a prompt execution is done
#Once the prompt execution is done it downloads the images using the /history endpoint

import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
from PIL import Image
import io

workflow = json.load(open("./workflow.json"))

server_address = "127.0.0.1:10001"


def save_gif_from_bytes(gif_bytes, file_path):
    with open(file_path, 'wb') as f:
        f.write(gif_bytes)
        
def resize_divisible(image, max_size=1024, divisible=16):
    W, H = image.size
    if W > H:
        W, H = max_size, int(max_size * H / W)
    else:
        W, H = int(max_size * W / H), max_size
    W = W - W % divisible
    H = H - H % divisible
    image = image.resize((W, H))
    return image

def queue_prompt(prompt, client_id):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt, client_id):
    prompt_id = queue_prompt(prompt, client_id)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    # print(history)
    for o in history['outputs']:
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            print(node_output)
            if 'gifs' in node_output:
                images_output = []
                for image in node_output['gifs']:
                    image_data = get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images

def zen_img2gif(prompt, image: Image.Image, duration: float):
    client_id = str(uuid.uuid4())
    image = resize_divisible(image, 512, 16)
    image_path = f"/tmp/{client_id}.png"
    image.save(image_path)
    width, height = image.size
    workflow["321"]["inputs"]["text"] = prompt
    workflow["499"]["inputs"]["number"] = duration
    workflow["519"]["inputs"]["Value"] = height
    workflow["520"]["inputs"]["Value"] = width
    workflow["492"]["inputs"]["image"] = image_path
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    output = get_images(ws, workflow, client_id)
    gif_bytes_str = output["487"][0]
    return gif_bytes_str

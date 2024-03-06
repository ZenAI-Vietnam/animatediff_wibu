from core import zen_img2gif, save_gif_from_bytes
from PIL import Image
import io

image = Image.open("assets/image_2.png")
prompt = "1girl, crying, shy, eyes wing, cute"
duration = 1.6

gif_bytes = zen_img2gif(prompt, image, duration)

save_gif_from_bytes(gif_bytes, "output.gif")
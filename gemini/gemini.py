
# import pathlib
# import google.generativeai as genai
# from PIL import Image

# # Configure Google Gemini API Key
# genai.configure(api_key='AIzaSyBlU4k1KyjTNIDEKJGOugsYedWXYt_el5A')

# # Load the image
# image_path = pathlib.Path('image.jpg')


# def generate(image_path):
#   with Image.open(image_path) as img:
#       # Generate text from image and text inputs
#       response = genai.GenerativeModel('gemini-pro-vision').generate_content(["Describe this image", img])
#       return response.text
    
    
import pathlib
import google.generativeai as genai
from PIL import Image
from flask import Flask, render_template, request
import base64
import os
from google.generativeai.types import HarmCategory, HarmBlockThreshold, MediaType


app = Flask(__name__)

# Configure Google Gemini API Key
genai.configure(api_key='AIzaSyBlU4k1KyjTNIDEKJGOugsYedWXYt_el5A')

def generate_text_from_image(image_file):
    with Image.open(image_file) as img:
        response = genai.GenerativeModel('gemini-pro-vision').generate_content(
            ["Describe this injury in detail. Do not include measurements (such as length & width of injury)", img],
            safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
            })
        return response.text

def generate_instructions_from_text(text):
    instructions = genai.GenerativeModel('gemini-pro').generate_content(
        ["Based on the following injury description, give step by step instructions (using a numbered list) on how to treat the injury. Just list the instructions, don't add other information", text],
            safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
            })
    return instructions.text

def instructions_to_link(text):
    link = genai.GenerativeModel('gemini-pro').generate_content(
        ["Given these instructions to help with the injury, provide a link to a trustworthy source on this topic", text],
            safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
            })
    return link.text

def generate_pics_from_instructions(text):
    response = genai.GenerativeModel('gemini-pro-vision').generate_content(
        ["Given these instructions to help with the injury, generate images for each step", text],
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
        })
    
    image_urls = [part.content for part in response.parts if part.media_type == MediaType.MEDIA_TYPE_IMAGE]
    
    return image_urls


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image_file' not in request.files:
            return 'No file part'
        
        image_file = request.files['image_file']
        
        if image_file.filename == '':
            return 'No selected file'
        
        if image_file and allowed_file(image_file.filename):
            image_path = pathlib.Path("image.jpg")
            image_file.save(image_path)
            
            generated_text = generate_text_from_image(image_path)
            instructions_text = generate_instructions_from_text(generated_text) 
            link_text = instructions_to_link(instructions_text) 
            return render_template('result.html', generated_text=generated_text, instructions_text=instructions_text, link_text=link_text)
    
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

if __name__ == '__main__':
    app.run(debug=True)

# injury image --> text (describes injury in pic) --> text is then inputted into LLM prompt --> generates a solution 
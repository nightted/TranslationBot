# Google Gemini modules
from google import genai
from google.genai import types
# Other modules
import os
import time 
import requests
import configparser
from PIL import Image
from io import BytesIO
from pathlib import Path

# Access API token and create Client
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['secret']['API_KEY']
client = genai.Client(
    api_key=api_key
)

# Select model and mode of ai reactionss
model = "gemini-2.5-flash-lite-preview-06-17" # default model 
gemini_mode = "chat" # default mode of gemini model
file_folder_path = "weather_radar_map"


def download_cwb_radar(folder_to_store, timestamp, start_time=None, end_time=None):

    # Download the rader reflectivity maps from cwb website

    if not timestamp:
        raise ValueError("timestamp is not defined.")
    
    date = timestamp.split("_")[0]
    time_stamp = timestamp.split("_")[1]    

    cwb_url = "https://www.cwa.gov.tw/Data/radar/CV1_3600_2025{}{}.png".format(date, time_stamp)

    response = requests.get(cwb_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image.save(os.path.join(folder_to_store,'radar_map_{}.jpg'.format(timestamp)))


def gemini_react(gemini_mode = None, file_path = None):

    if not gemini_mode:
        raise ValueError("gemini mode is not assigned.")

    if gemini_mode == "chat":

        chat = client.chats.create(model=model)
        while True:
            
            msg = input("please continue to chat: ")
            if "exit" in msg:
                break
            response = chat.send_message(msg)
            print(response.text)

        print("Chat End")

    elif gemini_mode == "vision":
        
        f_path = Path(file_path)
        if not f_path.exists():
            raise ValueError("path is not found.")
        f_path_list = list(f_path.iterdir())

        # assert 1 == 0, "Stop"

        if not file_path:
            raise ValueError("file path must not be empty.")

        # upload the image to genimi server
        sample_files = []
        for f in f_path_list:
            
            print("Now the file {} start to upload..".format(f.stem))
            sample_file = client.files.upload(file = f)

            # print(vars(sample_file.state))
            # assert 1 == 0 , "Stop"

            while sample_file.state.name != 'ACTIVE':
                print("Now the file {} is uploading..".format(f.stem))
                time.sleep(1)
                sample_file = client.files.get(sample_file.name)

            print("Uploading is complete.")
            print(f"Uploaded file : {sample_file.uri}.")
            sample_files.append(sample_file)

        #Call the genimi model and parse the analysis results
        prompt = ["The uploaded images are radar reflectivity map around Taiwan for the last 3 hours, there obviously a tropical cyclone is developing, \
                    starting to move to the north-east direction and tend to penatrate through Taiwan with speed around 20km/hour; \
                    Could you help to estimatet the wind level and rainfall for the next 24 hours, based on the consecutive images?"]
        
        response = client.models.generate_content(
            model=model,
            contents=[sample_files, prompt],
        )

        print(response.text)

    elif gemini_mode == "image_generation":

        # specify the model as gemini 2.0 due to its function for image generation
        model = "gemini-2.0-flash-preview-image-generation"
        
        # Define the text description for image generation 
        text_input = input("Please enter what kind of image type you would like to generate: ")
        text_input = (text_input)

        response = client.models.generate_content(
            model=model,
            contents=[text_input],
            config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
            )
        )

        for part in response.candidates[0].content.parts: # TODO: What does candidate means?
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = Image.open(BytesIO((part.inline_data.data)))
                image.save("generated_image.jpg")
    elif gemini_mode == "chat_summary":
        pass



if __name__ == "__main__":

    # download_cwb_radar(file_folder_path, "0706_1600")
    # download_cwb_radar(file_folder_path, "0706_1700")
    # download_cwb_radar(file_folder_path, "0706_1800")
    # gemini_react(gemini_mode = "vision", file_path = file_folder_path)
    gemini_react(gemini_mode = "image_generation")
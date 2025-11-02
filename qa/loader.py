import os
import time
import requests
import shutil

# Configuration
SOURCE_FOLDER = "meta"
DONE_FOLDER = os.path.join(SOURCE_FOLDER, "done")
API_URL = "https://kaballas-doe-tender.hf.space/api/v1/document/raw-text"
HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer Y1C43HM-MCJM4M1-PBXAW45-40S2VEV",
    "Content-Type": "application/json"
}

# Ensure done folder exists
os.makedirs(DONE_FOLDER, exist_ok=True)

def process_txt_files():
    for filename in os.listdir(SOURCE_FOLDER):
        if filename.endswith(".txt"):
            file_path = os.path.join(SOURCE_FOLDER, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                text_content = file.read()

            payload = {
                "textContent": text_content,
                "addToWorkspaces": "_work",
                "metadata": {
                    "title": filename
                }
            }

            try:
                response = requests.post(API_URL, headers=HEADERS, json=payload)
                print(f"Processed '{filename}': Status {response.status_code}")
                print("Response:", response.json())

                # Move file to done folder
                shutil.move(file_path, os.path.join(DONE_FOLDER, filename))

            except Exception as e:
                print(f"Error processing file '{filename}': {e}")

# Main loop
if __name__ == "__main__":
    while True:
        process_txt_files()
        time.sleep(10)

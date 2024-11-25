import os
import subprocess
from flask import Flask, request, jsonify
import time
import requests
from googletrans import Translator

# Step 1: Ensure dependencies are installed
def install_requirements():
    requirements = """
    flask
    requests
    googletrans==4.0.0-rc1
    gunicorn
    """
    with open("requirements.txt", "w") as f:
        f.write(requirements)

    try:
        subprocess.check_call([os.sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
    except Exception as e:
        print(f"Error installing dependencies: {e}")

# Install dependencies
install_requirements()

# Step 2: Define the Flask application
app = Flask(__name__)
translator = Translator()

api_url = "https://bloom-bert-api-dmkyqqzsta-as.a.run.app/predict"

def process_text(text):
    try:
        translated_text = translator.translate(text, src='id', dest='en').text
    except Exception as e:
        time.sleep(5)
        try:
            translated_text = translator.translate(text, src='id', dest='en').text
        except Exception as e:
            translated_text = None

    if translated_text:
        response = requests.post(api_url, json={"text": translated_text})
        if response.status_code == 200:
            result = response.json()
            taxonomy_level = result.get("blooms_level")
            probabilities = result.get("probabilities", {})
            probability = probabilities.get(taxonomy_level, None)
            return {
                'Level_Taksonomi': taxonomy_level,
                'Probability': probability
            }
    return {'Level_Taksonomi': None, 'Probability': None}

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({"error": "No text provided"}), 400
    return jsonify(process_text(text))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
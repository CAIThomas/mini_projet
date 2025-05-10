from flask import Flask, jsonify, request
from datetime import datetime
from google.cloud import storage
import pandas as pd
from io import StringIO
from vertexai.preview.generative_models import GenerativeModel
import vertexai
import re

# Initialisation Vertex AI
vertexai.init(project="positive-lambda-458707-v3", location="europe-west1")
model = GenerativeModel(model_name="gemini-2.0-flash-001")

# Paramètres GCS
BUCKET_NAME = "mini_projet"
BLOB_NAME = "mini_projet.csv"

app = Flask(__name__)

@app.route("/")
def root():
    return "Hello from Cloud Run ! 🚀"

@app.route("/hello")
def hello():
    return jsonify({"message": "Bienvenue sur l'API Cloud avec Flask !"})

@app.route("/status")
def status():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow()})

@app.route("/data", methods=["GET"])
def get_data():
    try:
        df = read_csv_from_gcs()
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": f"Erreur lecture GCS: {str(e)}"}), 500

@app.route("/data", methods=["POST"])
def add_person():
    data = request.get_json()

    # Validation
    if not data or 'name' not in data or 'age' not in data or 'email' not in data:
        return jsonify({'error': 'Invalid data, name, age, and email are required'}), 400

    # Lire les données existantes
    df = read_csv_from_gcs()

    # Ajouter la nouvelle personne
    new_row = pd.DataFrame([{
        'name': data['name'],
        'age': data['age'],
        'email': data['email']
    }])
    df = pd.concat([df, new_row], ignore_index=True)

    # Écrire les données mises à jour
    write_csv_to_gcs(df)

    return jsonify({'message': 'Person added successfully'}), 201

def read_csv_from_gcs():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(BLOB_NAME)

    if not blob.exists():
        return pd.DataFrame(columns=["name", "age", "email"])

    data = blob.download_as_text()
    return pd.read_csv(StringIO(data), sep=';')

def write_csv_to_gcs(df):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(BLOB_NAME)
    blob.upload_from_string(df.to_csv(index=False, sep='\t'), content_type='text/csv')

@app.route("/joke", methods=["GET"])
def get_joke():
    try:
        chat = model.start_chat()
        response = chat.send_message("Raconte-moi une blague drôle")
        joke = response.text.strip()
        joke = re.sub(r"---.*", "", joke)  # supprime les séparateurs type '---'
        joke = re.sub(r"\u00e9", " é", joke) 
        joke = re.sub(r"[^\w\s.,!?'\n-]", "", joke)  # supprime emojis mais garde \n
        joke = re.sub(r"\n{3,}", "\n\n", joke)  # évite trop de sauts de ligne

        joke = joke.strip()
        return jsonify({"joke": response.text})
    except Exception as e:
        return jsonify({"error": f"Erreur génération blague: {str(e)}"}), 500



if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)

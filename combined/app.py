import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from transformers import pipeline
from PIL import Image
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import requests

# Import components from the yield prediction project
from model_loader import ModelLoader
from preprocessing import preprocess_input

# --- APPLICATION SETUP ---
app = Flask(__name__)

# Configure upload folder for disease detection
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- LOAD MODELS (ONCE AT STARTUP) ---
try:
    # Load the yield prediction model and preprocessors
    yield_model_loader = ModelLoader.get_instance()
    print("Yield prediction model loaded successfully.")

    # Load the disease classification model from Hugging Face
    disease_pipe = pipeline("image-classification", model="linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification")
    print("Disease classification model loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")

# --- MAIN AND NAVIGATION ROUTES ---
@app.route('/')
def home():
    """Renders the main landing page."""
    return render_template('index.html')

# --- YIELD PREDICTION ROUTES ---
@app.route('/yield-prediction', methods=['GET', 'POST'])
def yield_prediction():
    """
    Handles the crop yield prediction.
    GET: Displays the input form.
    POST: Processes form data, predicts yield, and shows the result.
    """
    if request.method == 'POST':
        try:
            # Collect data from the form
            data_dict = {
                'Region': request.form['Region'],
                'Soil_Type': request.form['Soil_Type'],
                'Crop': request.form['Crop'],
                'Rainfall_mm': float(request.form['Rainfall_mm']),
                'Temperature_Celsius': float(request.form['Temperature_Celsius']),
                'Fertilizer_Used': request.form['Fertilizer_Used'],
                'Irrigation_Used': request.form['Irrigation_Used'],
                'Weather_Condition': request.form['Weather_Condition']
            }
            # Preprocess the input data
            processed_data = preprocess_input(data_dict, yield_model_loader)
            
            # Make a prediction
            prediction = yield_model_loader.model.predict(processed_data)[0]
            
            # The model predicts a scaled value. We need to inverse transform it.
            # The scaler was fit on [Rainfall, Temperature, Yield], so we create a dummy array.
            final_yield = yield_model_loader.scaler.inverse_transform([[0, 0, prediction]])[0][2]

            return render_template('yield_result.html', prediction=round(final_yield, 2), data=data_dict)
        except Exception as e:
            print(f"Error during yield prediction: {e}")
            return render_template('yield_predictor.html', error="An error occurred during prediction.")
    
    # For a GET request, just show the form
    return render_template('yield_predictor.html')


# --- DISEASE DETECTION ROUTES ---
@app.route('/disease-detection', methods=['GET', 'POST'])
def disease_detection():
    """
    Handles crop disease detection.
    GET: Displays the image upload form.
    POST: Processes the uploaded image, classifies the disease, and shows the result.
    """
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)
        if file:
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Process the image with the ML model
                image = Image.open(file_path)
                results = disease_pipe(image)
                results = sorted(results, key=lambda x: x['score'], reverse=True)

                return render_template("disease_result.html", results=results, image_path=file_path)
            except Exception as e:
                print(f"Error during disease detection: {e}")
                return render_template('disease_detector.html', error="Failed to process the image.")

    # For a GET request, show the upload form
    return render_template('disease_detector.html')


@app.route('/search_disease')
def search_disease():
    """
    API endpoint to fetch disease solutions by scraping websites.
    Called asynchronously by JavaScript on the disease result page.
    """
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Define sources to scrape
        search_query = quote_plus(f"{query} plant disease treatment")
        sources = [
            f"https://www.planetnatural.com/?s={search_query}",
            f"https://extension.umn.edu/search?search={search_query}"
        ]

        description = ""
        solutions = []
        source_list = []

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

        for url in sources:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    if len(p.text.strip()) > 100:
                        description += p.text.strip() + " "
                        if len(description) > 500:
                            break
                
                list_items = soup.find_all('li')
                for item in list_items:
                    if len(item.text.strip()) > 20:
                        solutions.append(item.text.strip())

                source_list.append({"url": url, "title": soup.title.string if soup.title else url})
                if len(solutions) > 4:
                    break

        description = (description[:500] + '...') if len(description) > 500 else description
        solutions = list(set(solutions))[:5] # Get unique solutions

        return jsonify({
            "description": description or "No detailed description available. Please consult a local expert.",
            "solutions": solutions or ["No specific solutions found. Try searching online or consult a local agricultural expert."],
            "sources": source_list
        })
    except Exception as e:
        print(f"Error during web scraping: {e}")
        return jsonify({"description": "Error fetching information.", "solutions": [], "sources": []}), 500


# --- RUN THE APPLICATION ---
if __name__ == '__main__':
    app.run(debug=True)

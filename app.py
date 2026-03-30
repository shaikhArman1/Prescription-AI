import os
import json
import io
from PIL import Image
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')

# Configure Gemini API
# If GEMINI_API_KEY is an environment variable, it configures automatically.
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "your_api_key_here":
    genai.configure(api_key=api_key)

@app.route('/')
def serve_index():
    return send_file('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_prescription():
    if not api_key or api_key == "your_api_key_here":
         return jsonify({"error": "Gemini API Key is not configured in .env file"}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Load the image
        img = Image.open(io.BytesIO(file.read()))
        
        # Use the gemini-2.5-flash model which is great for fast text/image tasks
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = """
        You are an expert AI Prescription Analyzer. 
        Carefully read the handwriting or text in the provided prescription image.
        
        1. Extract a complete summary of the disease or condition if mentioned by the doctor.
        2. Extract a list of ALL prescribed medicines from the prescription, including their dosage and frequency/timing.
        
        Format your response EXACTLY as a JSON object with these keys:
        "disease_summary": (A string summarizing the disease or condition. If none is found, return "No specific disease mentioned.")
        "medicines": (A list of objects, where each object has "name", "dosage", and "frequency" keys)
        
        Example:
        {
          "disease_summary": "Patient complains of viral fever and body ache.",
          "medicines": [
             {"name": "Paracetamol", "dosage": "500mg", "frequency": "Twice a day"},
             {"name": "Amoxicillin", "dosage": "250mg", "frequency": "Once a day"}
          ]
        }
        
        Do not include any markdown formatting like ```json or newlines around the JSON, just the raw JSON string.
        If you cannot decipher a field, output "Unknown" for that field's value.
        """
        
        response = model.generate_content([prompt, img])
        
        # Parse the JSON response
        text = response.text.strip()
        # Clean up in case Gemini still included markdown
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
            
        if text.endswith("```"):
            text = text[:-3]
            
        result = json.loads(text.strip())
        return jsonify(result)
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        # Sometimes Gemini API errors (e.g., safety blocks, connection issues)
        return jsonify({"error": "Failed to analyze the prescription image.", "details": str(e)}), 500

if __name__ == '__main__':
    print("Starting Server on http://Localhost:5000 ...")
    app.run(debug=True, port=5000)

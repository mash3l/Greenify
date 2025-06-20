import os

import torch
import timm
from flask import Flask, request, jsonify
from torchvision import transforms
from PIL import Image



app = Flask(__name__)
# UPLOAD_FOLDER = 'uploaded'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load model
def load_model(model_path, num_classes):
    model = timm.create_model("rexnet_150", pretrained=False, num_classes=num_classes)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

model_path = "disease_best_model.pth"
num_classes = 72
model = load_model(model_path, num_classes)

# Class names (same list as before — omitted here for brevity)
class_names = ["Apple___alternaria_leaf_spot","Apple___black_rot","Apple___brown_spot","Apple___gray_spot","Apple___healthy","Apple___rust",
                "Apple___scab","Bell_pepper___bacterial_spot","Bell_pepper___healthy","Blueberry___healthy","Cassava___bacterial_blight",
                "Cassava___brown_streak_disease","Cassava___green_mottle","Cassava___healthy","Cassava___mosaic_disease","Cherry___healthy",
                "Cherry___powdery_mildew","Coffee___healthy","Coffee___red_spider_mite","Coffee___rust","Corn___common_rust","Corn___gray_leaf_spot",
                "Corn___healthy","Corn___northern_leaf_blight","Grape___Leaf_blight","Grape___black_measles","Grape___black_rot","Grape___healthy",
                "Orange___citrus_greening","Peach___bacterial_spot","Peach___healthy","Potato___bacterial_wilt","Potato___early_blight","Potato___healthy",
                "Potato___late_blight","Potato___leafroll_virus","Potato___mosaic_virus","Potato___nematode","Potato___pests","Potato___phytophthora",
                "Raspberry___healthy","Rice___bacterial_blight","Rice___blast","Rice___brown_spot","Rice___tungro","Rose___healthy","Rose___rust",
                "Rose___slug_sawfly","Soybean___healthy","Squash___powdery_mildew","Strawberry___healthy","Strawberry___leaf_scorch","Sugercane___healthy",
                "Sugercane___mosaic","Sugercane___red_rot","Sugercane___rust","Sugercane___yellow_leaf","Tomato___bacterial_spot","Tomato___early_blight",
                "Tomato___healthy","Tomato___late_blight","Tomato___leaf_curl","Tomato___leaf_mold","Tomato___mosaic_virus","Tomato___septoria_leaf_spot",
                "Tomato___spider_mites","Tomato___target_spot","Watermelon___anthracnose","Watermelon___downy_mildew","Watermelon___healthy","Watermelon___mosaic_virus"]  
  # Keep your class names list here

# Transformations
transformations = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Prediction function
def predict_image(file):
    image = Image.open(file).convert("RGB")
    image = transformations(image).unsqueeze(0)

    with torch.no_grad():
        output = model(image)
        _, pred = torch.max(output, 1)
    
    return class_names[pred.item()]

@app.route('/', methods=['POST'])
def predict():
    if 'imagefile' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['imagefile']
    try:
        prediction = predict_image(file)
        return jsonify({"result": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
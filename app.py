
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
from keras.models import load_model
import uuid
from io import BytesIO

# Load the pre-trained model
model = load_model("CNN2Dmodel1.h5")

def preprocess_image(image):
    image = image.resize((224, 224))
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array

def predict(image):
    processed_image = preprocess_image(image)
    prediction = model.predict(processed_image)
    return prediction

def main():
    st.image("./Logo.png", width=100)
    st.markdown("""<h1 style='text-align: center;'>Dementia Classification through Facial Analysis using MOD-2D-CNN</h1>""", unsafe_allow_html=True)
    st.write("Choose an option to input image:")
    option = st.radio("Select Input Option", ("Webcam", "Upload Image"))
    
    Email = st.text_input(label="Email*")

    if option == "Webcam":
        st.write("Please allow access to your webcam.")
        uploaded_file = st.camera_input("Take a picture")
    else:
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if Email.strip() == '' or '@' not in Email or '.' not in Email:
        st.error("Please enter a valid email address.")
    elif uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        
        if st.button("Predict"):
            prediction = predict(image)
            if prediction[0][0] > 0.5:
                Prediction = "Non-Demented"
            else:
                Prediction = "Demented"
            st.write(Prediction)
            
            # Display a success message
            st.success("Facial Image Captured Successfully! You will get your cognitive assessment result for your dementia status at your provided email address soon.")
            
            
if __name__ == '__main__':
    main()


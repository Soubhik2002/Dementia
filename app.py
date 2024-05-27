import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
from keras.models import load_model
import os
import uuid
from streamlit_gsheets import GSheetsConnection
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from io import BytesIO


conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(worksheet="Image", usecols=list(range(7)), ttl=5)
existing_data = existing_data.dropna(how="all")


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


# def authenticate_drive():
#     gauth = GoogleAuth()
#     gauth.LocalWebserverAuth() 
#     drive = GoogleDrive(gauth)
#     return drive

def authenticate_drive():
    gauth = GoogleAuth()
    gauth.DEFAULT_SETTINGS['client_config_file'] = 'client_secrets.json'
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive


# def upload_to_drive(uploaded_file, filename, folder_id):
#     drive = authenticate_drive()
#     image_content = uploaded_file.getvalue()
#     image_file = BytesIO(image_content)
#     temp_path = "./temp.jpg"
#     with open(temp_path, "wb") as f:
#         f.write(image_content)
    
#     file = drive.CreateFile({'title': filename, 'parents': [{'id': folder_id}]})
#     file.SetContentFile(temp_path)
#     file.Upload()
#     f.close()
    
#     return file['alternateLink']

def upload_to_drive(uploaded_file, filename, folder_id):
    drive = authenticate_drive()
    image_content = uploaded_file.getvalue()
    
    file = drive.CreateFile({'title': filename, 'parents': [{'id': folder_id}]})
    file.content = BytesIO(image_content)
    file.Upload()
    return file['alternateLink']



def main():
    st.image("./Logo.png", width=100)
    st.markdown("""<h1 style='text-align: center;'>Dementia Classification through Facial Analysis using MOD-2D-CNN</h1>""", unsafe_allow_html=True)
    st.write("Choose an option to input image:")
    option = st.radio("Select Input Option", ("Webcam", "Upload Image"))
    
    
    if option == "Webcam":
        st.write("Please allow access to your webcam.")
        Email = st.text_input(label="Email*")
        uploaded_file = st.camera_input("Take a picture")
        
        if Email.strip() == '' or '@' not in Email or '.' not in Email and uploaded_file is not None:
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
                
                folder_id = '1oUYXeaqAcmoZ3Y1I_VMsw5_I3gWlwbu-' 
                link = upload_to_drive(uploaded_file, str(uuid.uuid4()) + ".jpg", folder_id)
                Image_Data = pd.DataFrame(
                    [
                        {
                            "Email_2": Email,
                            "Image_Name": link,
                            "Result": Prediction
                        }
                    ]
                )
                updated_df = pd.concat([existing_data, Image_Data], ignore_index=True)
                try:
                    conn.update(worksheet="Image", data=updated_df)
                    st.success("Faccial Image Captured Successfully !!! Congratulations On Completing The Whole Journey, Now You Will Get Your Whole Cognitive Assessment Result For Your Dementia Status In Your Provided E-mail I'd Soon.")
                except Exception as e:
                    st.write("Image and Prediction Not Uploaded to Google Sheets!")
        
        
    elif option == "Upload Image":
        # File uploader
        Email = st.text_input(label="Email*")
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
                
                folder_id = '1oUYXeaqAcmoZ3Y1I_VMsw5_I3gWlwbu-'  
                link = upload_to_drive(uploaded_file, str(uuid.uuid4()) + ".jpg", folder_id)

                Image_Data = pd.DataFrame(
                    [
                        {
                            "Email_2": Email,
                            "Image_Name": link,
                            "Result": Prediction 
                        }
                    ]
                )
                updated_df = pd.concat([existing_data, Image_Data], ignore_index=True)
                try:
                    conn.update(worksheet="Image", data=updated_df)
                    st.success("Faccial Image Captured Successfully !!! Congratulations On Completing The Whole Journey, Now You Will Get Your Whole Cognitive Assessment Result For Your Dementia Status In Your Provided E-mail I'd Soon.")
                except Exception as e:
                    st.error(f"Error occurred while updating Google Sheets: {e}")
                    
        

if __name__ == '__main__':
    main()

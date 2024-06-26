import os
import google.generativeai as genai
import requests
import streamlit as st
import time

# Set background image
page_bg_img = '''
<style>
[data-testid="stAppViewContainer"]{
background-image: url("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjCZ27eLOBB8MUm_1FpJUlT0JpRB-rzVHkTM1KlVimGd3Lfi2CjobmidNN3kKC_I767wh7X1aawIlCdf-59zxfEh8APdmSGiPobbEV0_Dl-JfT82AO9ihol9FxU_COxmsEhZT5nmJHwN3v2V3D7H3wZtwEB6rQ-EkL3jtZrOussnVW0fElk3lAqCzJQxCB1/s1071/20240426-152237.png");
background-size: cover;
}

[data-testid="stSidebar"]{
background-image: url("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEibBG6rvIOR6WyB7AD80ZLCp381xG5K6c4gpKrIbZwrsRTIXDTaUZHHhjlwazCdSWoQjwta_yt5v1dNrqUwnCt81RqcDIib9t-MqLCQ2vqZ1aVO33IXfI2OQ2dfohqMhsul9AoI3LCKemUg9DwiOjfeqtaZ6BZ4aFs2pXCmxpJx6MysilW4aNdCGdYyhfy_/s204/Screenshot%202024-04-26%20162431.png");
background-size: cover;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# Configure access to the Gemini app
os.environ['GOOGLE_API_KEY'] = 'AIzaSyD4OT0cgOFFg3Tvymj6lVyYBEKSEVV4Wto'
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Define the model variable at the global scope
model = None

# Function to generate an image using OpenAI's DALL-E
def generate_image(api_key, query):
    endpoint = "https://api.openai.com/v1/images"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": query,
        "max_tokens": 100,  # Adjust as needed
        "temperature": 0.7,  # Adjust as needed
        "top_p": 1.0,  # Adjust as needed
        # Add more parameters if supported by the API
    }
    response = requests.post(endpoint, json=data, headers=headers)
    if response.status_code == 200:
        image_url = response.json()["url"]
        return image_url
    else:
        print(f"Failed to generate image. Status code: {response.status_code}")
        return None

# Define a function for asking the chatbot
def ask_chatbot(query):
    global model  # Access the global model variable
    try:
        # Send query to Google Generative AI API
        print("Querying chatbot with:", query)  # Debug statement
        response = model.generate_content(query)
        print("Chatbot response:", response)  # Debug statement
        return response.text  # Return the text content of the response
    except Exception as e:
        st.error("An error occurred while querying the chatbot: {}".format(str(e)))
        return None

# Define a function to handle retries
def retry_request(func, max_retries=3, delay=1):
    retries = 0
    while retries < max_retries:
        try:
            return func()
        except Exception as e:
            st.warning("Retry attempt {} failed: {}".format(retries + 1, str(e)))
            retries += 1
            time.sleep(delay)
    st.error("Max retries exceeded. Unable to complete the request.")
    return None

def main():
    global model  # Access the global model variable 

    html = '''
    <p style="color:white; font-family: Arial, sans-serif; font-size: 24px;">
    Welcome To The 
    <span style="color:green;">Future</span>
    <span style="color:white;">Of</span>
    <span style="color:blue;">Tourism</span>
    </p>
    '''
    st.markdown(html, unsafe_allow_html=True)
    # List available models
    try:
        models = genai.list_models()
        model_names = [model.name for model in models]

        # Select the model
        selected_model = st.sidebar.selectbox("Select Model", model_names)
        
        # Initialize the selected model
        model = genai.GenerativeModel(selected_model)

    except Exception as e:
        st.error("An error occurred while initializing the model: {}".format(str(e)))
        return
    
    html='''
    <p style="color:white">Where connvenince meets exploration. Lets our chatbot be your trusted companion \n as you embark on  your next adventure </p>
    <p style="color:white">Ask me anything about your destination 😎 </p>
    '''
    st.markdown(html, unsafe_allow_html=True)
    user_query = st.text_input("You:")

    if st.button("Ask"):
        if user_query:
            # Retry asking the chatbot in case of errors
            chatbot_response = retry_request(lambda: ask_chatbot(user_query))

            if chatbot_response is not None:
                st.success("Chatbot Response:\n{}".format(chatbot_response))

                # Generate image based on the chatbot response
                image_url = generate_image("sk-proj-snjFxSme5E01v3dv7jt3T3BlbkFJHUxAvj82OGBLOEuQK7YA", chatbot_response)
                if image_url:
                    st.image(image_url, caption="Image generated based on chatbot response", use_column_width=True)
                else:
                    st.warning("Image generation failed.")

if __name__ == "__main__":
    main()

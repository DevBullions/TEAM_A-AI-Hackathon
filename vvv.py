import os
import google.generativeai as genai
import streamlit as st
import time

# Configure access to the Gemini app
os.environ['GOOGLE_API_KEY'] = 'AIzaSyDUt0Hw-mVUVzy_LRXIrOoTnay61eYDgEI'
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Define the model variable at the global scope
model = None

# Define a function for asking the chatbot
def ask_chatbot(query):
    global model  # Access the global model variable
    try:
        # Send query to Google Generative AI API
        response = model.generate_content(query)
        return response
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
    st.title("Tourism Chatbot")

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

    st.header("Ask me anything about your destination:")
    user_query = st.text_input("You:")

    if st.button("Ask"):
        if user_query:
            # Retry asking the chatbot in case of errors
            bot_response = retry_request(lambda: ask_chatbot(user_query))

            # Extracting budget information from bot response
            budget = None
            if bot_response:
                budget_keywords = ["budget", "cost", "price"]
                for keyword in budget_keywords:
                    if keyword in bot_response.lower():
                        budget_index = bot_response.lower().index(keyword)
                        budget_text = bot_response[budget_index:]
                        budget_text = budget_text.split(" ", 1)[1]  # Remove the keyword
                        budget = budget_text.split()[0]  # Extract the budget amount
                        break

            if bot_response is not None:
                if budget:
                    st.success("Chatbot: {} (Budget: {})".format(bot_response, budget))
                else:
                    st.success("Chatbot: {}".format(bot_response))

if __name__ == "__main__":
    main()

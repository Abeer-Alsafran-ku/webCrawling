import time
import requests
from ds.auto_create_dataset import safe_request
import bs4
import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import joblib

# Ensure required NLTK resources are available (handles first run setups)
def ensure_nltk_resource(resource_name, resource_path):
    try:
        nltk.data.find(resource_path)
    except LookupError:
        nltk.download(resource_name)


ensure_nltk_resource('stopwords', 'corpora/stopwords')
ensure_nltk_resource('punkt', 'tokenizers/punkt')
ensure_nltk_resource('punkt_tab', 'tokenizers/punkt_tab')

# Initialize stopwords set
stop_words = set(stopwords.words('english'))


# Define a function to clean text
def clean_text(text):
    if pd.isna(text):
        return ""
    if not isinstance(text, str):
        text = str(text)
    # Tokenize the text
    tokens = word_tokenize(text.lower())

    # Handle 'ai' abbreviation conversion
    processed_tokens = []
    for word in tokens:
        if word == 'ai':
            processed_tokens.append('artificial intelligence')
        else:
            processed_tokens.append(word)

    # Remove stopwords, punctuation, and short words
    filtered_tokens = [word for word in processed_tokens if
                       word not in stop_words and
                       word not in string.punctuation and
                       len(word) > 2] # Filter words with length > 2

    return " ".join(filtered_tokens)



if __name__ == "__main__":
    # step 1 : get URL from user input
    url = input("Enter the URL to fetch: ")
    try:
        response = safe_request("GET", url)
        print("Request successful!")
        print("Response content:")
        # print(response.text)
        # step 2 : extract the content of the html page
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else 'No title found'
        # print(f"Page Title: {title}")
        heading = soup.find('h1')
        if heading:
            print(f"Main h1 Heading: {heading.get_text()}")
        elif soup.find('h2'):
            heading = soup.find('h2')
            # print(f"Main h2 Heading: {heading.get_text()}")
        elif soup.find('h3'):
            heading = soup.find('h3')
            # print(f"Main h3 Heading: {heading.get_text()}")
        else:
            print("No main heading found.")
        body_text = soup.get_text(separator=' ', strip=True)
        # print(f"Body Text: {body_text[:500]}...")  # Print first
    except Exception as e:
        print(f"Request failed: {e}")

    # concat the title, heading, and body text
    full_content = f"{title} {heading.get_text() if heading else ''} {body_text}"
    print(f"Full Content: {full_content[:500]}...")  # Print first 500 characters

    # step 3 : Classify the content using the trained model
    # Load the model and vectorizer
    with open('svc_model.pkl', 'rb') as file_model:
        model = joblib.load(file_model)
    with open('tfidf_vectorizer.pkl', 'rb') as file_vectorizer:
        vectorizer = joblib.load(file_vectorizer)
    # Preprocess the content
    cleaned_content = clean_text(full_content)
    # Vectorize the content
    vectorized_content = vectorizer.transform([cleaned_content])
    # Make prediction
    prediction = model.predict(vectorized_content)

    if prediction[0] == '1':
        print(f"\nPrediction: {prediction[0]}\n Meaning the content of the web page {url} is related to AI")  # Assuming binary classification: 0 or 1
    elif prediction[0] == '0':
        print(f"\nPrediction: {prediction[0]}\n Meaning the content of the web page {url} is not related to AI")  # Assuming binary classification: 0 or 1
    else:
        print(f"\nPrediction: {prediction[0]}\n Meaning the content of the web page {url} is of unknown class")
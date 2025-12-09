import time
import requests
from auto_create_dataset import safe_request
import bs4
from svm import clean_text
import joblib

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
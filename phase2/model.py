# step 1 : vectorize the text dataset
from unittest import case
from matplotlib.pyplot import clf
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.naive_bayes import GaussianNB, MultinomialNB            
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix,classification_report
import joblib
import time

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
        if word.lower() == 'ai': # case insensitive check
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
    model_type = input("Enter model type (GNB for GaussianNB / MNB for MultinomialNB / SVM for Support Vector Machines / DT for Decision Trees ): ").strip().upper()
    stime = time.time()
    match model_type:
        case 'GNB':
            model = GaussianNB()
            filename_vectorizer = f'tfidf_{model_type}_vectorizer.pkl'
        case 'MNB':
            model = MultinomialNB()
            filename_vectorizer = f'tfidf_{model_type}_vectorizer.pkl' 
        case 'SVM':
            model = SVC()
            filename_vectorizer = f'tfidf_{model_type}_vectorizer.pkl' 
        case 'DT':
            model = DecisionTreeClassifier()
            filename_vectorizer = f'tfidf_{model_type}_vectorizer.pkl' 
        case _:
            print("Unsupported model type.")
            exit(1)
    # read csv, explicitly defining column names as there might not be a header row
    df = pd.read_csv('dataset.csv', header=None, names=['content', 'label'])

    # Apply the cleaning function to the entire 'content' column
    df['cleaned_content'] = df['content'].apply(clean_text)
    # print(len(df['cleaned_content']), "rows after cleaning")
    # vectorize the words using TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df['cleaned_content']) # Apply to the cleaned content column
    joblib.dump(vectorizer, filename_vectorizer)
    # print(f"Vectorizer saved as {filename_vectorizer}")
    # Define target variable
    y = df['label']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a Gaussian Naive Bayes classifier (works with TF-IDF features)
    if model_type in ['GNB', 'MNB']:
        model.fit(X_train.toarray(), y_train)
        y_pred = model.predict(X_test.toarray())
        # Make predictions with the loaded model (requires dense arrays)
        model_predictions = model.predict(X_test.toarray())
   
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        model_predictions = model.predict(X_test)

    etime = time.time()
    print(f"Training time for {model_type}: {etime - stime} seconds")

    # Make predictions and evaluate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy}")
    print(classification_report(y_test, model_predictions))
    print(confusion_matrix(y_test, model_predictions))

    # Save the trained model
    filename = f'{model_type}_model.pkl'
    joblib.dump(model, filename)
    print(f"Model saved as {filename}")


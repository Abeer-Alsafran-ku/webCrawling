# step 1 : vectorize the text dataset
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
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

# read csv, explicitly defining column names as there might not be a header row
df = pd.read_csv('dataset.csv', header=None, names=['content', 'label'])

# Apply the cleaning function to the entire 'content' column
df['cleaned_content'] = df['content'].apply(clean_text)

# vectorize the words using TF-IDF
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['cleaned_content']) # Apply to the cleaned content column

# Define target variable
y = df['label']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Support Vector Classifier (SVC) model
clf = SVC(kernel='linear')
clf.fit(X_train, y_train)

# Make predictions and evaluate accuracy
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model accuracy: {accuracy}")



# Save the trained model
filename = 'svc_model.pkl'
joblib.dump(clf, filename)
print(f"Model saved as {filename}")

# Load the model from disk
loaded_model = joblib.load(filename)
print("Model loaded successfully!")

# Make predictions with the loaded model
loaded_model_predictions = loaded_model.predict(X_test)
loaded_model_accuracy = accuracy_score(y_test, loaded_model_predictions)

print(f"Accuracy of loaded model: {loaded_model_accuracy}")

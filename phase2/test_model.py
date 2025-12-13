import joblib
from evaluate_model import clean_text
import time


if __name__ == "__main__":
    # Load the model and vectorizer
    with open('svc_model.pkl', 'rb') as file_model:
        model = joblib.load(file_model)
    print("Model loaded successfully!")
    # get the input data
    data1 = """
    Artificial Intelligence (AI) has rapidly transitioned from a futuristic concept to an integral part of our daily lives. From virtual assistants like Siri and Alexa to advanced recommendation engines on streaming platforms, AI is reshaping how we interact with technology. But beyond these everyday conveniences, AI is fundamentally transforming industries, society, and even the way we think about problem-solving.

    1. AI in Industry

    AI is no longer confined to tech giants—it is revolutionizing traditional industries:

    Healthcare: AI-powered diagnostic tools can analyze medical images faster and often more accurately than humans, enabling early detection of diseases. Predictive analytics also help in patient management and resource allocation.

    Finance: AI algorithms detect fraudulent transactions in real-time, optimize investment strategies, and personalize banking services for customers.

    Manufacturing: Intelligent automation and predictive maintenance reduce downtime and increase efficiency in production lines.

    2. The Role of Machine Learning

    At the heart of AI lies machine learning (ML), a technique where systems learn patterns from data rather than relying on explicit programming. ML powers applications like speech recognition, autonomous driving, and natural language processing (NLP). Deep learning, a subset of ML, mimics human neural networks and has enabled breakthroughs in image recognition, language translation, and even creative tasks like generating art or music.

    3. Ethical Considerations

    As AI grows, so do ethical concerns:

    Bias: AI systems can inherit biases present in training data, leading to unfair or discriminatory outcomes.

    Privacy: AI’s ability to analyze massive amounts of personal data raises serious privacy issues.

    Job Displacement: Automation threatens some traditional jobs, even as it creates new opportunities in AI development, data science, and human-AI collaboration.

    4. The Future of AI

    The future of AI is both exciting and uncertain. Emerging trends include:

    Explainable AI (XAI): Making AI decisions transparent and understandable to humans.

    AI in Climate Science: Predicting climate changes, optimizing energy usage, and developing sustainable solutions.

    Human-AI Collaboration: AI is becoming a tool to augment human intelligence, helping professionals make better decisions rather than replacing them.
    """
    data1 = data1.strip()
    data2 = """ 
        There are over 100 types of cancer. Healthcare providers categorize them according to where they start in your body and the type of tissue they affect. There are three broad cancer classifications:

Solid cancers: This is the most common type of cancer, making up about 80% to 90% of all cases. This includes carcinoma that forms in epithelial tissue (like your skin, breast, colon and lungs) and sarcoma that forms in bone and connective tissues.
Blood cancers: These are cancers that start in your blood cells or lymphatic system. Examples include leukemia, lymphoma and multiple myeloma.
Mixed: Cancers that involve two classifications or subtypes. Examples include carcinosarcoma and adenosquamous carcinoma.
How common is cancer?
Cancer is the second most common cause of death worldwide. Researchers estimate that in 2024, over 2 million people living in the U.S. will receive a cancer diagnosis, and over 611,000 people will die from the disease.

About 1 in 4 people will develop cancer at some point during their lifetime.

The most common cancers in the U.S. are:

Breast cancer.
Lung cancer.
Prostate cancer.
Colorectal cancer.
Blood cancers.
Anyone can develop cancer, but cases vary based on race and sex. According to the 2022 Annual Report on Cancer, the disease:

Affects slightly more men than women.
Affects people over 60 more than any other age group.
Affects more Black men than those in other racial groups.
Affects more women who are American Indian or Alaska Natives than those in other racial groups.
Symptoms and Causes
What are the symptoms of cancer?
Symptoms of cancer vary from person to person. They depend on what type of cancer you have and how advanced it is.


        """
    data2 = data2.strip()
    # convert the text to vector using the loaded vectorizer
    cleaned_text = clean_text(data2)
    vectorizer = joblib.load('tfidf_vectorizer.pkl')
    # Ensure the vectorizer is loaded correctly
    if vectorizer is None:
        raise ValueError("Vectorizer not loaded correctly. Please check the file path.")
    
    print("Vectorizer loaded successfully!")
    # Transform the cleaned text into the vector space
    X_new = vectorizer.transform([cleaned_text]) # Transform, not fit_transform, and pass as a list

    predictions = model.predict(X_new)
    print("Predictions:", predictions)
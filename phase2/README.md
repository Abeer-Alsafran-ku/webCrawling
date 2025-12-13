# Phase 2: Intelligent Web Page Classifica6on Using Machine Learning
Web crawling using machine learning (SVM and Naive Bayes Algorithms)

# Web Crawler using Support Vector Machine (SVM)

This project implements a web crawler that navigates web pages using the **Greedy Best First Search (GBFS)** algorithm. The crawler prioritizes links based on a heuristic function, aiming to efficiently reach target pages or maximize coverage based on link relevance.  

# Web Crawler using Naive Bayes (NB)

Our approach is to treat each page as a node and each link as an edge. The crawler then assigns a value to each link on the page based on its relevance as per the heuristic function. 

## Features
- Machine learning to support web crawling.
- Configurable start URL and target keywords.
- Simple and modular Python implementation.
- Tracks visited pages to avoid loops.

## File Structure
```text
webCrawling/phase2
  ├──  main.py # Web crawling integerated with ML
  ├──  evaluate_model.py # Test the ML models to predict the class of the webpage
  ├──  test_model.py # Static test case 
  ├──  train_model.py # Train the models and save the weights and the vectorizer 
  ├──  README.md # Project documentation and usage steps
  ├──  *_model.pkl # model weights
  ├──  *_vectorizer.pkl # vectorizer weights 
  └──  requirements.txt # Python dependencies
  ds/
    ├──  ai_related_webPages.txt # List of AI Related Web Pages
    ├──  non_ai_related_webPages.txt # List of Non-AI Related Web Pages
    └──  auto_create_dataset.py # Automatically create the content of a list of webpages
  results/
    └──  *.png # Confusion Matrix results evaluating plot
  AStar/
    ├──  AStarCrawler.py # Crawler from phase 1 
    └──  AStarHelperFunctions.py # Helper functions for AStarCrawler.py
  ├── report.pdf # A report for this project 
  └──  dataset.csv # A dataset consist of the body of AI related and non related web pages and the label 0: non related | 1: related 
```

## How to Run the Code

### 1. Clone the repository
```bash
download the file or git clone https://github.com/Abeer-Alsafran-ku/webCrawling.git 
cd webCrawling/phase2/
pip install -r requirements.txt
python main.py <SVM|DT|MNB|GNB> #for integrates crawler 
python evaluate_model.py #for evaluating classifiers
python train_model.py #for train the models 
python test_model.py #for testing models
```

## How SVM and other models Works in This Crawler

The SVM will classify the web page if it is AI related web page, or Non AI related page.

**Steps SVM:**
1. Train the SVM model on the (`dataset.csv`) dataset.
2. Test the model. (`check for it's accuracy and recall + F1-Score`)
3. Start from the initial URL (`START_URL`).
4. Process the body of the web page.
5. Classify if the web page is AI related or not (`using the model`).
6. Visit the page and repeat until the target or maximum depth is reached.

**Diagram:**
- To be added

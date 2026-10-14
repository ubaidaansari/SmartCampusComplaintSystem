
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Training data: complaint descriptions and their categories
complaints = [
    "Classroom fan is not working",
    "Electricity problem in classroom",
    "Light is broken",
    "Water tap is leaking",
    "No drinking water in college",
    "Washroom water problem",
    "Classroom benches are broken",
    "College desk is damaged",
    "Chair is broken",
    "WiFi is not working",
    "Internet connection problem",
    "Computer lab network is down",
]

categories = [
    "Electrical",
    "Electrical",
    "Electrical",
    "Water",
    "Water",
    "Water",
    "Maintenance",
    "Maintenance",
    "Maintenance",
    "Internet",
    "Internet",
    "Internet",
]

# Create and train the machine learning model
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", MultinomialNB())
])

model.fit(complaints, categories)


def predict_category(description):
    prediction = model.predict([description])[0]
    return prediction


# Test the model when this file is run directly
if __name__ == "__main__":
    test_complaint = "The fan in my classroom is not working"
    result = predict_category(test_complaint)

    print("Complaint:", test_complaint)
    print("Predicted Category:", result)
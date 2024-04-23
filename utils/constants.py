import os

DB_HOST = os.getenv("DB_HOST", "localhost")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")

LIST_TOPICS = [
    "World News",
    "National News",
    "Business & Finance",
    "Science & Technology",
    "Health & Wellness",
    "Entertainment & Culture",
    "Sports",
    "Travel",
    "Politics",
    "Education",
    "Environment & Sustainability",
    "Arts & Literature",
    "Gaming & Esports",
    "Food & Cooking",
    "Fashion & Beauty",
    # Specific Interests can be nested within these categories
    "Local News",
    "Personal Finance",
    "Science by Field",
    "Health Conditions",
    "Hobbies & Interests",
    "Social Issues",
]

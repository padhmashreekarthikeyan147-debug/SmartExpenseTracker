def predict_category(description):

    text = description.lower()

    category_keywords = {

        "Food": [
            "pizza", "burger", "hotel", "restaurant",
            "food", "tea", "coffee", "juice", "biryani"
        ],

        "Travel": [
            "uber", "ola", "bus", "train",
            "flight", "petrol", "diesel", "fuel", "auto"
        ],

        "Shopping": [
            "amazon", "flipkart", "shirt",
            "dress", "shoes", "mall", "shopping"
        ],

        "Education": [
            "college", "school", "book",
            "pen", "course", "fees", "exam"
        ],

        "Medical": [
            "hospital", "doctor", "medicine",
            "tablet", "clinic", "medical"
        ],

        "Entertainment": [
            "movie", "netflix", "game",
            "cinema", "spotify"
        ]
    }

    for category, words in category_keywords.items():

        for word in words:

            if word in text:
                return category

    return "Others"
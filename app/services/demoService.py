from app.ai.demoAI import predict_category
from app.ai.demoAI2 import predict_next_month

transactions = []


def create_transaction(data):
    category = predict_category(data["description"])

    transaction = {
        "id": len(transactions) + 1,
        "amount": data["amount"],
        "description": data["description"],
        "category": category,
    }

    transactions.append(transaction)

    return transaction


def predict_expense():
    return predict_next_month(transactions)

def predict_next_month(transactions):
    if not transactions:
        return 0

    avg = sum(t["amount"] for t in transactions) / len(transactions)

    return round(avg * 1.2, 2)

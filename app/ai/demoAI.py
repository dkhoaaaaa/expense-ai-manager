def predict_category(text):
    text = text.lower()

    if "ăn" in text:
        return "Ăn uống"
    elif "mua" in text:
        return "Mua sắm"
    elif "học" in text:
        return "Giáo dục"
    return "Khác"

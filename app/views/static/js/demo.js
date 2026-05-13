async function addTransaction() {
    const amount = document.getElementById("amount").value;
    const description = document.getElementById("description").value;

    if (!amount || !description) {
        showResult("❌ Vui lòng nhập đầy đủ thông tin", "danger");
        return;
    }

    try {
        const res = await fetch("/transactions/add", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                amount: Number(amount),
                description: description
            })
        });

        const data = await res.json();

        showResult(
            `✅ Thêm thành công!<br>
            🆔 ID: ${data.id}<br>
            💰 Số tiền: ${amount} VND<br>
            📝 Mô tả: ${description}<br>
            📂 Phân loại: <b>${data.category}</b>`,
            "success"
        );

    } catch (err) {
        showResult("❌ Lỗi server", "danger");
    }
}


// 👉 Hàm hiển thị thông báo (tái sử dụng)
function showResult(message, type) {
    const resultDiv = document.getElementById("result");

    resultDiv.className = `alert alert-${type} mt-4`;
    resultDiv.classList.remove("d-none");
    resultDiv.innerHTML = message;
}


// 📈 Dự đoán
async function predictExpense() {
    try {
        const res = await fetch("/transactions/predict");
        const data = await res.json();

        showResult(
            `📈 Dự đoán tháng sau:<br>
             💰 <b>${data.predicted_expense} VND</b>`,
            "info"
        );

    } catch (err) {
        showResult("❌ Không thể dự đoán", "danger");
    }
}
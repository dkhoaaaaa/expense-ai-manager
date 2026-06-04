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

document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("authModal");
    const openButtons = document.querySelectorAll(".js-open-auth");
    const closeButtons = document.querySelectorAll(".js-close-auth");
    const tabs = document.querySelectorAll(".auth-tab");
    const panels = document.querySelectorAll(".auth-panel");

    if (!modal || !openButtons.length || !tabs.length || !panels.length) {
        return;
    }

    const setActiveTab = (tabName) => {
        tabs.forEach((tab) => {
            tab.classList.toggle("is-active", tab.dataset.authTab === tabName);
        });

        panels.forEach((panel) => {
            panel.classList.toggle("is-active", panel.dataset.authPanel === tabName);
        });
    };

    const openModal = (tabName = "login") => {
        modal.classList.add("is-open");
        modal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
        setActiveTab(tabName);
    };

    const closeModal = () => {
        modal.classList.remove("is-open");
        modal.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
    };

    openButtons.forEach((button) => {
        button.addEventListener("click", () => {
            openModal(button.dataset.authTab || "login");
        });
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", closeModal);
    });

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            setActiveTab(tab.dataset.authTab || "login");
        });
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && modal.classList.contains("is-open")) {
            closeModal();
        }
    });
});
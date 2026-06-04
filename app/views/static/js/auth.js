document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("container");
    const registerButton = document.getElementById("register");
    const loginButton = document.getElementById("login");

    if (!container || !registerButton || !loginButton) {
        return;
    }

    registerButton.addEventListener("click", () => {
        container.classList.add("active");
        container.classList.remove("close");
    });

    loginButton.addEventListener("click", () => {
        container.classList.add("close");
        container.classList.remove("active");
    });
});
const btn = document.getElementById("themeBtn");

if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark");
    if (btn) btn.innerHTML = "☀️";
}

if (btn) {
    btn.addEventListener("click", function () {

        document.body.classList.toggle("dark");

        if (document.body.classList.contains("dark")) {
            localStorage.setItem("theme", "dark");
            btn.innerHTML = "☀️";
        } else {
            localStorage.setItem("theme", "light");
            btn.innerHTML = "🌙";
        }

    });
}

window.onload = function () {
    document.body.classList.add("loaded");
};
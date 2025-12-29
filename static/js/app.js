"use strict";
(() => {
    const path = window.location.pathname.replace(/\/+$/, "") || "/";
    const links = document.querySelectorAll("a.nav-link");
    links.forEach((link) => {
        const href = (link.getAttribute("href") || "").replace(/\/+$/, "") || "/";
        if (href === path)
            link.classList.add("active");
    });
    const html = document.documentElement;
    const button = document.getElementById("theme-toggle");
    const getStored = () => {
        const t = window.localStorage.getItem("theme");
        return t === "light" || t === "dark" ? t : null;
    };
    const setTheme = (theme) => {
        html.dataset.theme = theme;
        window.localStorage.setItem("theme", theme);
        if (button) {
            const icon = button.querySelector("i");
            if (icon)
                icon.className = theme === "dark" ? "bi bi-sun" : "bi bi-moon-stars";
            button.title = theme === "dark" ? "라이트 테마" : "다크 테마";
        }
    };
    setTheme(getStored() ?? "dark");
    button === null || button === void 0 ? void 0 : button.addEventListener("click", () => {
        const current = html.dataset.theme || "dark";
        setTheme(current === "dark" ? "light" : "dark");
    });
})();

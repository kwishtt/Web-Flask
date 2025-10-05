document.addEventListener("DOMContentLoaded", () => {
    const navToggle = document.querySelector(".nav-toggle");
    const nav = document.querySelector(".primary-nav");

    if (navToggle && nav) {
        navToggle.addEventListener("click", () => {
            nav.classList.toggle("active");
        });
    }

    document.querySelectorAll(".flash-close").forEach((button) => {
        button.addEventListener("click", (event) => {
            event.currentTarget.parentElement.remove();
        });
    });

    setTimeout(() => {
        document.querySelectorAll(".flash").forEach((flash) => {
            flash.classList.add("fade-out");
            flash.addEventListener("transitionend", () => flash.remove(), {
                once: true,
            });
        });
    }, 4000);

    document.querySelectorAll("img[data-fallback]").forEach((img) => {
        img.addEventListener("error", () => {
            const fallback = img.getAttribute("data-fallback");
            if (fallback && img.src !== fallback) {
                img.src = fallback;
            }
        });
    });
});

/* =========================================================
   SILAMBAM - LIQUID GLASS MOUSE EFFECT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const mouseGlow = document.getElementById("mouseGlow");

    if (!mouseGlow) {
        return;
    }

    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;

    let currentX = mouseX;
    let currentY = mouseY;

    document.addEventListener("mousemove", function (event) {

        mouseX = event.clientX;
        mouseY = event.clientY;

        document.body.classList.add("mouse-active");

    });

    document.addEventListener("mouseleave", function () {

        document.body.classList.remove("mouse-active");

    });

    function animateMouseGlow() {

        currentX += (mouseX - currentX) * 0.12;
        currentY += (mouseY - currentY) * 0.12;

        mouseGlow.style.left = currentX + "px";
        mouseGlow.style.top = currentY + "px";

        requestAnimationFrame(animateMouseGlow);
    }

    animateMouseGlow();


    /* =====================================================
       INTERACTIVE GLASS CARDS
       ===================================================== */

    const cards = document.querySelectorAll(
        ".glass, .card, .panel, .stat-card, .management-card, " +
        ".quick-info, .welcome, .date-card, .attendance-box, " +
        ".summary-card, .page-header, .login-box, .login-container"
    );

    cards.forEach(function (card) {

        card.addEventListener("mousemove", function (event) {

            const rect = card.getBoundingClientRect();

            const x =
                ((event.clientX - rect.left) / rect.width) * 100;

            const y =
                ((event.clientY - rect.top) / rect.height) * 100;

            card.style.setProperty(
                "--mouse-x",
                x + "%"
            );

            card.style.setProperty(
                "--mouse-y",
                y + "%"
            );

        });

        card.addEventListener("mouseleave", function () {

            card.style.removeProperty("--mouse-x");
            card.style.removeProperty("--mouse-y");

        });

    });

});
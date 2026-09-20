/* =====================================================
   MOBILE CITY MENU
===================================================== */

function toggleCityMenu() {

    const panel = document.getElementById("cityPanel");
    const button = document.querySelector(".mobile-city-menu-btn");
    const layout = document.querySelector(".city-layout");

    if (!panel || !button) {
        return;
    }

    const isOpen = panel.classList.contains("mobile-open");

    if (isOpen) {

        panel.classList.remove("mobile-open");
        button.classList.remove("active");
        layout.classList.remove("menu-open");

    } else {

        panel.classList.add("mobile-open");
        button.classList.add("active");
        layout.classList.add("menu-open");

    }
}


/* =====================================================
   CLOSE MENU AFTER CLICKING A CITY
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    const cityButtons =
        document.querySelectorAll("#cityPanel .add-city-btn");

    cityButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const panel =
                document.getElementById("cityPanel");

            const menuButton =
                document.querySelector(".mobile-city-menu-btn");

            const layout =
                document.querySelector(".city-layout");

            if (panel) {
                panel.classList.remove("mobile-open");
            }

            if (menuButton) {
                menuButton.classList.remove("active");
            }

            if (layout) {
                layout.classList.remove("menu-open");
            }

        });

    });


    /* =================================================
       CLOSE MENU WHEN CLICKING OUTSIDE
    ================================================= */

    document.addEventListener("click", function (event) {

        const panel =
            document.getElementById("cityPanel");

        const menuButton =
            document.querySelector(".mobile-city-menu-btn");

        const layout =
            document.querySelector(".city-layout");

        if (!panel || !menuButton) {
            return;
        }

        const clickedInsidePanel =
            panel.contains(event.target);

        const clickedMenuButton =
            menuButton.contains(event.target);

        if (
            !clickedInsidePanel &&
            !clickedMenuButton &&
            panel.classList.contains("mobile-open")
        ) {

            panel.classList.remove("mobile-open");
            menuButton.classList.remove("active");

            if (layout) {
                layout.classList.remove("menu-open");
            }

        }

    });


    /* =================================================
       CLOSE MENU WITH ESC
    ================================================= */

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {

            const panel =
                document.getElementById("cityPanel");

            const menuButton =
                document.querySelector(".mobile-city-menu-btn");

            const layout =
                document.querySelector(".city-layout");

            if (panel) {
                panel.classList.remove("mobile-open");
            }

            if (menuButton) {
                menuButton.classList.remove("active");
            }

            if (layout) {
                layout.classList.remove("menu-open");
            }

        }

    });

});

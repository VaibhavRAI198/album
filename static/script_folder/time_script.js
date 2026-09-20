document.addEventListener("DOMContentLoaded", function () {

    const timezoneElement =
        document.getElementById("timezoneName");

    const clockElement =
        document.getElementById("clock");


    let selectedTimezone =
        timezoneElement
            ? timezoneElement.textContent.trim()
            : "Asia/Kolkata";


    if (!selectedTimezone) {
        selectedTimezone = "Asia/Kolkata";
    }


    function updateClock() {

        const now = new Date();

        try {

            const time =
                new Intl.DateTimeFormat(
                    "en-IN",
                    {
                        timeZone: selectedTimezone,

                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",

                        hour12: true
                    }
                ).format(now);


            if (clockElement) {
                clockElement.textContent =
                    " | " + time;
            }

        } catch (error) {

            console.error(
                "Invalid timezone:",
                selectedTimezone,
                error
            );

            if (clockElement) {
                clockElement.textContent =
                    " | --:--:--";
            }
        }
    }


    updateClock();

    setInterval(
        updateClock,
        1000
    );

});

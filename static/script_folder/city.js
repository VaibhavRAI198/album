let galleryImages = [];
let currentImageIndex = 0;


/* =========================================================
   MOVE POPUP TO BODY
   Prevents parent containers from clipping popup
========================================================= */

function movePopupToBody() {

    const popup =
        document.getElementById("imagePopup");

    if (
        popup &&
        popup.parentElement !== document.body
    ) {
        document.body.appendChild(popup);
    }
}


/* =========================================================
   TOGGLE PLACE IMAGES
   Clicking place name hides/shows images
========================================================= */

function togglePlace(element) {

    const card =
        element.closest(".place-card");

    if (!card) {
        return;
    }

    card.classList.toggle("images-hidden");
}


/* =========================================================
   DISABLE DATA CONTAINER SCROLL
========================================================= */

function disableDataContainerScroll() {

    const dataContainer =
        document.querySelector(".data_container");

    if (dataContainer) {

        dataContainer.classList.add(
            "disable-scroll"
        );
    }
}


/* =========================================================
   ENABLE DATA CONTAINER SCROLL
========================================================= */

function enableDataContainerScroll() {

    const dataContainer =
        document.querySelector(".data_container");

    if (dataContainer) {

        dataContainer.classList.remove(
            "disable-scroll"
        );
    }
}


/* =========================================================
   GET CITY NAME
========================================================= */

function getCityName() {

    const cityInput =
        document.querySelector(
            'input[name="city_name"]'
        );

    if (!cityInput) {
        return "";
    }

    return cityInput.value.trim();
}


/* =========================================================
   UPDATE PLACE
========================================================= */

function updatePlace(event, placeIndex) {

    /*
       IMPORTANT:
       Prevent clicking update button
       from triggering togglePlace()
    */

    if (event) {

        event.preventDefault();
        event.stopPropagation();
    }


    const placeCard =
        event.target.closest(".place-card");

    if (!placeCard) {

        console.error(
            "Place card not found."
        );

        return;
    }


    /* -----------------------------------------
       CURRENT PLACE NAME
    ----------------------------------------- */

    const placeTitleElement =
        placeCard.querySelector(
            ".place-title-text"
        );

    if (!placeTitleElement) {

        alert(
            "Place name could not be found."
        );

        return;
    }


    const currentName =
        placeTitleElement.textContent
            .replace("📍", "")
            .trim();


    /* -----------------------------------------
       CURRENT DESCRIPTION
    ----------------------------------------- */

    const descriptionElement =
        placeCard.querySelector(
            ".place-description"
        );

    const currentDescription =
        descriptionElement
            ? descriptionElement.textContent.trim()
            : "";


    /* -----------------------------------------
       NEW PLACE NAME
    ----------------------------------------- */

    const newName =
        prompt(
            "Enter new place name:",
            currentName
        );


    /* User clicked Cancel */

    if (newName === null) {
        return;
    }


    const trimmedName =
        newName.trim();


    if (!trimmedName) {

        alert(
            "Place name cannot be empty."
        );

        return;
    }


    /* -----------------------------------------
       NEW DESCRIPTION
    ----------------------------------------- */

    const newDescription =
        prompt(
            "Enter place description:",
            currentDescription
        );


    /* User clicked Cancel */

    if (newDescription === null) {
        return;
    }


    const trimmedDescription =
        newDescription.trim();


    if (!trimmedDescription) {

        alert(
            "Description cannot be empty."
        );

        return;
    }


    /* -----------------------------------------
       CITY NAME
    ----------------------------------------- */

    const cityName =
        getCityName();


    if (!cityName) {

        alert(
            "City name could not be found."
        );

        return;
    }


    /* -----------------------------------------
       SEND UPDATE REQUEST
    ----------------------------------------- */

    fetch(
        "/update_place",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({

                city_name:
                    cityName,

                place_index:
                    placeIndex,

                place_name:
                    trimmedName,

                description:
                    trimmedDescription

            })
        }
    )

    .then(response => {

        if (!response.ok) {

            throw new Error(
                "Server returned an error."
            );
        }

        return response.json();
    })

    .then(data => {

        if (data.success) {

            /*
               Reload page so all data
               is refreshed from Flask.
            */

            window.location.reload();

        }
        else {

            alert(
                data.message ||
                "Unable to update place."
            );
        }

    })

    .catch(error => {

        console.error(
            "Update place error:",
            error
        );

        alert(
            "Something went wrong while updating the place."
        );

    });
}


/* =========================================================
   DELETE PLACE
========================================================= */

function deletePlace(event, placeIndex) {

    /*
       Prevent togglePlace()
    */

    if (event) {

        event.preventDefault();
        event.stopPropagation();
    }


    const placeCard =
        event.target.closest(".place-card");

    if (!placeCard) {
        return;
    }


    /* -----------------------------------------
       GET PLACE NAME
    ----------------------------------------- */

    const placeTitleElement =
        placeCard.querySelector(
            ".place-title-text"
        );

    let placeName =
        "this place";


    if (placeTitleElement) {

        placeName =
            placeTitleElement.textContent
                .replace("📍", "")
                .trim();
    }


    /* -----------------------------------------
       CONFIRM DELETE
    ----------------------------------------- */

    const confirmed =
        confirm(
            'Are you sure you want to delete "' +
            placeName +
            '"?\n\n' +
            "All images belonging to this place " +
            "will also be removed from the place."
        );


    if (!confirmed) {
        return;
    }


    /* -----------------------------------------
       GET CITY
    ----------------------------------------- */

    const cityName =
        getCityName();


    if (!cityName) {

        alert(
            "City name could not be found."
        );

        return;
    }


    /* -----------------------------------------
       SEND DELETE REQUEST
    ----------------------------------------- */

    fetch(
        "/delete_place",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({

                city_name:
                    cityName,

                place_index:
                    placeIndex

            })
        }
    )

    .then(response => {

        if (!response.ok) {

            throw new Error(
                "Server returned an error."
            );
        }

        return response.json();
    })

    .then(data => {

        if (data.success) {

            window.location.reload();

        }
        else {

            alert(
                data.message ||
                "Unable to delete place."
            );
        }

    })

    .catch(error => {

        console.error(
            "Delete place error:",
            error
        );

        alert(
            "Something went wrong while deleting the place."
        );

    });
}


/* =========================================================
   OPEN IMAGE POPUP
========================================================= */

function openImage(element) {

    const card =
        element.closest(".place-card");

    if (!card) {
        return;
    }


    const images =
        card.querySelectorAll(
            ".place-image"
        );


    galleryImages =
        Array.from(images).map(
            img => img.src
        );


    currentImageIndex =
        Array.from(images).indexOf(
            element
        );


    if (
        currentImageIndex < 0 ||
        galleryImages.length === 0
    ) {
        return;
    }


    /* Move popup to body */

    movePopupToBody();


    /* Set selected image */

    updatePopupImage();


    const popup =
        document.getElementById(
            "imagePopup"
        );


    if (!popup) {
        return;
    }


    /* Show popup */

    popup.style.display = "flex";


    /* Disable body scroll */

    document.body.classList.add(
        "popup-open"
    );


    /* Disable data container */

    disableDataContainerScroll();
}


/* =========================================================
   NEXT IMAGE
========================================================= */

function nextImage(event) {

    if (event) {
        event.stopPropagation();
    }


    if (galleryImages.length <= 1) {
        return;
    }


    currentImageIndex++;


    if (
        currentImageIndex >=
        galleryImages.length
    ) {

        currentImageIndex = 0;
    }


    updatePopupImage();
}


/* =========================================================
   PREVIOUS IMAGE
========================================================= */

function previousImage(event) {

    if (event) {
        event.stopPropagation();
    }


    if (galleryImages.length <= 1) {
        return;
    }


    currentImageIndex--;


    if (currentImageIndex < 0) {

        currentImageIndex =
            galleryImages.length - 1;
    }


    updatePopupImage();
}


/* =========================================================
   UPDATE POPUP IMAGE
========================================================= */

function updatePopupImage() {

    if (galleryImages.length === 0) {
        return;
    }


    const popupImage =
        document.getElementById(
            "popupImage"
        );


    if (!popupImage) {
        return;
    }


    popupImage.src =
        galleryImages[
            currentImageIndex
        ];


    updateImageCounter();
}


/* =========================================================
   IMAGE COUNTER
========================================================= */

function updateImageCounter() {

    const counter =
        document.getElementById(
            "imageCounter"
        );


    if (!counter) {
        return;
    }


    counter.innerText =
        (currentImageIndex + 1) +
        " / " +
        galleryImages.length;
}


/* =========================================================
   CLOSE IMAGE POPUP
========================================================= */

function closeImagePopup(event) {

    if (event) {
        event.stopPropagation();
    }


    const popup =
        document.getElementById(
            "imagePopup"
        );


    if (popup) {

        popup.style.display =
            "none";
    }


    const popupImage =
        document.getElementById(
            "popupImage"
        );


    if (popupImage) {

        popupImage.src = "";
    }


    /* Reset gallery */

    galleryImages = [];

    currentImageIndex = 0;


    /* Restore body scrolling */

    document.body.classList.remove(
        "popup-open"
    );


    /* Restore data container */

    enableDataContainerScroll();
}


/* =========================================================
   KEYBOARD CONTROLS
========================================================= */

document.addEventListener(
    "keydown",
    function(event) {

        const popup =
            document.getElementById(
                "imagePopup"
            );


        if (
            !popup ||
            popup.style.display === "none" ||
            popup.style.display === ""
        ) {
            return;
        }


        if (
            event.key ===
            "ArrowRight"
        ) {

            nextImage(event);

        }
        else if (
            event.key ===
            "ArrowLeft"
        ) {

            previousImage(event);

        }
        else if (
            event.key ===
            "Escape"
        ) {

            closeImagePopup(event);

        }

    }
);


/* =========================================================
   PAGE LOAD
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        movePopupToBody();

    }
);

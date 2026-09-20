const loginOverlay = document.getElementById("loginOverlay");
const loginSection = document.getElementById("loginSection");
const signupSection = document.getElementById("signupSection");
const loginForm = document.getElementById("loginForm");
const signupForm = document.getElementById("signupForm");
const loginError = document.getElementById("loginError");
const signupError = document.getElementById("signupError");
const loginButton = document.getElementById("loginButton");
const signupButton = document.getElementById("signupButton");

function closeLoginPopup() {
    if (loginOverlay) {
        loginOverlay.style.display = "none";
    }

    document.body.classList.remove("login-open");
}

function openLoginPopup() {
    if (!loginOverlay) {
        return;
    }

    loginOverlay.style.display = "flex";
    document.body.classList.add("login-open");

    showLogin();
}

function showLogin() {
    if (loginSection) {
        loginSection.style.display = "block";
    }

    if (signupSection) {
        signupSection.style.display = "none";
    }

    if (loginError) {
        loginError.textContent = "";
        loginError.className = "login-error";
    }

    if (signupError) {
        signupError.textContent = "";
        signupError.className = "login-error";
    }

    if (loginButton) {
        loginButton.disabled = false;
        loginButton.textContent = "Login";
    }
}

function showSignup() {
    if (loginSection) {
        loginSection.style.display = "none";
    }

    if (signupSection) {
        signupSection.style.display = "block";
    }

    if (loginError) {
        loginError.textContent = "";
        loginError.className = "login-error";
    }

    if (signupError) {
        signupError.textContent = "";
        signupError.className = "login-error";
    }

    if (signupButton) {
        signupButton.disabled = false;
        signupButton.textContent = "Create Account";
    }
}

function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);

    if (!input || !button) {
        return;
    }

    if (input.type === "password") {
        input.type = "text";
        button.textContent = "🙈";
    } else {
        input.type = "password";
        button.textContent = "👁";
    }
}

async function checkLoginSession() {
    try {
        const response = await fetch("/check-login", {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store"
        });

        if (!response.ok) {
            openLoginPopup();
            return;
        }

        const data = await response.json();

        if (data.logged_in === true) {
            closeLoginPopup();

            const userNameElement =
                document.getElementById("userName");

            if (userNameElement) {
                userNameElement.textContent =
                    data.user_name || "User";
            }

            const welcomeName =
                document.getElementById("welcomeName");

            if (welcomeName) {
                welcomeName.textContent =
                    data.user_name || "User";
            }

            return;
        }

        openLoginPopup();

    } catch (error) {
        console.error("Session check error:", error);
        openLoginPopup();
    }
}

if (loginForm) {
    loginForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        if (loginError) {
            loginError.textContent = "";
            loginError.className = "login-error";
        }

        const loginInput =
            document.getElementById("loginEmail");

        const passwordInput =
            document.getElementById("loginPassword");

        const login = loginInput
            ? loginInput.value.trim()
            : "";

        const password = passwordInput
            ? passwordInput.value
            : "";

        if (!login || !password) {
            if (loginError) {
                loginError.textContent =
                    "Email/phone and password are required.";

                loginError.className =
                    "login-error error";
            }

            return;
        }

        if (loginButton) {
            loginButton.disabled = true;
            loginButton.textContent = "Logging in...";
        }

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "same-origin",
                cache: "no-store",
                body: JSON.stringify({
                    login: login,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok && data.success === true) {

                if (loginError) {
                    loginError.textContent =
                        data.message || "Login successful.";

                    loginError.className =
                        "login-error success";
                }

                if (loginButton) {
                    loginButton.textContent =
                        "Login Successful ✓";
                }

                setTimeout(function() {
                    window.location.href =
                        data.redirect || "/";
                }, 500);

                return;
            }

            if (loginError) {
                loginError.textContent =
                    data.message ||
                    "Invalid email/phone or password.";

                loginError.className =
                    "login-error error";
            }

            if (loginButton) {
                loginButton.disabled = false;
                loginButton.textContent = "Login";
            }

        } catch (error) {
            console.error("Login error:", error);

            if (loginError) {
                loginError.textContent =
                    "Unable to connect to server.";

                loginError.className =
                    "login-error error";
            }

            if (loginButton) {
                loginButton.disabled = false;
                loginButton.textContent = "Login";
            }
        }
    });
}

if (signupForm) {
    signupForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        if (signupError) {
            signupError.textContent = "";
            signupError.className = "login-error";
        }

        if (signupButton) {
            signupButton.disabled = true;
            signupButton.textContent =
                "Creating Account...";
        }

        const formData = new FormData(signupForm);

        try {
            const response = await fetch("/signup", {
                method: "POST",
                credentials: "same-origin",
                cache: "no-store",
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success === true) {

                if (signupError) {
                    signupError.textContent =
                        data.message ||
                        "Account created successfully.";

                    signupError.className =
                        "login-error success";
                }

                if (signupButton) {
                    signupButton.textContent =
                        "Account Created ✓";
                }

                const registeredEmail =
                    data.user_email || "";

                setTimeout(function() {
                    showLogin();

                    const loginInput =
                        document.getElementById("loginEmail");

                    if (loginInput) {
                        loginInput.value =
                            registeredEmail;
                    }

                    const loginPassword =
                        document.getElementById(
                            "loginPassword"
                        );

                    if (loginPassword) {
                        loginPassword.value = "";
                        loginPassword.focus();
                    }
                }, 1000);

                return;
            }

            if (signupError) {
                signupError.textContent =
                    data.message ||
                    "Unable to create account.";

                signupError.className =
                    "login-error error";
            }

            if (signupButton) {
                signupButton.disabled = false;
                signupButton.textContent =
                    "Create Account";
            }

        } catch (error) {
            console.error("Signup error:", error);

            if (signupError) {
                signupError.textContent =
                    "Unable to connect to server.";

                signupError.className =
                    "login-error error";
            }

            if (signupButton) {
                signupButton.disabled = false;
                signupButton.textContent =
                    "Create Account";
            }
        }
    });
}

async function logoutUser(event) {
    if (event) {
        event.preventDefault();
    }

    try {
        const response = await fetch("/logout", {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store"
        });

        if (response.ok) {
            window.location.href = "/";
            return;
        }

        window.location.href = "/logout";

    } catch (error) {
        console.error("Logout error:", error);
        window.location.href = "/logout";
    }
}

document.addEventListener("DOMContentLoaded", function() {

    const logoutLinks =
        document.querySelectorAll('a[href="/logout"]');

    logoutLinks.forEach(function(link) {
        link.addEventListener("click", logoutUser);
    });

    checkLoginSession();
});

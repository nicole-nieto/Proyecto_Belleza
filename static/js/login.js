/* static/js/login.js */

document.addEventListener("DOMContentLoaded", () => {

    // ==========================
    // SWITCH ENTRE LOGIN/REGISTER
    // ==========================

    const loginBox = document.getElementById("login-box");
    const registerBox = document.getElementById("register-box");
    const toRegister = document.getElementById("to-register");
    const toLogin = document.getElementById("to-login");

    toRegister.addEventListener("click", (e) => {
        e.preventDefault();
        loginBox.classList.add("hidden");
        registerBox.classList.remove("hidden");
    });

    toLogin.addEventListener("click", (e) => {
        e.preventDefault();
        registerBox.classList.add("hidden");
        loginBox.classList.remove("hidden");
    });

    // ==========================
    //   LOGIN
    // ==========================

    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            const resp = await fetch(window.API_BASE + "/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: `username=${email}&password=${password}`
            });

            const data = await resp.json();

            if (!resp.ok) {
                document.getElementById("login-msg").innerText =
                    data.detail || "Error al iniciar sesión";
                return;
            }

            window.saveSession(data.access_token, data.rol);

            window.location.href = "/spas";
        });
    }


    // ==========================
    //   REGISTRO
    // ==========================

    const regForm = document.getElementById("register-form");
    if (regForm) {
        regForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const nombre = document.getElementById("reg-nombre").value;
            const correo = document.getElementById("reg-correo").value;
            const contrasena = document.getElementById("reg-password").value;

            const resp = await fetch(window.API_BASE + "/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nombre, correo, contrasena })
            });

            const data = await resp.json();

            if (!resp.ok) {
                document.getElementById("register-msg").innerText =
                    data.detail || "Error al registrar";
                return;
            }

            document.getElementById("register-msg").style.color = "green";
            document.getElementById("register-msg").innerText = "Registrado correctamente. Ahora puedes iniciar sesión.";

            setTimeout(() => {
                registerBox.classList.add("hidden");
                loginBox.classList.remove("hidden");
            }, 1200);
        });
    }

    window.updateNav();
});

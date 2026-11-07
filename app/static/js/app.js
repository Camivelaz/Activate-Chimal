document.addEventListener("DOMContentLoaded", function () {

    const botonMenu = document.getElementById("menu-toggle");
    const menu = document.getElementById("menu");

    if (botonMenu && menu) {
        botonMenu.addEventListener("click", function () {
            menu.classList.toggle("abierto");
        });
    }

    const fechas = document.querySelectorAll('input[type="date"]');

    fechas.forEach(function (campo) {
        campo.addEventListener("change", function () {
            if (campo.value && campo.min && campo.value < campo.min) {
                campo.value = campo.min;
            }
        });
    });

});
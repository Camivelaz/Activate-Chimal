document.addEventListener("DOMContentLoaded", function () {

    const avatar = document.getElementById("avatar-preview");

    if (avatar) {
        const ropa = document.getElementById("ropa");
        const color = document.getElementById("color");
        const accesorio = document.getElementById("accesorio");

        function actualizarAvatar() {
            avatar.dataset.ropa = ropa.value;
            avatar.dataset.color = color.value;
            avatar.dataset.accesorio = accesorio.value;
        }

        ropa.addEventListener("change", actualizarAvatar);
        color.addEventListener("change", actualizarAvatar);
        accesorio.addEventListener("change", actualizarAvatar);

        actualizarAvatar();
    }

    const selectorFoto = document.getElementById("foto");
    const vistaFoto = document.getElementById("foto-preview");
    const fotoVacia = document.getElementById("foto-vacia");

    if (selectorFoto && vistaFoto) {
        selectorFoto.addEventListener("change", function () {

            const archivo = selectorFoto.files[0];

            if (!archivo) return;

            const formatos = [
                "image/jpeg",
                "image/png",
                "image/webp"
            ];

            if (!formatos.includes(archivo.type)) {
                alert("Selecciona una imagen JPG, PNG o WEBP.");
                selectorFoto.value = "";
                return;
            }

            if (archivo.size > 3 * 1024 * 1024) {
                alert("La imagen no debe superar los 3 MB.");
                selectorFoto.value = "";
                return;
            }

            const lector = new FileReader();

            lector.onload = function (evento) {
                vistaFoto.src = evento.target.result;
                vistaFoto.hidden = false;

                if (fotoVacia) {
                    fotoVacia.hidden = true;
                }
            };

            lector.readAsDataURL(archivo);
        });
    }

});
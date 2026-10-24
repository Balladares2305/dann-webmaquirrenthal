const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector("#site-nav");

menuToggle.addEventListener("click", () => {
  const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
  menuToggle.setAttribute("aria-expanded", String(!isOpen));
  menuToggle.setAttribute("aria-label", isOpen ? "Abrir menú" : "Cerrar menú");
  siteNav.classList.toggle("is-open", !isOpen);
});

siteNav.addEventListener("click", (event) => {
  if (event.target.closest("a")) {
    menuToggle.setAttribute("aria-expanded", "false");
    menuToggle.setAttribute("aria-label", "Abrir menú");
    siteNav.classList.remove("is-open");
  }
});

document.querySelector("#year").textContent = new Date().getFullYear();

const quoteForm = document.querySelector("#quote-form");
const formResult = document.querySelector("#form-result");
let requestText = "";

quoteForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!quoteForm.reportValidity()) return;

  const formData = new FormData(quoteForm);
  const details = formData.get("details").trim();
  requestText = [
    "Hola, quisiera solicitar una cotización de MAQUIRRETHAL.",
    `Nombre: ${formData.get("name").trim()}`,
    `Teléfono: ${formData.get("phone").trim()}`,
    `Equipo: ${formData.get("equipment")}`,
    details ? `Proyecto: ${details}` : "",
  ].filter(Boolean).join("\n");

  formResult.hidden = false;
  formResult.textContent = "";

  if (navigator.share) {
    try {
      await navigator.share({ title: "Cotización MAQUIRRETHAL", text: requestText });
      formResult.textContent = "Solicitud compartida. Gracias por contactarnos.";
      return;
    } catch (error) {
      if (error.name === "AbortError") {
        formResult.textContent = "No se compartió la solicitud. Puedes intentarlo de nuevo o copiar el mensaje.";
      } else {
        formResult.textContent = "No fue posible abrir el menú para compartir. Puedes copiar el mensaje.";
      }
      addCopyButton();
      return;
    }
  }

  formResult.textContent = "Tu solicitud está lista. Cópiala y envíala por tu canal de contacto preferido.";
  addCopyButton();
});

function addCopyButton() {
  const copyButton = document.createElement("button");
  copyButton.className = "copy-request";
  copyButton.type = "button";
  copyButton.textContent = "Copiar solicitud";
  copyButton.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(requestText);
      copyButton.textContent = "Solicitud copiada";
    } catch {
      const textArea = document.createElement("textarea");
      textArea.value = requestText;
      textArea.setAttribute("readonly", "");
      textArea.style.position = "fixed";
      textArea.style.opacity = "0";
      document.body.append(textArea);
      textArea.select();
      const copied = document.execCommand("copy");
      textArea.remove();
      copyButton.textContent = copied ? "Solicitud copiada" : "No se pudo copiar. Selecciona y copia los datos del formulario.";
    }
  });
  formResult.append(copyButton);
}

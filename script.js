const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector("#site-nav");
const equipmentGrid = document.querySelector("#equipment-grid");

const equipmentImages = [
  "imagenes/BACADITO.jpeg",
  "imagenes/compresor motor.jpeg",
  "imagenes/compresor.jpeg",
  "imagenes/concretera.jpeg",
  "imagenes/demoledor compresor.jpeg",
  "imagenes/demoledor .jpeg",
  "imagenes/DWE4577_1_1.jpg",
  "imagenes/generador1.jpeg",
  "imagenes/generador2.jpg",
  "imagenes/images.jpeg",
  "imagenes/luminarias.jpeg",
  "imagenes/MNTACARGAS.png",
  "imagenes/moladoras.jpeg",
  "imagenes/rotomartillo.jpeg",
  "imagenes/soldadora 1.webp",
  "imagenes/soldadora elite.jpeg",
  "imagenes/soldadora inco.jpeg",
  "imagenes/torre de iluminacion a paneles .jpeg"
];

function normalizeTitle(value) {
  return value
    .replace(/\.[^/.]+$/, "")
    .replace(/[-_]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function renderEquipmentCards() {
  if (!equipmentGrid) return;

  equipmentGrid.innerHTML = "";

  equipmentImages.forEach((imagePath, index) => {
    const article = document.createElement("article");
    article.className = "equipment-card";
    if (index === 0) article.classList.add("equipment-card-featured");

    const title = normalizeTitle(imagePath.split("/").pop());
    const kicker = index % 2 === 0 ? "POTENCIA Y PRECISIÓN" : "SOLUCIÓN EN OBRA";
    const shortName = title.length > 25 ? `${title.slice(0, 25)}...` : title;

    article.innerHTML = `
      <div class="card-visual" data-image-slot>
        <span class="card-number">/ ${shortName.toUpperCase()}</span>
        <img class="custom-photo" src="${imagePath}" alt="${shortName}">
        <svg viewBox="0 0 320 185" aria-hidden="true">
          <path d="m170 65 54-45 17 9-44 51zM231 29l40-23 13 11-39 27z" fill="#f5b72c" stroke="#1b1d19" stroke-width="7" stroke-linejoin="round"></path>
          <path d="M79 118c0-17 14-31 31-31h102c17 0 31 14 31 31v23c0 16-13 29-29 29h-106c-16 0-29-13-29-29z" fill="#252924" stroke="#111" stroke-width="7"></path>
          <circle cx="120" cy="141" r="11" fill="#9c998e"></circle><circle cx="157" cy="141" r="11" fill="#9c998e"></circle><circle cx="194" cy="141" r="11" fill="#9c998e"></circle>
          <path d="m91 94 27-57c5-10 15-17 27-17h42c13 0 23 10 23 23v53l20 18H82z" fill="#f5b72c" stroke="#1b1d19" stroke-width="7" stroke-linejoin="round"></path>
          <path d="m137 27-20 50h51V40c0-7-6-13-13-13z" fill="#39423d" stroke="#1b1d19" stroke-width="5"></path>
          <path d="M81 95h151l17 22H70z" fill="#edaa22" stroke="#1b1d19" stroke-width="6"></path>
        </svg>
      </div>
      <div class="card-copy">
        <div><p class="card-kicker">${kicker}</p><h3>${shortName}</h3></div>
        <span class="card-arrow" aria-hidden="true">↗</span>
        <p>Maquinaria disponible para apoyar tu proyecto con eficiencia y seguridad.</p>
      </div>
    `;

    equipmentGrid.appendChild(article);
  });

  document.querySelectorAll("[data-image-slot]").forEach((slot) => {
    const image = slot.querySelector(".custom-photo");
    if (!image) return;

    const showImage = () => slot.classList.add("has-custom-image");
    image.addEventListener("load", showImage, { once: true });
    image.addEventListener("error", () => image.remove(), { once: true });

    if (image.complete && image.naturalWidth > 0) showImage();
  });
}

if (menuToggle) {
  menuToggle.addEventListener("click", () => {
    const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Abrir menú" : "Cerrar menú");
    siteNav.classList.toggle("is-open", !isOpen);
  });
}

if (siteNav) {
  siteNav.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      menuToggle.setAttribute("aria-expanded", "false");
      menuToggle.setAttribute("aria-label", "Abrir menú");
      siteNav.classList.remove("is-open");
    }
  });
}

document.querySelector("#year").textContent = new Date().getFullYear();
renderEquipmentCards();

const heroImage = document.querySelector(".hero-art .custom-photo");
if (heroImage) {
  const heroImages = [
    "imagenes/BACADITO.jpeg",
    "imagenes/compresor motor.jpeg",
    "imagenes/compresor.jpeg",
    "imagenes/concretera.jpeg",
    "imagenes/demoledor compresor.jpeg",
    "imagenes/demoledor .jpeg",
    "imagenes/DWE4577_1_1.jpg",
    "imagenes/generador1.jpeg",
    "imagenes/generador2.jpg",
    "imagenes/images.jpeg",
    "imagenes/luminarias.jpeg",
    "imagenes/MNTACARGAS.png",
    "imagenes/moladoras.jpeg",
    "imagenes/rotomartillo.jpeg",
    "imagenes/soldadora 1.webp",
    "imagenes/soldadora elite.jpeg",
    "imagenes/soldadora inco.jpeg",
    "imagenes/torre de iluminacion a paneles .jpeg"
  ];

  let heroImageIndex = heroImages.indexOf(heroImage.getAttribute("src") || "");
  if (heroImageIndex === -1) heroImageIndex = 0;

  setInterval(() => {
    heroImageIndex = (heroImageIndex + 1) % heroImages.length;
    heroImage.src = heroImages[heroImageIndex];
    heroImage.alt = "Maquinaria pesada en una obra";
    heroImage.loading = "eager";
    const heroSlot = heroImage.closest("[data-image-slot]");
    if (heroSlot) heroSlot.classList.add("has-custom-image");
  }, 2000);
}

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

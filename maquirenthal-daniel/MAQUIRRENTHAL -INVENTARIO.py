import customtkinter as ctk
from tkinter import Canvas, Label, PhotoImage, ttk, filedialog, messagebox
from datetime import datetime
import json
import os
import sys

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if getattr(sys, "frozen", False):
    carpeta_datos = os.getenv("APPDATA") or os.path.expanduser("~")
    carpeta_datos = os.path.join(carpeta_datos, "MAQUIRRETHAL")
    os.makedirs(carpeta_datos, exist_ok=True)
    ARCHIVO_DATOS = os.path.join(carpeta_datos, "inventario_renta.json")
else:
    ARCHIVO_DATOS = "inventario_renta.json"
IVA = 0.15
EMPRESA = "MAQUIRRETHAL S.A"

FUENTE_NORMAL = ("Arial", 16)
FUENTE_BOLD   = ("Arial", 16, "bold")
FUENTE_TITULO = ("Arial", 18, "bold")
FUENTE_TABLA  = ("Arial", 14)
FUENTE_TOTAL  = ("Arial", 20, "bold")   # 👈 Rojo y grande para TOTAL NETO A CANCELAR


# =========================================================
# PERSISTENCIA
# =========================================================
def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def guardar_datos(datos):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


# =========================================================
# GPS
# =========================================================
def obtener_gps():
    try:
        import geocoder
        g = geocoder.ip('me')
        if g.latlng:
            return f"{g.latlng[0]:.6f}, {g.latlng[1]:.6f}"
    except Exception:
        pass
    return "No disponible"


# =========================================================
# APLICACIÓN PRINCIPAL
# =========================================================
class AppRentaMaquinaria(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{EMPRESA} - Control de Inventario y Renta de Maquinaria")
        self.geometry("1350x850")
        self.minsize(1200, 750)

        self.datos = cargar_datos()
        self.contrato_seleccionado = None
        self.ruta_foto_entrega = ""
        self.trazos_firma_entrega = []
        self.parpadeo_estado = False

        self._construir_ui()
        self.after(800, self._loop_parpadeo)
        self.after(1000, self._verificar_alertas)

    # =====================================================
    # UI PRINCIPAL
    # =====================================================
    def _construir_ui(self):
        header = ctk.CTkFrame(self, fg_color="#0d47a1", height=248)
        header.pack(fill="x", padx=10, pady=(4, 0))
        header.pack_propagate(False)
        ruta_banner = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "empresa_banner.png",
        )
        self.logo_empresa = PhotoImage(file=ruta_banner)
        Label(
            header,
            image=self.logo_empresa,
            bg="white",
            borderwidth=0,
        ).pack(fill="x")
        ctk.CTkLabel(
            header,
            text=f"🏗  {EMPRESA}  |  SISTEMA DE RENTA DE MAQUINARIA",
            font=FUENTE_TITULO, text_color="white",
        ).pack(fill="x", pady=0)

        self.banner = ctk.CTkFrame(self, fg_color="transparent")

        self.tabs = ctk.CTkTabview(self, width=1300, height=720)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        self.tab_form = self.tabs.add("📝 Formulario de Registro")
        self.tab_tabla = self.tabs.add("📊 Tabla de Contratos")

        self._construir_formulario(self.tab_form)
        self._construir_tabla(self.tab_tabla)

    # =====================================================
    # FORMULARIO
    # =====================================================
    def _construir_formulario(self, parent):
        self.contenedor = ctk.CTkScrollableFrame(parent)
        self.contenedor.pack(fill="both", expand=True, padx=5, pady=5)
        self._activar_scroll_mouse(self.contenedor)

        # 1) DATOS DEL CLIENTE
        self._seccion(self.contenedor, "👤 Datos del Cliente")
        f0 = self._frame_grid(self.contenedor)
        self.entry_cliente = self._campo(f0, "Nombre del cliente:", 0, 0)
        self.entry_cedula = self._campo(f0, "Cédula:", 0, 2)
        self.entry_telefono = self._campo(f0, "Teléfono:", 1, 0)
        self.entry_correo = self._campo(f0, "Correo electrónico:", 1, 2)
        self.entry_area = self._campo(f0, "Área / lugar de uso:", 2, 0)

        # 2) IDENTIFICACIÓN DEL EQUIPO
        self._seccion(self.contenedor, "🔧 Identificación del Equipo")
        f1 = self._frame_grid(self.contenedor)
        self.entry_nombre = self._campo(f1, "Nombre del equipo:", 0, 0)
        self.entry_serie = self._campo(f1, "Serie del equipo:", 0, 2)
        self.entry_cantidad = self._campo(f1, "Cantidad de equipos:", 1, 0)
        self.entry_horometro_ini = self._campo(f1, "Horómetro inicial motor:", 1, 2)

        # 3) DATOS FINANCIEROS
        self._seccion(self.contenedor, "💰 Datos Financieros")
        f2 = self._frame_grid(self.contenedor)
        self.entry_horas = self._campo(f2, "Horas contratadas:", 0, 0)
        self.entry_precio = self._campo(f2, "Precio por hora:", 0, 2)
        self.entry_garantia = self._campo(f2, "Garantía / Depósito:", 1, 0)

        ctk.CTkLabel(f2, text="Método de Pago:", font=FUENTE_NORMAL).grid(
            row=1, column=2, sticky="w", padx=6, pady=4
        )
        self.combo_pago = ctk.CTkOptionMenu(
            f2, values=["Efectivo", "Transferencia", "Tarjeta", "Crédito interno"],
            font=FUENTE_NORMAL, dropdown_font=FUENTE_NORMAL,
        )
        self.combo_pago.grid(row=1, column=3, sticky="ew", padx=6, pady=4)

        self.entry_subtotal = self._campo(f2, "Subtotal (Horas × Precio):", 2, 0)
        self.entry_iva = self._campo(f2, "IVA 15%:", 2, 2)

        # 👇 TOTAL NETO A CANCELAR (rojo y negrita)
        ctk.CTkLabel(
            f2, text="TOTAL NETO A CANCELAR:", font=FUENTE_TOTAL, text_color="#ff1744"
        ).grid(row=3, column=0, sticky="w", padx=6, pady=6)
        self.entry_total = ctk.CTkEntry(f2, font=FUENTE_TOTAL, text_color="#ff1744")
        self.entry_total.grid(row=3, column=1, sticky="ew", padx=6, pady=6)

        for e in (self.entry_subtotal, self.entry_iva, self.entry_total):
            e.configure(state="readonly")

        self.entry_horas.bind("<KeyRelease>", self._calcular_total)
        self.entry_precio.bind("<KeyRelease>", self._calcular_total)

        # 4) FECHAS Y CONTROL TÉCNICO
        self._seccion(self.contenedor, "📅 Fechas y Control Técnico")
        f4 = self._frame_grid(self.contenedor)
        self.entry_fecha_entrega = self._campo(f4, "Fecha/Hora entrega (YYYY-MM-DD HH:MM):", 0, 0)
        self.entry_fecha_max = self._campo(f4, "Fecha/Hora máx. devolución:", 0, 2)
        self._auto_fecha_entrega()

        ctk.CTkLabel(f4, text="Nivel de combustible:", font=FUENTE_NORMAL).grid(
            row=1, column=0, sticky="w", padx=6, pady=4
        )
        self.combo_combustible = ctk.CTkOptionMenu(
            f4, values=["Full", "1/2", "1/4"], font=FUENTE_NORMAL, dropdown_font=FUENTE_NORMAL,
        )
        self.combo_combustible.grid(row=1, column=1, sticky="ew", padx=6, pady=4)

        self.var_mantenimiento = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            f4, text="⚠ Alerta de mantenimiento (>250 h desde último servicio)",
            variable=self.var_mantenimiento, font=FUENTE_NORMAL,
        ).grid(row=1, column=2, columnspan=2, sticky="w", padx=6, pady=4)

        # 5) ESTADO DE ENTREGA (único que queda)
        self._seccion(self.contenedor, "🔍 Estado de Entrega del Equipo")
        ctk.CTkLabel(
            self.contenedor, text="Estado al ENTREGAR:", font=FUENTE_NORMAL
        ).pack(anchor="w", padx=6)
        self.txt_estado_entrega = ctk.CTkTextbox(self.contenedor, height=90, font=FUENTE_NORMAL)
        self.txt_estado_entrega.pack(fill="x", padx=6, pady=(0, 6))

        # 6) RESPONSABLE Y FIRMA DE ENTREGA
        self._seccion(self.contenedor, "✍️ Responsable y Firma de Entrega")
        self.entry_entregado_por = ctk.CTkEntry(
            self.contenedor, font=FUENTE_NORMAL,
            placeholder_text="Nombre de quien entrega el equipo",
        )
        self.entry_entregado_por.pack(fill="x", padx=6, pady=(0, 8))
        self.canvas_firma_entrega = Canvas(
            self.contenedor, height=140, bg="white", cursor="crosshair",
            highlightthickness=1, highlightbackground="#888888",
        )
        self.canvas_firma_entrega.pack(fill="x", padx=6, pady=(0, 6))
        self.canvas_firma_entrega.bind("<Button-1>", self._iniciar_trazo_firma)
        self.canvas_firma_entrega.bind("<B1-Motion>", self._dibujar_trazo_firma)
        ctk.CTkButton(
            self.contenedor, text="🧹 Limpiar firma", width=150,
            font=FUENTE_NORMAL, command=self._limpiar_firma_entrega,
        ).pack(anchor="w", padx=6, pady=(0, 8))

        # 7) FOTO DE ENTREGA
        self._seccion(self.contenedor, "📷 Registro Fotográfico (Entrega)")
        f6 = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        f6.pack(fill="x", pady=4)

        self.btn_foto_entrega = ctk.CTkButton(
            f6, text="📎 Adjuntar Foto de Entrega",
            font=FUENTE_NORMAL, command=self._adjuntar_foto_entrega,
        )
        self.btn_foto_entrega.pack(side="left", padx=6, pady=6)
        self.lbl_foto_entrega = ctk.CTkLabel(f6, text="Sin imagen", text_color="gray", font=FUENTE_NORMAL)
        self.lbl_foto_entrega.pack(side="left", padx=6)

        # 8) BOTONES OPERATIVOS
        f7 = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        f7.pack(fill="x", pady=18)

        ctk.CTkButton(
            f7, text="📥 Registrar Nueva Renta", width=230, height=45, font=FUENTE_BOLD,
            fg_color="#1f6aa5", hover_color="#144870", command=self._registrar_renta,
        ).pack(side="left", padx=8)

        self.btn_actualizar = ctk.CTkButton(
            f7, text="🔄 Registrar Devolución", width=250, height=45, font=FUENTE_BOLD,
            fg_color="#2e7d32", hover_color="#1b5e20",
            command=self._abrir_ventana_devolucion,
        )
        self.btn_actualizar.pack(side="left", padx=8)

        self.btn_movilizacion = ctk.CTkButton(
            f7, text="🚚 Movilización", width=190, height=45, font=FUENTE_BOLD,
            fg_color="#ef6c00", hover_color="#b34700",
            command=self._abrir_movilizacion, state="disabled",
        )
        self.btn_movilizacion.pack(side="left", padx=8)

        ctk.CTkButton(
            f7, text="🧹 Limpiar Campos", width=190, height=45, font=FUENTE_BOLD,
            fg_color="#8e24aa", hover_color="#5e1275", command=self._limpiar_campos,
        ).pack(side="left", padx=8)

    # =====================================================
    # TABLA
    # =====================================================
    def _construir_tabla(self, parent):
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.pack(fill="x", padx=6, pady=(6, 4))

        ctk.CTkLabel(top, text="🔎 Búsqueda rápida (Cédula / Serie):", font=FUENTE_NORMAL).pack(
            side="left", padx=6
        )
        self.entry_busqueda = ctk.CTkEntry(
            top, width=340, placeholder_text="Escriba para filtrar...", font=FUENTE_NORMAL
        )
        self.entry_busqueda.pack(side="left", padx=6)
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self._refrescar_tabla())

        ctk.CTkButton(
            top, text="↻ Refrescar", width=130, font=FUENTE_NORMAL, command=self._refrescar_tabla,
        ).pack(side="left", padx=6)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Treeview", background="#2b2b2b", foreground="white",
            fieldbackground="#2b2b2b", rowheight=34, font=FUENTE_TABLA,
        )
        estilo.configure("Treeview.Heading", background="#1f6aa5", foreground="white",
                         font=("Arial", 14, "bold"))

        columnas = (
            "ID", "Equipo", "Serie", "Cliente", "Cédula",
            "Entrega", "Máx. Dev.", "Horas", "Total", "Estado",
        )
        self.tabla = ttk.Treeview(parent, columns=columnas, show="headings", height=16)
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=120, anchor="center")

        self.tabla.pack(fill="both", expand=True, padx=6, pady=6)
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar_contrato)
        self._refrescar_tabla()

    # =====================================================
    # SCROLL MOUSE
    # =====================================================
    def _activar_scroll_mouse(self, scrollable_frame):
        try:
            canvas = scrollable_frame._parent_canvas
        except AttributeError:
            return

        def _on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel_linux(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        def _bind_all(_):
            scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)
            scrollable_frame.bind_all("<Button-4>", _on_mousewheel_linux)
            scrollable_frame.bind_all("<Button-5>", _on_mousewheel_linux)

        def _unbind_all(_):
            scrollable_frame.unbind_all("<MouseWheel>")
            scrollable_frame.unbind_all("<Button-4>")
            scrollable_frame.unbind_all("<Button-5>")

        scrollable_frame.bind("<Enter>", _bind_all)
        scrollable_frame.bind("<Leave>", _unbind_all)

    # =====================================================
    # HELPERS UI
    # =====================================================
    def _seccion(self, parent, titulo):
        ctk.CTkLabel(
            parent, text=titulo, font=FUENTE_TITULO, text_color="#4fc3f7"
        ).pack(anchor="w", padx=6, pady=(16, 4))

    def _frame_grid(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=6, pady=4)
        for i in range(4):
            f.grid_columnconfigure(i, weight=1)
        return f

    def _campo(self, parent, etiqueta, fila, col):
        ctk.CTkLabel(parent, text=etiqueta, font=FUENTE_NORMAL).grid(
            row=fila, column=col, sticky="w", padx=6, pady=4
        )
        entry = ctk.CTkEntry(parent, font=FUENTE_NORMAL)
        entry.grid(row=fila, column=col + 1, sticky="ew", padx=6, pady=4)
        return entry

    def _auto_fecha_entrega(self):
        self.entry_fecha_entrega.delete(0, "end")
        self.entry_fecha_entrega.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))

    # =====================================================
    # CÁLCULOS
    # =====================================================
    def _calcular_total(self, event=None):
        try:
            horas = float(self.entry_horas.get() or 0)
            precio = float(self.entry_precio.get() or 0)
            subtotal = horas * precio
            iva = subtotal * IVA
            total = subtotal + iva

            for entry, valor in (
                (self.entry_subtotal, subtotal),
                (self.entry_iva, iva),
                (self.entry_total, total),
            ):
                entry.configure(state="normal")
                entry.delete(0, "end")
                entry.insert(0, f"{valor:.2f}")
                entry.configure(state="readonly")
        except ValueError:
            pass

    # =====================================================
    # FOTO DE ENTREGA
    # =====================================================
    def _adjuntar_foto_entrega(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto de entrega",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif")],
        )
        if ruta:
            self.ruta_foto_entrega = ruta
            self.lbl_foto_entrega.configure(text=os.path.basename(ruta), text_color="#81c784")

    # =====================================================
    # VENTANA DE DEVOLUCIÓN (NUEVA)
    # =====================================================
    def _abrir_ventana_devolucion(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("🔄 Registrar Devolución")
        self.update_idletasks()
        ancho_principal = self.winfo_width()
        alto_principal = self.winfo_height()
        ancho = max(600, int(ancho_principal * 0.75))
        alto = max(450, int(alto_principal * 0.75))
        x = self.winfo_rootx() + (ancho_principal - ancho) // 2
        y = self.winfo_rooty() + (alto_principal - alto) // 2
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
        ventana.grab_set()

        contenido = ctk.CTkScrollableFrame(ventana, orientation="vertical")
        contenido.pack(fill="both", expand=True, padx=8, pady=8)
        self._activar_scroll_mouse(contenido)

        ctk.CTkLabel(
            contenido, text="🔄 Registrar Devolución de Equipo",
            font=FUENTE_TITULO, text_color="#4fc3f7",
        ).pack(pady=14)

        # ---- Buscador ----
        frame_busq = ctk.CTkFrame(contenido, fg_color="transparent")
        frame_busq.pack(fill="x", padx=20, pady=6)

        ctk.CTkLabel(
            frame_busq,
            text="Buscar por ID de contrato, cliente, cédula o serie del equipo:",
            font=FUENTE_NORMAL,
        ).pack(anchor="w")

        frame_input = ctk.CTkFrame(contenido, fg_color="transparent")
        frame_input.pack(fill="x", padx=20, pady=6)

        entry_buscar_dev = ctk.CTkEntry(
            frame_input, font=FUENTE_NORMAL,
            placeholder_text="ID / nombre / cédula / serie",
        )
        entry_buscar_dev.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # ---- Resultado (scrollable) ----
        resultado_frame = ctk.CTkFrame(contenido, fg_color="transparent")
        resultado_frame.pack(fill="x", padx=20, pady=10)

        # Variables para guardar el contrato encontrado
        contrato_encontrado = {"valor": None}

        def render_detalle(c):
            for w in resultado_frame.winfo_children():
                w.destroy()

            if not c:
                ctk.CTkLabel(
                    resultado_frame, text="❌ No se encontró ningún contrato.",
                    font=FUENTE_BOLD, text_color="#ef5350",
                ).pack(pady=20)
                contrato_encontrado["valor"] = None
                return

            contrato_encontrado["valor"] = c

            def fila(label, valor):
                f = ctk.CTkFrame(resultado_frame, fg_color="transparent")
                f.pack(fill="x", pady=2)
                ctk.CTkLabel(f, text=f"{label}", font=FUENTE_BOLD,
                             text_color="#4fc3f7", width=240, anchor="w").pack(side="left")
                ctk.CTkLabel(f, text=str(valor), font=FUENTE_NORMAL, anchor="w").pack(side="left")

            # ---- Datos del contrato ----
            ctk.CTkLabel(
                resultado_frame,
                text=f"📄 Contrato #{c['id']} - {c['estado_contrato']}",
                font=FUENTE_TITULO, text_color="#81c784",
            ).pack(anchor="w", pady=(0, 8))

            fila("Equipo:", c["equipo"])
            fila("Serie:", c["serie"])
            fila("Cantidad:", c["cantidad"])
            fila("Horómetro inicial:", c["horometro_inicial"])
            fila("Horas contratadas:", c["horas_contratadas"])
            fila("Precio por hora:", f"${c['precio_hora']:.2f}")
            fila("Garantía:", f"${c['garantia']:.2f}")
            fila("Método de pago:", c["metodo_pago"])
            fila("Subtotal:", f"${c['subtotal']:.2f}")
            fila("IVA 15%:", f"${c['iva']:.2f}")
            fila("TOTAL A CANCELAR:", f"${c['total']:.2f}")
            fila("Cliente:", c["cliente"])
            fila("Cédula:", c["cedula"])
            fila("Teléfono:", c["telefono"])
            fila("Correo:", c["correo"])
            fila("Área de uso:", c["area"])
            fila("Fecha entrega:", c["fecha_entrega"])
            fila("Fecha máx. devolución:", c["fecha_max_devolucion"])
            fila("Combustible:", c["nivel_combustible"])
            fila("Entregado por:", c.get("quien_entrega") or "—")
            fila(
                "Justificación de entrega vencida:",
                c.get("justificacion_vencimiento") or "—",
            )
            firma = c.get("firma_entrega") or []
            if firma:
                lienzo_firma = Canvas(
                    resultado_frame, width=700, height=120, bg="white",
                    highlightthickness=1, highlightbackground="#888888",
                )
                lienzo_firma.pack(fill="x", pady=4)
                for trazo in firma:
                    if len(trazo) >= 4:
                        lienzo_firma.create_line(
                            *trazo, fill="#111111", width=2, capstyle="round",
                            smooth=True,
                        )
            else:
                fila("Firma de quien entrega:", "Sin registrar")
            fila("Horómetro final:", c.get("horometro_final") or "—")
            fila("Horas que estuvo activo:", f"{c.get('horas_uso_real', 0):.2f} h")
            fila("Combustible al devolver:", c.get("nivel_combustible_devolucion") or "—")
            fila("Recibido por:", c.get("recibido_por") or "—")
            fila("Entregado por al devolver:", c.get("quien_entrega_devolucion") or "—")
            firma_devolucion = c.get("firma_devolucion") or []
            if firma_devolucion:
                lienzo_firma_devolucion = Canvas(
                    resultado_frame, width=700, height=120, bg="white",
                    highlightthickness=1, highlightbackground="#888888",
                )
                lienzo_firma_devolucion.pack(fill="x", pady=4)
                for trazo in firma_devolucion:
                    if len(trazo) >= 4:
                        lienzo_firma_devolucion.create_line(
                            *trazo, fill="#111111", width=2, capstyle="round",
                            smooth=True,
                        )
            else:
                fila("Firma de quien entrega al devolver:", "Sin registrar")
            fila("Alerta mantenimiento:", "Sí" if c["alerta_mantenimiento"] else "No")
            fila("Estado al ENTREGAR:", c["estado_entrega"] or "—")
            fila("Estado al DEVOLVER:", c.get("estado_devuelto") or "—")
            fila("Foto entrega:", c.get("foto_entrega") or "—")
            fila("Foto recepción:", c.get("foto_recepcion") or "—")

            mov = c.get("movilizacion") or {}
            fila("Kilometraje inicial:", mov.get("km_inicial", "—"))
            fila("Kilometraje final:", mov.get("km_final", "—"))
            fila("GPS inicio:", mov.get("gps_inicio", "—"))
            fila("GPS fin:", mov.get("gps_fin", "—"))

        def buscar(*_):
            texto = entry_buscar_dev.get().strip().lower()
            if not texto:
                render_detalle(None)
                return

            for c in self.datos:
                coincide_id = str(c["id"]) == texto
                coincide_cliente = texto in c["cliente"].lower()
                coincide_cedula = texto in str(c["cedula"]).lower()
                coincide_serie = texto in c["serie"].lower()

                if coincide_id or coincide_cliente or coincide_cedula or coincide_serie:
                    render_detalle(c)
                    actualizar_horas_uso()
                    return

            render_detalle(None)
            actualizar_horas_uso()

        entry_buscar_dev.bind("<KeyRelease>", buscar)
        ctk.CTkButton(
            frame_input, text="🔎 Buscar", width=120, font=FUENTE_BOLD,
            fg_color="#1f6aa5", hover_color="#144870", command=buscar,
        ).pack(side="left")

        # ---- Acciones de cierre ----
        ctk.CTkLabel(
            contenido, text="Horómetro final:", font=FUENTE_NORMAL
        ).pack(anchor="w", padx=20, pady=(8, 0))
        entry_horometro_final = ctk.CTkEntry(
            contenido, font=FUENTE_NORMAL, placeholder_text="Lectura al recibir el equipo"
        )
        entry_horometro_final.pack(fill="x", padx=20, pady=(0, 6))
        label_horas_uso = ctk.CTkLabel(
            contenido, text="Horas que estuvo activo: —",
            font=FUENTE_BOLD, text_color="#ff1744",
        )
        label_horas_uso.pack(anchor="w", padx=20, pady=(0, 8))
        trazos_firma_devolucion = []

        def actualizar_horas_uso(_event=None):
            contrato = contrato_encontrado["valor"]
            try:
                horometro_final = float(entry_horometro_final.get().strip())
                horometro_inicial = float(contrato["horometro_inicial"])
                horas_uso = horometro_final - horometro_inicial
                if horas_uso < 0:
                    raise ValueError
            except (TypeError, ValueError, KeyError):
                label_horas_uso.configure(text="Horas que estuvo activo: —")
                return
            label_horas_uso.configure(
                text=f"Horas que estuvo activo: {horas_uso:.2f} h"
            )

        entry_horometro_final.bind("<KeyRelease>", actualizar_horas_uso)

        ctk.CTkLabel(
            contenido, text="Nivel del combustible al devolver:", font=FUENTE_NORMAL
        ).pack(anchor="w", padx=20)
        combo_combustible_devolucion = ctk.CTkOptionMenu(
            contenido, values=["Seleccione...", "Full", "1/2", "1/4"],
            font=FUENTE_NORMAL, dropdown_font=FUENTE_NORMAL,
        )
        combo_combustible_devolucion.set("Seleccione...")
        combo_combustible_devolucion.pack(fill="x", padx=20, pady=(0, 6))

        ctk.CTkLabel(
            contenido, text="Quién recibe el equipo:", font=FUENTE_NORMAL
        ).pack(anchor="w", padx=20)
        entry_recibido_por = ctk.CTkEntry(
            contenido, font=FUENTE_NORMAL, placeholder_text="Nombre de quien recibe"
        )
        entry_recibido_por.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkLabel(
            contenido, text="Quién entrega el equipo:", font=FUENTE_NORMAL
        ).pack(anchor="w", padx=20)
        entry_entrega_devolucion = ctk.CTkEntry(
            contenido, font=FUENTE_NORMAL,
            placeholder_text="Nombre de quien devuelve el equipo",
        )
        entry_entrega_devolucion.pack(fill="x", padx=20, pady=(0, 6))

        ctk.CTkLabel(
            contenido, text="Firma de quien entrega el equipo:", font=FUENTE_NORMAL
        ).pack(anchor="w", padx=20)
        canvas_firma_devolucion = Canvas(
            contenido, height=110, bg="white", cursor="crosshair",
            highlightthickness=1, highlightbackground="#888888",
        )
        canvas_firma_devolucion.pack(fill="x", padx=20, pady=(0, 4))

        def iniciar_trazo_devolucion(event):
            trazos_firma_devolucion.append([event.x, event.y])

        def dibujar_trazo_devolucion(event):
            if not trazos_firma_devolucion:
                return
            trazo = trazos_firma_devolucion[-1]
            x_anterior, y_anterior = trazo[-2:]
            canvas_firma_devolucion.create_line(
                x_anterior, y_anterior, event.x, event.y,
                fill="#111111", width=2, capstyle="round", smooth=True,
            )
            trazo.extend((event.x, event.y))

        def limpiar_firma_devolucion():
            trazos_firma_devolucion.clear()
            canvas_firma_devolucion.delete("all")

        canvas_firma_devolucion.bind("<Button-1>", iniciar_trazo_devolucion)
        canvas_firma_devolucion.bind("<B1-Motion>", dibujar_trazo_devolucion)
        ctk.CTkButton(
            contenido, text="🧹 Limpiar firma", width=150, font=FUENTE_NORMAL,
            command=limpiar_firma_devolucion,
        ).pack(anchor="w", padx=20, pady=(0, 8))

        ctk.CTkLabel(
            contenido, text="Estado al DEVOLVER (obligatorio):", font=FUENTE_NORMAL
        ).pack(anchor="w", padx=20, pady=(10, 0))
        txt_estado_dev = ctk.CTkTextbox(contenido, height=90, font=FUENTE_NORMAL)
        txt_estado_dev.pack(fill="x", padx=20, pady=(0, 6))

        ruta_foto_recepcion = {"valor": ""}
        lbl_foto = ctk.CTkLabel(contenido, text="Sin imagen", text_color="gray", font=FUENTE_NORMAL)
        lbl_foto.pack(anchor="w", padx=20)

        def adjuntar_foto():
            ruta = filedialog.askopenfilename(
                title="Seleccionar foto de recepción",
                filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif")],
            )
            if ruta:
                ruta_foto_recepcion["valor"] = ruta
                lbl_foto.configure(text=os.path.basename(ruta), text_color="#81c784")

        ctk.CTkButton(
            contenido, text="📎 Adjuntar Foto de Recepción", font=FUENTE_NORMAL,
            command=adjuntar_foto,
        ).pack(anchor="w", padx=20, pady=6)

        def confirmar_devolucion():
            c = contrato_encontrado["valor"]
            if c is None:
                messagebox.showwarning("Sin contrato", "Busque y seleccione un contrato primero.")
                return
            if c["estado_contrato"] == "Finalizado":
                messagebox.showinfo("Ya finalizado", "Este contrato ya fue finalizado.")
                return

            horometro_final_texto = entry_horometro_final.get().strip()
            if not horometro_final_texto:
                messagebox.showerror("Falta información", "Ingrese el horómetro final.")
                return
            try:
                horometro_final = float(horometro_final_texto)
                horometro_inicial = float(c.get("horometro_inicial", 0))
                if horometro_final < horometro_inicial:
                    raise ValueError
            except (TypeError, ValueError):
                messagebox.showerror(
                    "Dato inválido",
                    "El horómetro final debe ser numérico y no menor al inicial.",
                )
                return

            nivel_combustible_devolucion = combo_combustible_devolucion.get()
            if nivel_combustible_devolucion == "Seleccione...":
                messagebox.showerror(
                    "Falta información", "Seleccione el nivel del combustible."
                )
                return

            recibido_por = entry_recibido_por.get().strip()
            if not recibido_por:
                messagebox.showerror(
                    "Falta información", "Indique quién recibe el equipo."
                )
                return

            quien_entrega_devolucion = entry_entrega_devolucion.get().strip()
            if not quien_entrega_devolucion:
                messagebox.showerror(
                    "Falta información",
                    "Indique quién entrega el equipo al devolverlo.",
                )
                return
            if not any(len(trazo) >= 4 for trazo in trazos_firma_devolucion):
                messagebox.showerror(
                    "Falta la firma",
                    "Registre la firma de quien entrega el equipo al devolverlo.",
                )
                return

            estado = txt_estado_dev.get("1.0", "end").strip()
            if not estado:
                messagebox.showerror("Falta información", "Debe indicar el estado de devolución.")
                return

            for cc in self.datos:
                if cc["id"] == c["id"]:
                    cc["estado_devuelto"] = estado
                    cc["horometro_final"] = horometro_final
                    cc["horas_uso_real"] = horometro_final - horometro_inicial
                    cc["nivel_combustible_devolucion"] = nivel_combustible_devolucion
                    cc["recibido_por"] = recibido_por
                    cc["quien_entrega_devolucion"] = quien_entrega_devolucion
                    cc["firma_devolucion"] = [
                        trazo.copy() for trazo in trazos_firma_devolucion
                    ]
                    cc["foto_recepcion"] = ruta_foto_recepcion["valor"]
                    cc["estado_contrato"] = "Finalizado"
                    cc["fecha_devolucion_real"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    break

            guardar_datos(self.datos)
            messagebox.showinfo("Actualizado", "Devolución registrada correctamente.")
            self._refrescar_tabla()
            self._verificar_alertas()
            ventana.destroy()

        ctk.CTkButton(
            contenido, text="💾 Confirmar Devolución", height=45, font=FUENTE_BOLD,
            fg_color="#2e7d32", hover_color="#1b5e20", command=confirmar_devolucion,
        ).pack(fill="x", padx=20, pady=16)

    # =====================================================
    # MOVILIZACIÓN
    # =====================================================
    def _abrir_movilizacion(self):
        if self.contrato_seleccionado is None:
            messagebox.showwarning("Sin selección", "Seleccione un contrato de la tabla primero.")
            return

        ventana = ctk.CTkToplevel(self)
        ventana.title(f"🚚 Movilización - Contrato #{self.contrato_seleccionado['id']}")
        ventana.geometry("620x560")
        ventana.grab_set()

        c = self.contrato_seleccionado
        mov = c.get("movilizacion", {})

        ctk.CTkLabel(
            ventana,
            text=f"🚚 Registro de Movilización\nContrato #{c['id']} - {c['equipo']} (Serie {c['serie']})",
            font=FUENTE_TITULO, text_color="#ffb74d",
        ).pack(pady=14)

        ctk.CTkLabel(ventana, text="Kilometraje inicial:", font=FUENTE_NORMAL).pack(anchor="w", padx=20)
        entry_km_ini = ctk.CTkEntry(ventana, font=FUENTE_NORMAL)
        entry_km_ini.pack(fill="x", padx=20, pady=(0, 8))
        entry_km_ini.insert(0, str(mov.get("km_inicial", "")))

        ctk.CTkLabel(ventana, text="Kilometraje final:", font=FUENTE_NORMAL).pack(anchor="w", padx=20)
        entry_km_fin = ctk.CTkEntry(ventana, font=FUENTE_NORMAL)
        entry_km_fin.pack(fill="x", padx=20, pady=(0, 8))
        entry_km_fin.insert(0, str(mov.get("km_final", "")))

        ctk.CTkLabel(ventana, text="🟢 Inicio de ruta (GPS):", font=FUENTE_BOLD,
                     text_color="#81c784").pack(anchor="w", padx=20, pady=(10, 0))
        lbl_gps_ini = ctk.CTkLabel(ventana, text=mov.get("gps_inicio", "Sin registrar"),
                                   font=FUENTE_NORMAL, text_color="gray")
        lbl_gps_ini.pack(anchor="w", padx=20)

        ctk.CTkLabel(ventana, text="🔴 Fin de ruta (GPS):", font=FUENTE_BOLD,
                     text_color="#ef5350").pack(anchor="w", padx=20, pady=(10, 0))
        lbl_gps_fin = ctk.CTkLabel(ventana, text=mov.get("gps_fin", "Sin registrar"),
                                   font=FUENTE_NORMAL, text_color="gray")
        lbl_gps_fin.pack(anchor="w", padx=20)

        gps_inicio_temp = {"valor": mov.get("gps_inicio", "")}
        gps_fin_temp = {"valor": mov.get("gps_fin", "")}

        def capturar_inicio():
            gps = obtener_gps()
            if gps == "No disponible":
                gps = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} (GPS no disponible)"
            gps_inicio_temp["valor"] = gps
            lbl_gps_ini.configure(text=gps, text_color="#81c784")

        def capturar_fin():
            gps = obtener_gps()
            if gps == "No disponible":
                gps = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} (GPS no disponible)"
            gps_fin_temp["valor"] = gps
            lbl_gps_fin.configure(text=gps, text_color="#ef5350")

        frame_btn_gps = ctk.CTkFrame(ventana, fg_color="transparent")
        frame_btn_gps.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(frame_btn_gps, text="📍 Capturar GPS Inicio",
                      font=FUENTE_NORMAL, fg_color="#2e7d32", hover_color="#1b5e20",
                      command=capturar_inicio).pack(side="left", padx=4)
        ctk.CTkButton(frame_btn_gps, text="📍 Capturar GPS Fin",
                      font=FUENTE_NORMAL, fg_color="#c62828", hover_color="#8e0000",
                      command=capturar_fin).pack(side="left", padx=4)

        def guardar():
            try:
                km_ini = float(entry_km_ini.get() or 0)
                km_fin = float(entry_km_fin.get() or 0)
            except ValueError:
                messagebox.showerror("Dato inválido", "El kilometraje debe ser numérico.")
                return

            for cc in self.datos:
                if cc["id"] == c["id"]:
                    cc["movilizacion"] = {
                        "km_inicial": km_ini,
                        "km_final": km_fin,
                        "gps_inicio": gps_inicio_temp["valor"],
                        "gps_fin": gps_fin_temp["valor"],
                        "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                    break

            guardar_datos(self.datos)
            messagebox.showinfo("Guardado", "Datos de movilización actualizados.")
            ventana.destroy()

        ctk.CTkButton(
            ventana, text="💾 Guardar Movilización", height=45,
            font=FUENTE_BOLD, fg_color="#1f6aa5", hover_color="#144870",
            command=guardar,
        ).pack(fill="x", padx=20, pady=20)

    def _registrar_renta(self):
        cliente = self.entry_cliente.get().strip()
        cedula = self.entry_cedula.get().strip()
        equipo = self.entry_nombre.get().strip()
        serie = self.entry_serie.get().strip()
        quien_entrega = self.entry_entregado_por.get().strip()
        if not all((cliente, cedula, equipo, serie, quien_entrega)):
            messagebox.showerror(
                "Faltan datos",
                "Complete cliente, cédula, equipo, serie y quién entrega el equipo.",
            )
            return
        if not any(len(trazo) >= 4 for trazo in self.trazos_firma_entrega):
            messagebox.showerror(
                "Falta la firma", "Registre la firma de quien entrega el equipo."
            )
            return

        try:
            cantidad = int(self.entry_cantidad.get())
            horometro = float(self.entry_horometro_ini.get() or 0)
            horas = float(self.entry_horas.get())
            precio = float(self.entry_precio.get())
            garantia = float(self.entry_garantia.get() or 0)
            fecha_entrega = datetime.strptime(
                self.entry_fecha_entrega.get().strip(), "%Y-%m-%d %H:%M"
            )
            fecha_max = datetime.strptime(
                self.entry_fecha_max.get().strip(), "%Y-%m-%d %H:%M"
            )
            if cantidad < 1 or min(horometro, horas, precio, garantia) < 0 or horas == 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Datos inválidos",
                "Revise cantidades, importes y fechas (YYYY-MM-DD HH:MM).",
            )
            return

        subtotal = horas * precio
        iva = subtotal * IVA
        contrato = {
            "id": max(
                (dato.get("id", 0) for dato in self.datos if isinstance(dato.get("id"), int)),
                default=0,
            ) + 1,
            "equipo": equipo,
            "serie": serie,
            "cantidad": cantidad,
            "horometro_inicial": horometro,
            "horas_contratadas": horas,
            "precio_hora": precio,
            "garantia": garantia,
            "metodo_pago": self.combo_pago.get(),
            "subtotal": subtotal,
            "iva": iva,
            "total": subtotal + iva,
            "cliente": cliente,
            "cedula": cedula,
            "telefono": self.entry_telefono.get().strip(),
            "correo": self.entry_correo.get().strip(),
            "area": self.entry_area.get().strip(),
            "fecha_entrega": fecha_entrega.strftime("%Y-%m-%d %H:%M"),
            "fecha_max_devolucion": fecha_max.strftime("%Y-%m-%d %H:%M"),
            "nivel_combustible": self.combo_combustible.get(),
            "alerta_mantenimiento": self.var_mantenimiento.get(),
            "estado_entrega": self.txt_estado_entrega.get("1.0", "end").strip(),
            "quien_entrega": quien_entrega,
            "firma_entrega": [trazo.copy() for trazo in self.trazos_firma_entrega],
            "estado_devuelto": "",
            "foto_entrega": self.ruta_foto_entrega,
            "foto_recepcion": "",
            "estado_contrato": "Activo",
            "movilizacion": {
                "km_inicial": 0,
                "km_final": 0,
                "gps_inicio": "",
                "gps_fin": "",
            },
        }
        self.datos.append(contrato)
        try:
            guardar_datos(self.datos)
        except OSError as error:
            self.datos.pop()
            messagebox.showerror("Error al guardar", str(error))
            return

        self._refrescar_tabla()
        self._limpiar_campos()
        messagebox.showinfo("Renta registrada", f"Contrato #{contrato['id']} guardado.")

    def _refrescar_tabla(self, event=None):
        filtro = self.entry_busqueda.get().strip().casefold()
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for contrato in self.datos:
            cedula = str(contrato.get("cedula", ""))
            serie = str(contrato.get("serie", ""))
            if filtro and filtro not in cedula.casefold() and filtro not in serie.casefold():
                continue

            fecha_max = contrato.get("fecha_max_devolucion", "")
            self.tabla.insert(
                "",
                "end",
                iid=str(contrato["id"]),
                values=(
                    contrato["id"],
                    contrato.get("equipo", ""),
                    serie,
                    contrato.get("cliente", ""),
                    cedula,
                    contrato.get("fecha_entrega", ""),
                    fecha_max,
                    contrato.get("horas_contratadas", ""),
                    f"${float(contrato.get('total', 0)):,.2f}",
                    contrato.get("estado_contrato", "Activo"),
                ),
            )

    def _seleccionar_contrato(self, event=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            self.contrato_seleccionado = None
            self.btn_movilizacion.configure(state="disabled")
            return

        contrato_id = self.tabla.item(seleccion[0], "values")[0]
        self.contrato_seleccionado = next(
            (c for c in self.datos if str(c.get("id")) == str(contrato_id)),
            None,
        )
        self.btn_movilizacion.configure(
            state="normal" if self.contrato_seleccionado else "disabled"
        )

    def _limpiar_campos(self):
        for entry in (
            self.entry_cliente, self.entry_cedula, self.entry_telefono,
            self.entry_correo, self.entry_area, self.entry_nombre, self.entry_serie,
            self.entry_cantidad, self.entry_horometro_ini, self.entry_horas,
            self.entry_precio, self.entry_garantia, self.entry_fecha_max,
        ):
            entry.delete(0, "end")

        self.entry_fecha_entrega.delete(0, "end")
        self._auto_fecha_entrega()
        self.combo_pago.set("Efectivo")
        self.combo_combustible.set("Full")
        self.var_mantenimiento.set(False)
        self.txt_estado_entrega.delete("1.0", "end")
        self.entry_entregado_por.delete(0, "end")
        self._limpiar_firma_entrega()
        self.ruta_foto_entrega = ""
        self.lbl_foto_entrega.configure(text="Sin imagen", text_color="gray")
        for entry in (self.entry_subtotal, self.entry_iva, self.entry_total):
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.configure(state="readonly")
        self.contrato_seleccionado = None
        self.btn_movilizacion.configure(state="disabled")

    def _iniciar_trazo_firma(self, event):
        self.trazos_firma_entrega.append([event.x, event.y])

    def _dibujar_trazo_firma(self, event):
        if not self.trazos_firma_entrega:
            return
        trazo = self.trazos_firma_entrega[-1]
        x_anterior, y_anterior = trazo[-2:]
        self.canvas_firma_entrega.create_line(
            x_anterior, y_anterior, event.x, event.y,
            fill="#111111", width=2, capstyle="round", smooth=True,
        )
        trazo.extend((event.x, event.y))

    def _limpiar_firma_entrega(self):
        self.trazos_firma_entrega.clear()
        self.canvas_firma_entrega.delete("all")

    def _verificar_alertas(self):
        ahora = datetime.now()
        alertas = []
        for contrato in self.datos:
            if str(contrato.get("estado_contrato", "")).casefold() != "activo":
                continue
            try:
                fecha_max = datetime.strptime(
                    contrato.get("fecha_max_devolucion", ""),
                    "%Y-%m-%d %H:%M",
                )
            except ValueError:
                continue
            if ahora > fecha_max and not contrato.get("justificacion_vencimiento"):
                alertas.append(contrato)

        for widget in self.banner.winfo_children():
            widget.destroy()
        if alertas:
            if not self.banner.winfo_manager():
                self.banner.pack(fill="x", padx=10, pady=0, before=self.tabs)
            self.parpadeo_estado = not self.parpadeo_estado
            self.banner.configure(
                fg_color="#c62828" if self.parpadeo_estado else "#8e0000"
            )
            for contrato in alertas:
                texto = (
                    f"⚠ Contrato #{contrato.get('id')} vencido: "
                    f"{contrato.get('equipo', 'Equipo')} "
                    f"({contrato.get('serie', '')}) — Justificar entrega"
                )
                ctk.CTkButton(
                    self.banner,
                    text=texto,
                    font=FUENTE_BOLD,
                    fg_color="#c62828",
                    hover_color="#8e0000",
                    command=lambda c=contrato: self._abrir_justificacion_vencimiento(c),
                ).pack(fill="x", padx=4, pady=2)
        else:
            self.banner.pack_forget()
        self.after(30000, self._verificar_alertas)

    def _abrir_justificacion_vencimiento(self, contrato):
        ventana = ctk.CTkToplevel(self)
        ventana.title(f"Justificar entrega - Contrato #{contrato.get('id')}")
        ventana.geometry("620x400")
        ventana.transient(self)
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text=(
                f"Contrato #{contrato.get('id')} vencido\n"
                f"{contrato.get('equipo', 'Equipo')} — {contrato.get('serie', '')}"
            ),
            font=FUENTE_TITULO,
            text_color="#ef5350",
        ).pack(fill="x", padx=20, pady=16)
        ctk.CTkLabel(
            ventana, text="Justificación de la entrega fuera de plazo:",
            font=FUENTE_NORMAL,
        ).pack(anchor="w", padx=20)
        texto_justificacion = ctk.CTkTextbox(ventana, height=180, font=FUENTE_NORMAL)
        texto_justificacion.pack(fill="both", expand=True, padx=20, pady=8)
        texto_justificacion.insert(
            "1.0", contrato.get("justificacion_vencimiento", "")
        )

        def guardar_justificacion():
            justificacion = texto_justificacion.get("1.0", "end").strip()
            if not justificacion:
                messagebox.showerror(
                    "Falta información", "Escriba la justificación de la entrega."
                )
                return

            anterior = contrato.get("justificacion_vencimiento")
            fecha_anterior = contrato.get("fecha_justificacion_vencimiento")
            contrato["justificacion_vencimiento"] = justificacion
            contrato["fecha_justificacion_vencimiento"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
            try:
                guardar_datos(self.datos)
            except OSError as error:
                if anterior is None:
                    contrato.pop("justificacion_vencimiento", None)
                else:
                    contrato["justificacion_vencimiento"] = anterior
                if fecha_anterior is None:
                    contrato.pop("fecha_justificacion_vencimiento", None)
                else:
                    contrato["fecha_justificacion_vencimiento"] = fecha_anterior
                messagebox.showerror(
                    "Error al guardar", f"No se pudo guardar la justificación: {error}"
                )
                return

            ventana.destroy()
            self._verificar_alertas()

        ctk.CTkButton(
            ventana, text="💾 Guardar justificación", height=42,
            font=FUENTE_BOLD, command=guardar_justificacion,
        ).pack(fill="x", padx=20, pady=(0, 16))

    def _loop_parpadeo(self):
        self._verificar_alertas()


if __name__ == "__main__":
    app = AppRentaMaquinaria()
    app.mainloop()
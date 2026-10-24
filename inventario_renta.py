import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
import json
import os
import re

# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class InventarioRentaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Inventario y Renta de Maquinaria")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Datos
        self.archivo_json = "inventario_renta.json"
        self.contratos = []
        self.contrato_seleccionado = None
        self.foto_entrega_path = ""
        self.foto_recepcion_path = ""
        self.modo_devolucion = False
        
        # Cargar datos existentes
        self.cargar_datos()
        
        # Construir interfaz
        self.construir_interfaz()
        
        # Iniciar verificación de alarmas
        self.verificar_alarmas()
    
    def cargar_datos(self):
        """Carga los datos desde el archivo JSON"""
        if os.path.exists(self.archivo_json):
            try:
                with open(self.archivo_json, 'r', encoding='utf-8') as f:
                    self.contratos = [
                        self._normalizar_contrato(contrato)
                        for contrato in json.load(f)
                    ]
            except (json.JSONDecodeError, IOError):
                self.contratos = []
        else:
            self.contratos = []

    @staticmethod
    def _normalizar_contrato(contrato):
        """Adapta nombres de campos de las otras versiones sin descartar datos."""
        contrato = contrato.copy()
        aliases = {
            "nombre_equipo": "equipo",
            "nombre_cliente": "cliente",
            "area_uso": "area",
            "fecha_devolucion": "fecha_max_devolucion",
            "estado_devolucion": "estado_devuelto",
        }
        for campo, alias in aliases.items():
            if campo not in contrato and alias in contrato:
                contrato[campo] = contrato[alias]

        if "estado" not in contrato:
            estado = str(contrato.get("estado_contrato", "ACTIVO")).upper()
            contrato["estado"] = "DEVUELTO" if estado == "FINALIZADO" else estado
        contrato.setdefault("horometro_final", None)
        return contrato
    
    def guardar_datos(self):
        """Guarda los datos en el archivo JSON"""
        with open(self.archivo_json, 'w', encoding='utf-8') as f:
            json.dump(self.contratos, f, indent=4, ensure_ascii=False)
    
    def construir_interfaz(self):
        """Construye toda la interfaz gráfica"""
        # Banner de alarmas
        self.banner_alarma = ctk.CTkLabel(
            self.root, 
            text="", 
            font=("Arial", 14, "bold"),
            fg_color="#8B0000",
            text_color="white",
            height=40,
            corner_radius=0
        )
        self.banner_alarma.pack(fill="x", side="top")
        
        # Frame principal
        self.frame_principal = ctk.CTkFrame(self.root)
        self.frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestañas
        self.tabs = ctk.CTkTabview(self.frame_principal)
        self.tabs.pack(fill="both", expand=True)
        
        self.tab_formulario = self.tabs.add("Formulario de Registro")
        self.tab_tabla = self.tabs.add("Tabla de Contratos")
        
        # Construir cada pestaña
        self.construir_tab_formulario()
        self.construir_tab_tabla()
    
    def construir_tab_formulario(self):
        """Construye la pestaña del formulario de registro"""
        # Canvas con scrollbar para el formulario
        canvas = ctk.CTkScrollableFrame(self.tab_formulario)
        canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === IDENTIFICACIÓN DEL EQUIPO ===
        frame_equipo = ctk.CTkFrame(canvas)
        frame_equipo.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(frame_equipo, text="🏗️ IDENTIFICACIÓN DEL EQUIPO", 
                     font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # Nombre del equipo
        ctk.CTkLabel(frame_equipo, text="Nombre del Equipo:").pack(anchor="w", padx=10)
        self.entry_nombre = ctk.CTkEntry(frame_equipo, placeholder_text="Ej: Excavadora CAT 320")
        self.entry_nombre.pack(fill="x", padx=10, pady=2)
        
        # Serie del equipo
        ctk.CTkLabel(frame_equipo, text="Serie del Equipo:").pack(anchor="w", padx=10)
        self.entry_serie = ctk.CTkEntry(frame_equipo, placeholder_text="Ej: CAT0320ABC123")
        self.entry_serie.pack(fill="x", padx=10, pady=2)
        
        # Cantidad de equipos
        ctk.CTkLabel(frame_equipo, text="Cantidad de Equipos:").pack(anchor="w", padx=10)
        self.entry_cantidad = ctk.CTkEntry(frame_equipo, placeholder_text="Ej: 1")
        self.entry_cantidad.pack(fill="x", padx=10, pady=2)
        
        # Horómetro inicial
        ctk.CTkLabel(frame_equipo, text="Horómetro Inicial del Motor (al entregar):").pack(anchor="w", padx=10)
        self.entry_horometro_inicial = ctk.CTkEntry(frame_equipo, placeholder_text="Ej: 1500")
        self.entry_horometro_inicial.pack(fill="x", padx=10, pady=2)
        
        # Horómetro final
        ctk.CTkLabel(frame_equipo, text="Horómetro Final del Motor (al recibir):").pack(anchor="w", padx=10)
        self.entry_horometro_final = ctk.CTkEntry(frame_equipo, placeholder_text="Se llena al devolver", state="disabled")
        self.entry_horometro_final.pack(fill="x", padx=10, pady=2)
        
        # === DATOS FINANCIEROS ===
        frame_financiero = ctk.CTkFrame(canvas)
        frame_financiero.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(frame_financiero, text="💰 DATOS FINANCIEROS", 
                     font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # Horas contratadas
        ctk.CTkLabel(frame_financiero, text="Horas Contratadas a Rentar:").pack(anchor="w", padx=10)
        self.entry_horas = ctk.CTkEntry(frame_financiero, placeholder_text="Ej: 8")
        self.entry_horas.pack(fill="x", padx=10, pady=2)
        self.entry_horas.bind('<KeyRelease>', self.calcular_totales)
        
        # Precio por hora
        ctk.CTkLabel(frame_financiero, text="Precio por Hora del Equipo ($):").pack(anchor="w", padx=10)
        self.entry_precio = ctk.CTkEntry(frame_financiero, placeholder_text="Ej: 50.00")
        self.entry_precio.pack(fill="x", padx=10, pady=2)
        self.entry_precio.bind('<KeyRelease>', self.calcular_totales)
        
        # Garantía
        ctk.CTkLabel(frame_financiero, text="Garantía / Depósito de Seguridad ($):").pack(anchor="w", padx=10)
        self.entry_garantia = ctk.CTkEntry(frame_financiero, placeholder_text="Ej: 500.00")
        self.entry_garantia.pack(fill="x", padx=10, pady=2)
        
        # Método de pago
        ctk.CTkLabel(frame_financiero, text="Método de Pago:").pack(anchor="w", padx=10)
        self.combo_pago = ctk.CTkComboBox(frame_financiero, values=["Efectivo", "Transferencia", "Tarjeta", "Crédito Interno"])
        self.combo_pago.set("Efectivo")
        self.combo_pago.pack(fill="x", padx=10, pady=2)
        
        # Monto total calculado (solo lectura)
        frame_total = ctk.CTkFrame(frame_financiero, fg_color="#2B2B2B")
        frame_total.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(frame_total, text="📊 CÁLCULO AUTOMÁTICO:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=2)
        
        self.label_subtotal = ctk.CTkLabel(frame_total, text="Subtotal: $0.00", font=("Arial", 11))
        self.label_subtotal.pack(anchor="w", padx=10)
        
        self.label_iva = ctk.CTkLabel(frame_total, text="IVA (15%): $0.00", font=("Arial", 11))
        self.label_iva.pack(anchor="w", padx=10)
        
        self.label_total = ctk.CTkLabel(frame_total, text="TOTAL NETO: $0.00", font=("Arial", 14, "bold"), text_color="#4CAF50")
        self.label_total.pack(anchor="w", padx=10, pady=2)
        
        # === DATOS DEL CLIENTE ===
        frame_cliente = ctk.CTkFrame(canvas)
        frame_cliente.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(frame_cliente, text="👤 DATOS DEL CLIENTE", 
                     font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkLabel(frame_cliente, text="Nombre del Cliente:").pack(anchor="w", padx=10)
        self.entry_cliente = ctk.CTkEntry(frame_cliente, placeholder_text="Nombre completo")
        self.entry_cliente.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(frame_cliente, text="Cédula:").pack(anchor="w", padx=10)
        self.entry_cedula = ctk.CTkEntry(frame_cliente, placeholder_text="Número de cédula")
        self.entry_cedula.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(frame_cliente, text="Teléfono:").pack(anchor="w", padx=10)
        self.entry_telefono = ctk.CTkEntry(frame_cliente, placeholder_text="Número de teléfono")
        self.entry_telefono.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(frame_cliente, text="Correo Electrónico:").pack(anchor="w", padx=10)
        self.entry_correo = ctk.CTkEntry(frame_cliente, placeholder_text="correo@ejemplo.com")
        self.entry_correo.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(frame_cliente, text="Área / Lugar de Uso:").pack(anchor="w", padx=10)
        self.entry_area = ctk.CTkEntry(frame_cliente, placeholder_text="Ej: Zona Norte, Proyecto X")
        self.entry_area.pack(fill="x", padx=10, pady=2)
        
        # === FECHAS Y CONTROL TÉCNICO ===
        frame_fechas = ctk.CTkFrame(canvas)
        frame_fechas.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(frame_fechas, text="📅 FECHAS Y CONTROL TÉCNICO", 
                     font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # Fecha de entrega
        ctk.CTkLabel(frame_fechas, text="Fecha/Hora de Entrega:").pack(anchor="w", padx=10)
        self.entry_fecha_entrega = ctk.CTkEntry(frame_fechas, placeholder_text="YYYY-MM-DD HH:MM")
        self.entry_fecha_entrega.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.entry_fecha_entrega.pack(fill="x", padx=10, pady=2)
        
        # Fecha máxima de devolución
        ctk.CTkLabel(frame_fechas, text="Fecha/Hora Máxima de Devolución:").pack(anchor="w", padx=10)
        self.entry_fecha_devolucion = ctk.CTkEntry(frame_fechas, placeholder_text="YYYY-MM-DD HH:MM")
        self.entry_fecha_devolucion.pack(fill="x", padx=10, pady=2)
        
        # Nivel de combustible
        ctk.CTkLabel(frame_fechas, text="Nivel de Combustible de Entrega:").pack(anchor="w", padx=10)
        self.combo_combustible = ctk.CTkComboBox(frame_fechas, values=["Full", "1/2", "1/4"])
        self.combo_combustible.set("Full")
        self.combo_combustible.pack(fill="x", padx=10, pady=2)
        
        # Alerta de mantenimiento
        self.check_mantenimiento = ctk.CTkCheckBox(
            frame_fechas, 
            text="⚠️ Alerta: Equipo supera 250 horas desde último servicio",
            text_color="orange"
        )
        self.check_mantenimiento.pack(anchor="w", padx=10, pady=5)
        
        # === ESTADOS DE INSPECCIÓN ===
        frame_inspeccion = ctk.CTkFrame(canvas)
        frame_inspeccion.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(frame_inspeccion, text="🔍 ESTADOS DE INSPECCIÓN", 
                     font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkLabel(frame_inspeccion, text="Estado en que se ENTREGA el equipo al cliente:").pack(anchor="w", padx=10)
        self.text_estado_entrega = ctk.CTkTextbox(frame_inspeccion, height=60)
        self.text_estado_entrega.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(frame_inspeccion, text="Estado en que se DEVUELVE el equipo a la empresa:").pack(anchor="w", padx=10)
        self.text_estado_devolucion = ctk.CTkTextbox(frame_inspeccion, height=60, state="disabled")
        self.text_estado_devolucion.pack(fill="x", padx=10, pady=2)
        
        # === REGISTRO FOTOGRÁFICO ===
        frame_fotos = ctk.CTkFrame(canvas)
        frame_fotos.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(frame_fotos, text="📷 REGISTRO FOTOGRÁFICO", 
                     font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        frame_botones_fotos = ctk.CTkFrame(frame_fotos)
        frame_botones_fotos.pack(fill="x", padx=10, pady=5)
        
        self.boton_foto_entrega = ctk.CTkButton(
            frame_botones_fotos, 
            text="📸 Adjuntar Foto de Entrega",
            command=self.adjuntar_foto_entrega
        )
        self.boton_foto_entrega.pack(side="left", padx=5, expand=True, fill="x")
        
        self.boton_foto_recepcion = ctk.CTkButton(
            frame_botones_fotos, 
            text="📸 Adjuntar Foto de Recepción",
            command=self.adjuntar_foto_recepcion,
            state="disabled"
        )
        self.boton_foto_recepcion.pack(side="left", padx=5, expand=True, fill="x")
        
        self.label_foto_entrega = ctk.CTkLabel(frame_fotos, text="Foto entrega: No adjunta", text_color="gray")
        self.label_foto_entrega.pack(anchor="w", padx=10)
        
        self.label_foto_recepcion = ctk.CTkLabel(frame_fotos, text="Foto recepción: No adjunta", text_color="gray")
        self.label_foto_recepcion.pack(anchor="w", padx=10)
        
        # === BOTONES OPERATIVOS ===
        frame_botones = ctk.CTkFrame(canvas)
        frame_botones.pack(fill="x", pady=10, padx=5)
        
        self.boton_registrar = ctk.CTkButton(
            frame_botones, 
            text="📥 Registrar Nueva Renta",
            command=self.registrar_renta,
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#2E7D32"
        )
        self.boton_registrar.pack(side="left", padx=5, expand=True, fill="x")
        
        self.boton_devolucion = ctk.CTkButton(
            frame_botones, 
            text="🔄 Registrar Devolución / Actualizar",
            command=self.registrar_devolucion,
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#1565C0"
        )
        self.boton_devolucion.pack(side="left", padx=5, expand=True, fill="x")
        
        self.boton_limpiar = ctk.CTkButton(
            frame_botones, 
            text="🧹 Limpiar Campos",
            command=self.limpiar_campos,
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#616161"
        )
        self.boton_limpiar.pack(side="left", padx=5, expand=True, fill="x")
    
    def construir_tab_tabla(self):
        """Construye la pestaña de la tabla de contratos"""
        # Buscador
        frame_busqueda = ctk.CTkFrame(self.tab_tabla)
        frame_busqueda.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(frame_busqueda, text="🔍 Búsqueda Rápida (Cédula o Serie):").pack(side="left", padx=5)
        self.entry_busqueda = ctk.CTkEntry(frame_busqueda, placeholder_text="Ingrese cédula o serie...")
        self.entry_busqueda.pack(side="left", padx=5, fill="x", expand=True)
        self.entry_busqueda.bind('<KeyRelease>', self.filtrar_tabla)
        
        # Tabla de contratos
        frame_tabla = ctk.CTkFrame(self.tab_tabla)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Headers
        headers = ["ID", "Equipo", "Serie", "Cliente", "Cédula", "Fecha Entrega", "Fecha Devolución", "Horas", "Total", "Estado"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(frame_tabla, text=header, font=("Arial", 10, "bold")).grid(row=0, column=i, padx=2, pady=2, sticky="w")
        
        # Frame scrollable para los datos
        self.frame_datos = ctk.CTkScrollableFrame(frame_tabla)
        self.frame_datos.grid(row=1, column=0, columnspan=len(headers), sticky="nsew", padx=2, pady=2)
        
        self.actualizar_tabla()
    
    def calcular_totales(self, event=None):
        """Calcula automáticamente subtotal, IVA y total"""
        try:
            horas = float(self.entry_horas.get() or 0)
            precio = float(self.entry_precio.get() or 0)
            
            subtotal = horas * precio
            iva = subtotal * 0.15
            total = subtotal + iva
            
            self.label_subtotal.configure(text=f"Subtotal: ${subtotal:,.2f}")
            self.label_iva.configure(text=f"IVA (15%): ${iva:,.2f}")
            self.label_total.configure(text=f"TOTAL NETO: ${total:,.2f}")
        except ValueError:
            self.label_subtotal.configure(text="Subtotal: $0.00")
            self.label_iva.configure(text="IVA (15%): $0.00")
            self.label_total.configure(text="TOTAL NETO: $0.00")
    
    def adjuntar_foto_entrega(self):
        """Abre diálogo para seleccionar foto de entrega"""
        filepath = filedialog.askopenfilename(
            title="Seleccionar Foto de Entrega",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos los archivos", "*.*")]
        )
        if filepath:
            self.foto_entrega_path = filepath
            self.label_foto_entrega.configure(text=f"Foto entrega: {os.path.basename(filepath)}", text_color="green")
    
    def adjuntar_foto_recepcion(self):
        """Abre diálogo para seleccionar foto de recepción"""
        filepath = filedialog.askopenfilename(
            title="Seleccionar Foto de Recepción",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos los archivos", "*.*")]
        )
        if filepath:
            self.foto_recepcion_path = filepath
            self.label_foto_recepcion.configure(text=f"Foto recepción: {os.path.basename(filepath)}", text_color="green")
    
    def validar_campos(self):
        """Valida que los campos requeridos estén correctos"""
        errores = []
        
        # Validar campos vacíos
        if not self.entry_nombre.get().strip():
            errores.append("Nombre del equipo es requerido")
        if not self.entry_serie.get().strip():
            errores.append("Serie del equipo es requerida")
        if not self.entry_cliente.get().strip():
            errores.append("Nombre del cliente es requerido")
        if not self.entry_cedula.get().strip():
            errores.append("Cédula es requerida")
        
        # Validar campos numéricos
        try:
            cantidad = int(self.entry_cantidad.get() or 1)
            if cantidad < 1:
                errores.append("Cantidad debe ser al menos 1")
        except ValueError:
            errores.append("Cantidad debe ser un número entero")
        
        try:
            horometro = float(self.entry_horometro_inicial.get() or 0)
            if horometro < 0:
                errores.append("Horómetro inicial no puede ser negativo")
        except ValueError:
            errores.append("Horómetro inicial debe ser un número")
        
        try:
            horas = float(self.entry_horas.get() or 0)
            if horas <= 0:
                errores.append("Horas contratadas debe ser mayor a 0")
        except ValueError:
            errores.append("Horas contratadas debe ser un número")
        
        try:
            precio = float(self.entry_precio.get() or 0)
            if precio < 0:
                errores.append("Precio por hora no puede ser negativo")
        except ValueError:
            errores.append("Precio por hora debe ser un número")
        
        try:
            garantia = float(self.entry_garantia.get() or 0)
            if garantia < 0:
                errores.append("Garantía no puede ser negativa")
        except ValueError:
            errores.append("Garantía debe ser un número")
        
        # Validar formato de fechas
        try:
            datetime.strptime(self.entry_fecha_entrega.get(), "%Y-%m-%d %H:%M")
        except ValueError:
            errores.append("Formato de fecha de entrega inválido (YYYY-MM-DD HH:MM)")
        
        try:
            datetime.strptime(self.entry_fecha_devolucion.get(), "%Y-%m-%d %H:%M")
        except ValueError:
            errores.append("Formato de fecha de devolución inválido (YYYY-MM-DD HH:MM)")
        
        if errores:
            messagebox.showerror("Error de Validación", "\n".join(errores))
            return False
        return True
    
    def registrar_renta(self):
        """Registra una nueva renta"""
        if not self.validar_campos():
            return
        
        # Generar ID único
        contrato_id = f"CTR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calcular totales
        horas = float(self.entry_horas.get())
        precio = float(self.entry_precio.get())
        subtotal = horas * precio
        iva = subtotal * 0.15
        total = subtotal + iva
        
        contrato = {
            "id": contrato_id,
            "nombre_equipo": self.entry_nombre.get().strip(),
            "serie": self.entry_serie.get().strip(),
            "cantidad": int(self.entry_cantidad.get() or 1),
            "horometro_inicial": float(self.entry_horometro_inicial.get() or 0),
            "horometro_final": None,
            "horas_contratadas": horas,
            "precio_hora": precio,
            "garantia": float(self.entry_garantia.get() or 0),
            "metodo_pago": self.combo_pago.get(),
            "subtotal": subtotal,
            "iva": iva,
            "total": total,
            "nombre_cliente": self.entry_cliente.get().strip(),
            "cedula": self.entry_cedula.get().strip(),
            "telefono": self.entry_telefono.get().strip(),
            "correo": self.entry_correo.get().strip(),
            "area_uso": self.entry_area.get().strip(),
            "fecha_entrega": self.entry_fecha_entrega.get(),
            "fecha_devolucion": self.entry_fecha_devolucion.get(),
            "nivel_combustible": self.combo_combustible.get(),
            "alerta_mantenimiento": self.check_mantenimiento.get(),
            "estado_entrega": self.text_estado_entrega.get("1.0", "end").strip(),
            "estado_devolucion": "",
            "foto_entrega": self.foto_entrega_path,
            "foto_recepcion": "",
            "estado": "ACTIVO",
            "fecha_registro": datetime.now().isoformat()
        }
        
        self.contratos.append(contrato)
        self.guardar_datos()
        self.actualizar_tabla()
        
        messagebox.showinfo("Éxito", f"Contrato {contrato_id} registrado correctamente")
        self.limpiar_campos()
    
    def registrar_devolucion(self):
        """Registra la devolución de un contrato"""
        if not self.contrato_seleccionado:
            messagebox.showwarning("Atención", "Debe seleccionar un contrato de la tabla primero")
            return
        
        # Buscar el contrato
        contrato = None
        for c in self.contratos:
            if c['id'] == self.contrato_seleccionado:
                contrato = c
                break
        
        if not contrato:
            messagebox.showerror("Error", "No se encontró el contrato seleccionado")
            return
        
        # Validar campos de devolución
        try:
            horometro_final = float(self.entry_horometro_final.get())
            if horometro_final < contrato['horometro_inicial']:
                messagebox.showerror("Error", "El horómetro final no puede ser menor al inicial")
                return
        except ValueError:
            messagebox.showerror("Error", "Horómetro final debe ser un número válido")
            return
        
        # Actualizar contrato
        contrato['horometro_final'] = horometro_final
        contrato['estado_devolucion'] = self.text_estado_devolucion.get("1.0", "end").strip()
        contrato['foto_recepcion'] = self.foto_recepcion_path
        contrato['estado'] = "DEVUELTO"
        contrato['fecha_devolucion_real'] = datetime.now().isoformat()
        
        self.guardar_datos()
        self.actualizar_tabla()
        
        messagebox.showinfo("Éxito", f"Devolución del contrato {contrato['id']} registrada correctamente")
        self.limpiar_campos()
    
    def limpiar_campos(self):
        """Limpia todos los campos del formulario"""
        # Limpiar entries
        self.entry_nombre.delete(0, "end")
        self.entry_serie.delete(0, "end")
        self.entry_cantidad.delete(0, "end")
        self.entry_cantidad.insert(0, "1")
        self.entry_horometro_inicial.delete(0, "end")
        self.entry_horometro_final.delete(0, "end")
        self.entry_horometro_final.configure(state="disabled")
        self.entry_horas.delete(0, "end")
        self.entry_precio.delete(0, "end")
        self.entry_garantia.delete(0, "end")
        self.entry_cliente.delete(0, "end")
        self.entry_cedula.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_correo.delete(0, "end")
        self.entry_area.delete(0, "end")
        self.entry_fecha_entrega.delete(0, "end")
        self.entry_fecha_entrega.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.entry_fecha_devolucion.delete(0, "end")
        
        # Resetear selectores
        self.combo_pago.set("Efectivo")
        self.combo_combustible.set("Full")
        self.check_mantenimiento.deselect()
        
        # Limpiar textos
        self.text_estado_entrega.delete("1.0", "end")
        self.text_estado_devolucion.delete("1.0", "end")
        self.text_estado_devolucion.configure(state="disabled")
        
        # Limpiar fotos
        self.foto_entrega_path = ""
        self.foto_recepcion_path = ""
        self.label_foto_entrega.configure(text="Foto entrega: No adjunta", text_color="gray")
        self.label_foto_recepcion.configure(text="Foto recepción: No adjunta", text_color="gray")
        self.boton_foto_recepcion.configure(state="disabled")
        
        # Resetear totales
        self.label_subtotal.configure(text="Subtotal: $0.00")
        self.label_iva.configure(text="IVA (15%): $0.00")
        self.label_total.configure(text="TOTAL NETO: $0.00")
        
        # Resetear modo
        self.modo_devolucion = False
        self.contrato_seleccionado = None
    
    def actualizar_tabla(self, filtro=""):
        """Actualiza la tabla con los contratos"""
        # Limpiar datos anteriores
        for widget in self.frame_datos.winfo_children():
            widget.destroy()
        
        for i, contrato in enumerate(self.contratos):
            # Aplicar filtro
            if filtro:
                filtro_lower = filtro.lower()
                if filtro_lower not in contrato['cedula'].lower() and filtro_lower not in contrato['serie'].lower():
                    continue
            
            # Color de fondo según estado
            bg_color = "#1E1E1E" if i % 2 == 0 else "#2B2B2B"
            
            row_frame = ctk.CTkFrame(self.frame_datos, fg_color=bg_color)
            row_frame.pack(fill="x", pady=1)
            
            # Botón para seleccionar
            btn_seleccionar = ctk.CTkButton(
                row_frame, 
                text="Seleccionar",
                width=80,
                height=25,
                font=("Arial", 9),
                command=lambda cid=contrato['id']: self.seleccionar_contrato(cid)
            )
            btn_seleccionar.pack(side="left", padx=2)
            
            # Datos
            datos = [
                contrato['id'],
                contrato['nombre_equipo'],
                contrato['serie'],
                contrato['nombre_cliente'],
                contrato['cedula'],
                contrato['fecha_entrega'],
                contrato['fecha_devolucion'],
                str(contrato['horas_contratadas']),
                f"${contrato['total']:,.2f}",
                contrato['estado']
            ]
            
            for j, dato in enumerate(datos):
                lbl = ctk.CTkLabel(row_frame, text=str(dato), font=("Arial", 9), width=100)
                lbl.pack(side="left", padx=2)
    
    def filtrar_tabla(self, event=None):
        """Filtra la tabla según el texto de búsqueda"""
        filtro = self.entry_busqueda.get()
        self.actualizar_tabla(filtro)
    
    def seleccionar_contrato(self, contrato_id):
        """Selecciona un contrato para devolución"""
        self.contrato_seleccionado = contrato_id
        self.modo_devolucion = True
        
        # Buscar contrato
        contrato = None
        for c in self.contratos:
            if c['id'] == contrato_id:
                contrato = c
                break
        
        if not contrato:
            return
        
        # Llenar campos con datos del contrato
        self.limpiar_campos()
        
        self.entry_nombre.insert(0, contrato['nombre_equipo'])
        self.entry_serie.insert(0, contrato['serie'])
        self.entry_cantidad.insert(0, str(contrato['cantidad']))
        self.entry_horometro_inicial.insert(0, str(contrato['horometro_inicial']))
        self.entry_horas.insert(0, str(contrato['horas_contratadas']))
        self.entry_precio.insert(0, str(contrato['precio_hora']))
        self.entry_garantia.insert(0, str(contrato['garantia']))
        self.combo_pago.set(contrato['metodo_pago'])
        self.entry_cliente.insert(0, contrato['nombre_cliente'])
        self.entry_cedula.insert(0, contrato['cedula'])
        self.entry_telefono.insert(0, contrato['telefono'])
        self.entry_correo.insert(0, contrato['correo'])
        self.entry_area.insert(0, contrato['area_uso'])
        self.entry_fecha_entrega.insert(0, contrato['fecha_entrega'])
        self.entry_fecha_devolucion.insert(0, contrato['fecha_devolucion'])
        self.combo_combustible.set(contrato['nivel_combustible'])
        
        if contrato['alerta_mantenimiento']:
            self.check_mantenimiento.select()
        
        self.text_estado_entrega.insert("1.0", contrato['estado_entrega'])
        
        # Habilitar campos de devolución
        self.entry_horometro_final.configure(state="normal")
        self.text_estado_devolucion.configure(state="normal")
        self.boton_foto_recepcion.configure(state="normal")
        
        # Cambiar a pestaña de formulario
        self.tabs.set("Formulario de Registro")
        
        messagebox.showinfo("Contrato Seleccionado", 
                          f"Contrato {contrato_id} cargado. Complete los campos de devolución.")
    
    def verificar_alarmas(self):
        """Verifica si hay contratos vencidos y muestra alarmas"""
        ahora = datetime.now()
        alarmas = []
        
        for contrato in self.contratos:
            if contrato['estado'] == "ACTIVO" and not contrato['horometro_final']:
                try:
                    fecha_devolucion = datetime.strptime(contrato['fecha_devolucion'], "%Y-%m-%d %H:%M")
                    if ahora > fecha_devolucion:
                        alarmas.append(
                            f"⚠️ MORA: Equipo {contrato['nombre_equipo']} (Serie: {contrato['serie']}) - "
                            f"Cliente: {contrato['nombre_cliente']} - Venció: {contrato['fecha_devolucion']}"
                        )
                except ValueError:
                    continue
        
        if alarmas:
            texto_alarma = "  |  ".join(alarmas)
            self.banner_alarma.configure(text=texto_alarma)
            # Parpadeo
            self.parpadear_banner()
        else:
            self.banner_alarma.configure(text="")
        
        # Verificar cada 30 segundos
        self.root.after(30000, self.verificar_alarmas)
    
    def parpadear_banner(self):
        """Hace parpadear el banner de alarma"""
        color_actual = self.banner_alarma.cget("fg_color")
        nuevo_color = "#FF0000" if color_actual == "#8B0000" else "#8B0000"
        self.banner_alarma.configure(fg_color=nuevo_color)
        self.root.after(500, self.parpadear_banner)


def main():
    root = ctk.CTk()
    app = InventarioRentaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

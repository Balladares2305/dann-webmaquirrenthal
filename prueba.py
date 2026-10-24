import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import json
import os

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
                    self.contratos = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.contratos = []
        else:
            self.contratos = []
    
    def guardar_datos(self):
        """Guarda los datos en el archivo JSON"""
        with open(self.archivo_json, 'w', encoding='utf-8') as f:
            json.dump(self.contratos, f, indent=4, ensure_ascii=False)
    
    def construir_interfaz(self):
        """Construye toda la interfaz gráfica"""
        # Banner de alarmas
        self.banner_alarma = ctk.CTkLabel(
            self.root, 
            text="SISTEMA ESTABLE - SIN RETRASOS", 
            font=("Arial", 14, "bold"),
            fg_color="#1b4d3e",
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
        canvas = ctk.CTkScrollableFrame(self.tab_formulario)
        canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === IDENTIFICACIÓN DEL EQUIPO ===
        frame_equipo = ctk.CTkFrame(canvas)
        frame_equipo.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(frame_equipo, text="🏗️ IDENTIFICACIÓN DEL EQUIPO", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkLabel(frame_equipo, text="Nombre del Equipo:").pack(anchor="w", padx=10)
        self.entry_nombre = ctk.CTkEntry(frame_equipo, placeholder_text="Ej: Excavadora CAT 320")
        self.entry_nombre.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(frame_equipo, text="Serie del Equipo:").pack(anchor="w", padx=10)
        self.entry_serie = ctk.CTkEntry(frame_equipo, placeholder_text="Ej: CAT0320ABC123")
        self.entry_serie.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(frame_equipo, text="Cantidad de Equipos:").pack(anchor="w", padx=10)
        self.entry_cantidad = ctk.CTkEntry(frame_equipo, placeholder_text="Ej: 1")
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(frame_equipo, text="Horómetro Inicial del Motor (al entregar):").pack(anchor="w", padx=10)
        self.entry_horometro_inicial = ctk.CTkEntry(frame_equipo, placeholder_text="Ej: 1500")
        self.entry_horometro_inicial.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(frame_equipo, text="Horómetro Final del Motor (al recibir):").pack(anchor="w", padx=10)
        self.entry_horometro_final = ctk.CTkEntry(frame_equipo, placeholder_text="Se llena al devolver", state="disabled")
        self.entry_horometro_final.pack(fill="x", padx=10, pady=2)
        
        # === DATOS FINANCIEROS ===
        frame_financiero = ctk.CTkFrame(canvas)
        frame_financiero.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(frame_financiero, text="💰 DATOS FINANCIEROS", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkLabel(frame_financiero, text="Horas Contratadas a Rentar:").pack(anchor="w", padx=10)
        self.entry_horas = ctk.CTkEntry(frame_financiero, placeholder_text="Ej: 8")
        self.entry_horas.pack(fill="x", padx=10, pady=2)
        self.entry_horas.bind('<KeyRelease>', self.calcular_totales)
        
        ctk.CTkLabel(frame_financiero, text="Precio por Hora del Equipo ($):").pack(anchor="w", padx=10)
        self.entry_precio = ctk.CTkEntry(frame_financiero, placeholder_text="Ej: 50.00")
        self.entry_precio.pack(fill="x", padx=10, pady=2)
        self.entry_precio.bind('<KeyRelease>', self.calcular_totales)
        
        ctk.CTkLabel(frame_financiero, text="Garantía / Depósito de Seguridad ($):").pack(anchor="w", padx=10)
        self.entry_garantia = ctk.CTkEntry(frame_financiero, placeholder_text="Ej: 500.00")
        self.entry_garantia.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(frame_financiero, text="Método de Pago:").pack(anchor="w", padx=10)
        self.combo_pago = ctk.CTkComboBox(frame_financiero, values=["Efectivo", "Transferencia", "Tarjeta", "Crédito Interno"])
        self.combo_pago.set("Efectivo")
        self.combo_pago.pack(fill="x", padx=10, pady=2)
        
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
        
        ctk.CTkLabel(frame_cliente, text="👤 DATOS DEL CLIENTE", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
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
        
        ctk.CTkLabel(frame_fechas, text="📅 FECHAS Y CONTROL TÉCNICO", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkLabel(frame_fechas, text="Fecha/Hora de Entrega:").pack(anchor="w", padx=10)
        self.entry_fecha_entrega = ctk.CTkEntry(frame_fechas, placeholder_text="YYYY-MM-DD HH:MM")
        self.entry_fecha_entrega.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.entry_fecha_entrega.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(frame_fechas, text="Fecha/Hora Máxima de Devolución:").pack(anchor="w", padx=10)
        self.entry_fecha_devolucion = ctk.CTkEntry(frame_fechas, placeholder_text="YYYY-MM-DD HH:MM")
        self.entry_fecha_devolucion.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(frame_fechas, text="Nivel de Combustible de Entrega:").pack(anchor="w", padx=10)
        self.combo_combustible = ctk.CTkComboBox(frame_fechas, values=["Full", "1/2", "1/4"])
        self.combo_combustible.set("Full")
        self.combo_combustible.pack(fill="x", padx=10, pady=2)
        
        self.check_mantenimiento = ctk.CTkCheckBox(frame_fechas, text="⚠️ Alerta: Equipo supera 250 horas desde último servicio", text_color="orange")
        self.check_mantenimiento.pack(anchor="w", padx=10, pady=5)
        
        # === ESTADOS DE INSPECCIÓN ===
        frame_inspeccion = ctk.CTkFrame(canvas)
        frame_inspeccion.pack(fill="x", pady=5, padx=5)
        

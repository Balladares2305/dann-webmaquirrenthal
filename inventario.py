import json
import os
from tkinter import *
from tkinter import ttk, messagebox

ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventario.json")


class InventarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Inventario")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        self.productos = self.cargar_datos()

        self.crear_interfaz()
        self.actualizar_tabla()

    def cargar_datos(self):
        if os.path.exists(ARCHIVO_DATOS):
            try:
                with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def guardar_datos(self):
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(self.productos, f, indent=4, ensure_ascii=False)

    def crear_interfaz(self):
        # Frame de entrada de datos
        frame_entrada = LabelFrame(self.root, text="Agregar Producto", padx=10, pady=10)
        frame_entrada.pack(fill="x", padx=10, pady=5)

        Label(frame_entrada, text="Nombre:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_nombre = Entry(frame_entrada, width=25)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=2)

        Label(frame_entrada, text="Cantidad:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_cantidad = Entry(frame_entrada, width=25)
        self.entry_cantidad.grid(row=1, column=1, padx=5, pady=2)

        Label(frame_entrada, text="Precio:").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_precio = Entry(frame_entrada, width=25)
        self.entry_precio.grid(row=2, column=1, padx=5, pady=2)

        Button(frame_entrada, text="Agregar Producto", command=self.agregar_producto,
               bg="#4CAF50", fg="white", width=20).grid(row=0, column=2, rowspan=3, padx=10)

        # Frame de la tabla
        frame_tabla = Frame(self.root, padx=10, pady=5)
        frame_tabla.pack(fill="both", expand=True, padx=10)

        columnas = ("nombre", "cantidad", "precio", "subtotal")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)

        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("cantidad", text="Cantidad")
        self.tabla.heading("precio", text="Precio Unitario")
        self.tabla.heading("subtotal", text="Subtotal")

        self.tabla.column("nombre", width=250)
        self.tabla.column("cantidad", width=100, anchor="center")
        self.tabla.column("precio", width=120, anchor="e")
        self.tabla.column("subtotal", width=120, anchor="e")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tabla.bind("<<TreeviewSelect>>", self.on_select)

        # Frame de acciones
        frame_acciones = Frame(self.root, padx=10, pady=5)
        frame_acciones.pack(fill="x", padx=10)

        Label(frame_acciones, text="Nueva Cantidad:").pack(side="left")
        self.entry_nueva_cantidad = Entry(frame_acciones, width=10)
        self.entry_nueva_cantidad.pack(side="left", padx=5)

        Button(frame_acciones, text="Actualizar Stock", command=self.actualizar_stock,
               bg="#2196F3", fg="white").pack(side="left", padx=5)

        Button(frame_acciones, text="Eliminar Producto", command=self.eliminar_producto,
               bg="#f44336", fg="white").pack(side="left", padx=5)

        Button(frame_acciones, text="Calcular Valor Total", command=self.calcular_total,
               bg="#FF9800", fg="white").pack(side="right", padx=5)

        # Etiqueta de total
        self.label_total = Label(self.root, text="Valor Total del Inventario: $0.00",
                                 font=("Arial", 12, "bold"), pady=10)
        self.label_total.pack()

    def on_select(self, event):
        seleccion = self.tabla.selection()
        if seleccion:
            valores = self.tabla.item(seleccion[0], "values")
            self.entry_nueva_cantidad.delete(0, END)
            self.entry_nueva_cantidad.insert(0, valores[1])

    def agregar_producto(self):
        nombre = self.entry_nombre.get().strip()
        cantidad_str = self.entry_cantidad.get().strip()
        precio_str = self.entry_precio.get().strip()

        if not nombre or not cantidad_str or not precio_str:
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios.")
            return

        try:
            cantidad = int(cantidad_str)
            precio = float(precio_str)
            if cantidad < 0 or precio < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Cantidad y precio deben ser números positivos válidos.")
            return

        for producto in self.productos:
            if producto["nombre"].lower() == nombre.lower():
                messagebox.showinfo("Duplicado", f"El producto '{nombre}' ya existe. Usa 'Actualizar Stock'.")
                return

        self.productos.append({"nombre": nombre, "cantidad": cantidad, "precio": precio})
        self.guardar_datos()
        self.actualizar_tabla()
        self.limpiar_campos()
        messagebox.showinfo("Éxito", f"Producto '{nombre}' agregado correctamente.")

    def actualizar_stock(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona un producto de la tabla primero.")
            return

        nueva_cantidad_str = self.entry_nueva_cantidad.get().strip()
        try:
            nueva_cantidad = int(nueva_cantidad_str)
            if nueva_cantidad < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingresa una cantidad válida (entero positivo).")
            return

        nombre = self.tabla.item(seleccion[0], "values")[0]
        for producto in self.productos:
            if producto["nombre"] == nombre:
                producto["cantidad"] = nueva_cantidad
                break

        self.guardar_datos()
        self.actualizar_tabla()
        self.entry_nueva_cantidad.delete(0, END)
        messagebox.showinfo("Éxito", f"Stock de '{nombre}' actualizado a {nueva_cantidad}.")

    def eliminar_producto(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona un producto de la tabla primero.")
            return

        nombre = self.tabla.item(seleccion[0], "values")[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar el producto '{nombre}'?"):
            self.productos = [p for p in self.productos if p["nombre"] != nombre]
            self.guardar_datos()
            self.actualizar_tabla()
            self.entry_nueva_cantidad.delete(0, END)

    def calcular_total(self):
        total = sum(p["cantidad"] * p["precio"] for p in self.productos)
        self.label_total.config(text=f"Valor Total del Inventario: ${total:,.2f}")

    def actualizar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for producto in self.productos:
            subtotal = producto["cantidad"] * producto["precio"]
            self.tabla.insert("", "end", values=(
                producto["nombre"],
                producto["cantidad"],
                f"${producto['precio']:,.2f}",
                f"${subtotal:,.2f}"
            ))

    def limpiar_campos(self):
        self.entry_nombre.delete(0, END)
        self.entry_cantidad.delete(0, END)
        self.entry_precio.delete(0, END)
        self.entry_nombre.focus()


if __name__ == "__main__":
    root = Tk()
    app = InventarioApp(root)
    root.mainloop()

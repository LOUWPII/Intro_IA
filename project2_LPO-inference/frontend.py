import tkinter as tk
from tkinter import messagebox, scrolledtext, Button, Entry, Listbox, Label
from parser import parsear
from cnf_converter import convertir_a_fnc_paso_a_paso

class LogicInferenceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Motor de Inferencia en LPO")

        # Campo de texto para ingresar cláusulas
        Label(root, text="Ingresa una cláusula en LPO:").pack(pady=5)
        self.clause_entry = Entry(root, width=50)
        self.clause_entry.pack(pady=5)

        # Teclado virtual para LPO
        self.create_lpo_keyboard()

        # Botón para agregar cláusulas
        self.add_button = Button(root, text="Agregar", command=self.add_clause)
        self.add_button.pack(pady=5)

        # Lista de cláusulas ingresadas
        Label(root, text="Cláusulas ingresadas:").pack(pady=5)
        self.clauses_listbox = Listbox(root, width=50, height=10)
        self.clauses_listbox.pack(pady=5)

        # Botón para ejecutar inferencia
        self.execute_button = Button(root, text="Ejecutar Inferencia", command=self.execute_inference)
        self.execute_button.pack(pady=5)

        # Área de resultados
        Label(root, text="Resultado:").pack(pady=5)
        self.result_text = scrolledtext.ScrolledText(root, width=50, height=10)
        self.result_text.pack(pady=5)

        # Lista interna para almacenar cláusulas
        self.clauses = []

    def create_lpo_keyboard(self):
        """Crea un teclado virtual con símbolos de LPO."""
        keyboard_frame = tk.Frame(self.root)
        keyboard_frame.pack(pady=5)

        # Botones del teclado LPO
        buttons = [
            ("∀", "∀"), ("∃", "∃"), ("¬", "¬"), ("∧", "∧"),
            ("∨", "∨"), ("→", "→"), ("↔", "↔"), ("(", "("), (")", ")")
        ]

        for text, symbol in buttons:
            button = Button(keyboard_frame, text=text, command=lambda s=symbol: self.insert_symbol(s))
            button.pack(side=tk.LEFT, padx=2, pady=2)

    def insert_symbol(self, symbol):
        """Inserta un símbolo de LPO en el campo de texto."""
        self.clause_entry.insert(tk.END, symbol)

    def add_clause(self):
        """Agrega la cláusula ingresada a la lista."""
        texto_formula = self.clause_entry.get()
        if texto_formula:
            try:
                # Validamos que la fórmula se pueda parsear
                formula_ast = parsear(texto_formula)
                self.clauses.append(formula_ast)
                self.clauses_listbox.insert(tk.END, str(formula_ast))
                self.clause_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error de Sintaxis", f"No se pudo entender la fórmula: {e}")
        else:
            messagebox.showwarning("Advertencia", "Ingresa una cláusula válida.")

    def execute_inference(self):
        """Ejecuta el motor de inferencia con las cláusulas ingresadas."""
        if not self.clauses:
            messagebox.showwarning("Advertencia", "No hay cláusulas para ejecutar.")
            return

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "=== Conversión a FNC Paso a Paso ===\n\n")
        
        for i, formula in enumerate(self.clauses):
            self.result_text.insert(tk.END, f"Fórmula {i+1}:\n")
            pasos = convertir_a_fnc_paso_a_paso(formula)
            for nombre_paso, formula_str in pasos:
                self.result_text.insert(tk.END, f"  [{nombre_paso}]: {formula_str}\n")
            self.result_text.insert(tk.END, "\n" + "-"*40 + "\n\n")

        self.result_text.insert(tk.END, "Conversión finalizada con éxito.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogicInferenceGUI(root)
    root.mainloop()
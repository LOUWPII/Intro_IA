class VariableAleatoria:
    def __init__(self, nombre, estados, padres=None):
        self.nombre = nombre
        self.estados = estados          # Lista de strings
        self.padres = padres or []      # Lista de nombres de padres
        self.cpt = {}                   # Tabla de probabilidad condicional

    def __repr__(self):
        p = f"({','.join(self.padres)})" if self.padres else ""
        return f"{self.nombre}{p} -> ({','.join(self.estados)})"


class RedBayesiana:
    def __init__(self):
        self.variables = {}   # nombre -> VariableAleatoria
        self.orden = []       # Orden topológico

    def agregar_variable(self, var: VariableAleatoria):
        self.variables[var.nombre] = var
        if var.nombre not in self.orden:
            self.orden.append(var.nombre)

    def definir_cpt(self, nombre_var, cpt_dict):
        """cpt_dict: {(estado_padre1, estado_padre2, ...): {estado_hijo: prob}}
            Para variables sin padres: {(): {estado: prob}}
        """
        self.variables[nombre_var].cpt = cpt_dict


    def _ordenar_topologicamente(self):
        """Retorna una lista de nombres de variables ordenada topológicamente."""
        visitados = set()
        orden = []
        # Los padres quedan añadidos por delante de los hijos
        def dfs(nombre):
            if nombre in visitados:
                return
            visitados.add(nombre)
            for padre in self.variables[nombre].padres:
                dfs(padre)
            orden.append(nombre)

        for n in self.variables:
            dfs(n)
        return orden

    def probabilidad(self, evidencia: dict, consulta: dict) -> float:
        """Calcula P(consulta | evidencia) usando inferencia por enumeración."""
        orden = self._ordenar_topologicamente()
        ocultas = [v for v in orden
                if v not in consulta and v not in evidencia]

        def calcular_prob(estado):
            """Calcula P(estado) para un estado completo (asignación a todas las variables)."""
            estado_completo = {**estado, **evidencia, **consulta}
            p = 1.0
            # Recorremos las variables en orden topológico para asegurar que los padres ya estén asignados
            for nombre in orden:
                var = self.variables[nombre]
                clave_padres = tuple(estado_completo[padre] for padre in var.padres)
                try:
                    p *= var.cpt[clave_padres][estado_completo[nombre]]
                except KeyError:
                    return 0.0
            return p

        def sumar_ocultas(cubiertas, estado):
            """Recursivamente suma sobre todas las combinaciones de estados de las variables ocultas."""
            if cubiertas >= len(ocultas):
                return calcular_prob(estado)
            nombre = ocultas[cubiertas]
            total = 0.0
            # Para cada estado posible de la variable oculta actual, asignamos ese estado y seguimos cubriendo las siguientes ocultas
            for val in self.variables[nombre].estados:
                estado[nombre] = val
                total += sumar_ocultas(cubiertas + 1, estado)
            del estado[nombre]
            return total

        return sumar_ocultas(0, {})
    

    def distribucion_completa(self, evidencia: dict, var_consulta: str) -> dict:
        """Retorna la distribución P(var_consulta | evidencia) para todos sus estados."""
        resultado = {}
        # Para cada estado posible de la variable de consulta, calculamos su probabilidad dado la evidencia
        for estado in self.variables[var_consulta].estados:
            resultado[estado] = self.probabilidad(evidencia, {var_consulta: estado})
        
        suma_total = sum(resultado.values())
        alfa = 1 / suma_total
        
        return {estado: prob * alfa for estado, prob in resultado.items()}
        
    def mostrar_estructura(self):    
        """
        Recorre la red desde las raíces mostrando
        los predecesores de cada nodo en formato árbol.
        Retorna el string además de imprimirlo.
        """
        orden = self._ordenar_topologicamente()

        raices = [n for n in orden if not self.variables[n].padres]

        lineas = []
        lineas.append(f"Cantidad de Variables: {len(self.variables)}")
        lineas.append(f"Raíces:    {', '.join(raices)}")
        lineas.append("─" * 32)

        visitados = set()

        def _imprimir_nodo(nombre, prefijo, es_ultimo):
            """Imprime el nodo actual y luego recursivamente sus hijos."""
            var = self.variables[nombre]
            conector = "└─ " if es_ultimo else "├─ "
            estados  = "(" + " | ".join(var.estados) + ")"
            lineas.append(prefijo + conector + nombre + " " + estados)

            if var.padres:
                ext = prefijo + ("   " if es_ultimo else "│  ")
                lineas.append(ext + "   Predecesores: " + " ← ".join(var.padres))

            visitados.add(nombre)

            hijos = [
                n for n in orden
                if nombre in self.variables[n].padres and n not in visitados
            ]
            ext = prefijo + ("   " if es_ultimo else "│  ")
            # Para cada hijo, llamamos recursivamente para imprimir su subárbol
            for i, hijo in enumerate(hijos):
                _imprimir_nodo(hijo, ext, i == len(hijos) - 1)

        # Comenzamos la impresión desde las raíces, cada una con un prefijo vacío
        for i, raiz in enumerate(raices):
            _imprimir_nodo(raiz, "", i == len(raices) - 1)

        resultado = "\n".join(lineas)
        print(resultado)
        return resultado
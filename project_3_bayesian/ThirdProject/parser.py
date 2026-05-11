from classes import VariableAleatoria,RedBayesiana
import re

def parsear_definicion_variable(texto):
    """
    Parsea: A(B,C) -> (D,E,F)  o  A -> (D,E,F)
    Retorna: VariableAleatoria
    """
    texto = texto.strip()
    # El patrón busca un nombre seguido opcionalmente de padres entre paréntesis, luego '->' y finalmente los estados entre paréntesis
    patron = r'^(\w+)(?:\(([^)]*)\))?\s*->\s*\(([^)]+)\)$'
    m = re.match(patron, texto)
    # Si no coincide con el patrón, lanzamos un error indicando el formato esperado
    if not m:
        raise ValueError(
            f"Formato inválido: '{texto}'\n"
            "Usa: NombreVar(Padre1,Padre2) -> (Estado1,Estado2,Estado3)\n"
            "O sin padres: NombreVar -> (Estado1,Estado2)"
        )
    nombre = m.group(1).strip()
    padres_str = m.group(2)
    estados_str = m.group(3)

    padres = [p.strip() for p in padres_str.split(',') if p.strip()] if padres_str else []
    estados = [e.strip() for e in estados_str.split(',') if e.strip()]

    # Validamos que se hayan definido al menos 2 estados para la variable, ya que una variable con menos de 2 estados no es útil en una red bayesiana
    if len(estados) < 2:
        raise ValueError("La variable debe tener al menos 2 estados.")

    return VariableAleatoria(nombre, estados, padres)


def parsear_cpt_texto(texto_cpt, variables):
    """Parsea líneas de CPTs en formato: P(Var|Padre1=Val1,Padre2=Val2) = p1, p2, p3"""
    cpts = {}
    lineas = [l.strip() for l in texto_cpt.strip().splitlines() if l.strip()]

    # Recorremos cada línea buscando aquellas que definan CPTs, identificadas por comenzar con 'P('
    for linea in lineas:
        # Si la línea no comienza con 'P(', la ignoramos ya que no corresponde a una definición de CPT
        if not linea.startswith('P('):
            continue

        cierre = linea.index(')')          # Posición del ')' que cierra P(...)
        idx_eq = linea.index('=', cierre)  # Primer '=' después del cierre

        lhs = linea[:idx_eq].strip()
        rhs = linea[idx_eq + 1:].strip()

        probs = [float(x.strip()) for x in rhs.split(',')]

        # Usamos una expresión regular para extraer el nombre de la variable de consulta y las condiciones (padres y sus valores) si existen
        m = re.match(r'^P\((\w+)(?:\|([^)]*))?\)$', lhs)
        # Si no coincide con el patrón, lanzamos un error indicando el formato esperado para las líneas de CPT
        if not m:
            raise ValueError(f"Formato inválido en cabecera: {lhs}")

        var_nombre = m.group(1).strip()
        condicion_str = m.group(2)

        # Validamos que la variable de consulta esté definida en el conjunto de variables, ya que no podemos asignar probabilidades a una variable que no existe en la red bayesiana
        if var_nombre not in variables:
            raise ValueError(f"Variable '{var_nombre}' no definida.")

        var = variables[var_nombre]

        # Validamos que el número de probabilidades proporcionadas coincida con el número de estados de la variable, ya que cada estado debe tener una probabilidad asociada
        if len(probs) != len(var.estados):
            raise ValueError(
                f"La variable '{var_nombre}' tiene {len(var.estados)} estados "
                f"pero se dieron {len(probs)} probabilidades en: {linea}"
            )

        # Si hay condiciones (padres), las parseamos para construir la clave del CPT. Si no hay condiciones, la clave será una tupla vacía.
        if condicion_str:
            partes = [p.strip() for p in condicion_str.split(',')]
            clave = tuple()
            # Para cada parte de la condición, esperamos un formato 'Padre=Valor'. Si no se cumple, lanzamos un error indicando el formato esperado para las condiciones en las líneas de CPT
            for parte in partes:
                if '=' not in parte:
                    raise ValueError(f"Condición mal formada: {parte}")
                pnombre, pestado = parte.split('=', 1)
                clave += (pestado.strip(),)
        else:
            clave = ()

        if var_nombre not in cpts:
            cpts[var_nombre] = {}

        # Asignamos las probabilidades a la variable correspondiente en el CPT, usando la clave construida a partir de las condiciones. Esto nos permite luego acceder a las probabilidades según los estados de los padres.
        cpts[var_nombre][clave] = {
            estado: prob for estado, prob in zip(var.estados, probs)
        }

    return cpts
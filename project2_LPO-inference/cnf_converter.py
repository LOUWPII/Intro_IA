from structures import *

def eliminar_bicondicional(formula):
    """
    Paso 1: Eliminar doble implicación (A ↔ B) => (A → B) ∧ (B → A)
    Recursivamente busca el operador ↔ y lo reemplaza por una conjunción de implicaciones.
    """
    if isinstance(formula, Predicado):
        return formula
    if isinstance(formula, Not):
        return Not(eliminar_bicondicional(formula.formula))
    if isinstance(formula, And):
        return And(eliminar_bicondicional(formula.izquierda), eliminar_bicondicional(formula.derecha))
    if isinstance(formula, Or):
        return Or(eliminar_bicondicional(formula.izquierda), eliminar_bicondicional(formula.derecha))
    if isinstance(formula, Implica):
        return Implica(eliminar_bicondicional(formula.izquierda), eliminar_bicondicional(formula.derecha))
    if isinstance(formula, DobleImplica):
        izq = eliminar_bicondicional(formula.izquierda)
        der = eliminar_bicondicional(formula.derecha)
        return And(Implica(izq, der), Implica(der, izq))
    if isinstance(formula, ParaTodo):
        return ParaTodo(formula.variable, eliminar_bicondicional(formula.formula))
    if isinstance(formula, Existe):
        return Existe(formula.variable, eliminar_bicondicional(formula.formula))
    return formula

def eliminar_implicacion(formula):
    """
    Paso 2: Eliminar implicación (A → B) => (¬A ∨ B)
    Transforma cada flecha en un 'O' donde el antecedente está negado.
    """
    if isinstance(formula, Predicado):
        return formula
    if isinstance(formula, Not):
        return Not(eliminar_implicacion(formula.formula))
    if isinstance(formula, And):
        return And(eliminar_implicacion(formula.izquierda), eliminar_implicacion(formula.derecha))
    if isinstance(formula, Or):
        return Or(eliminar_implicacion(formula.izquierda), eliminar_implicacion(formula.derecha))
    if isinstance(formula, Implica):
        izq = eliminar_implicacion(formula.izquierda)
        der = eliminar_implicacion(formula.derecha)
        return Or(Not(izq), der)
    if isinstance(formula, ParaTodo):
        return ParaTodo(formula.variable, eliminar_implicacion(formula.formula))
    if isinstance(formula, Existe):
        return Existe(formula.variable, eliminar_implicacion(formula.formula))
    return formula

def mover_negacion(formula):
    """
    Paso 3: Forma Normal de Negación (NNF)
    Aplica las Leyes de De Morgan para mover las negaciones lo más profundo posible (hacia los predicados).
    ¬(A ∧ B) => ¬A ∨ ¬B
    ¬(A ∨ B) => ¬A ∧ ¬B
    ¬∀x P(x) => ∃x ¬P(x)
    ¬∃x P(x) => ∀x ¬P(x)
    ¬¬A => A (Eliminación de doble negación)
    """
    if isinstance(formula, Predicado):
        return formula
    if isinstance(formula, Not):
        hijo = formula.formula
        # Caso de doble negación: ¬¬A => A
        if isinstance(hijo, Not):
            return mover_negacion(hijo.formula)
        
        # De Morgan para Conjunción: ¬(A ∧ B) => ¬A ∨ ¬B
        if isinstance(hijo, And):
            return Or(mover_negacion(Not(hijo.izquierda)), mover_negacion(Not(hijo.derecha)))
        
        # De Morgan para Disyunción: ¬(A ∨ B) => ¬A ∧ ¬B
        if isinstance(hijo, Or):
            return And(mover_negacion(Not(hijo.izquierda)), mover_negacion(Not(hijo.derecha)))
        
        # De Morgan para Cuantificador Universal: ¬∀x P(x) => ∃x ¬P(x)
        if isinstance(hijo, ParaTodo):
            return Existe(hijo.variable, mover_negacion(Not(hijo.formula)))
        
        # De Morgan para Cuantificador Existencial: ¬∃x P(x) => ∀x ¬P(x)
        if isinstance(hijo, Existe):
            return ParaTodo(hijo.variable, mover_negacion(Not(hijo.formula)))
        
        # Si es un predicado, simplemente devolvemos ¬P
        return Not(mover_negacion(hijo))
    
    # Procesar subfórmulas de forma recursiva
    if isinstance(formula, And):
        return And(mover_negacion(formula.izquierda), mover_negacion(formula.derecha))
    if isinstance(formula, Or):
        return Or(mover_negacion(formula.izquierda), mover_negacion(formula.derecha))
    if isinstance(formula, ParaTodo):
        return ParaTodo(formula.variable, mover_negacion(formula.formula))
    if isinstance(formula, Existe):
        return Existe(formula.variable, mover_negacion(formula.formula))
    return formula

#def estandarizar variables
#def skolemizar   
#def eliminaar cuantificador universal

def distribuir_or(formula):
    """
    Paso 7: Propiedad Distributiva (FNC Final)
    Mueve los operadores ∨ hacia adentro de los ∧.
    Regla: A ∨ (B ∧ C)  =>  (A ∨ B) ∧ (A ∨ C)
    Esto nos garantiza que la fórmula final sea una conjunción de disyunciones.
    """
    if isinstance(formula, Predicado):
        return formula
    if isinstance(formula, Not):
        return formula  
    if isinstance(formula, And):
        return And(distribuir_or(formula.izquierda), distribuir_or(formula.derecha))
    
    if isinstance(formula, Or):
        izq = distribuir_or(formula.izquierda)
        der = distribuir_or(formula.derecha)
        
        # Si la derecha es un AND: A ∨ (B ∧ C)
        if isinstance(der, And):
            return And(distribuir_or(Or(izq, der.izquierda)), distribuir_or(Or(izq, der.derecha)))
        
        # Si la izquierda es un AND: (A ∧ B) ∨ C
        if isinstance(izq, And):
            return And(distribuir_or(Or(izq.izquierda, der)), distribuir_or(Or(izq.derecha, der)))
        
        return Or(izq, der)
    
    return formula

def convertir_a_fnc_paso_a_paso(formula_inicial):
    """
    Realiza la conversión completa a FNC y devuelve la lista de pasos detallada.
    Solo añade los pasos que produzcan un cambio real en la cadena de texto de la fórmula.
    """
    pasos = []
    
    # El estado inicial siempre se muestra
    f_actual = formula_inicial
    pasos.append(("Original", str(f_actual)))
    
    # Definición de la secuencia de transformaciones
    transformaciones = [
        ("Eliminar ↔", eliminar_bicondicional),
        ("Eliminar →", eliminar_implicacion),
        ("Mover ¬", mover_negacion),
        #estandarizar variables
        #skolemizar   
        #eliminaar cuantificador universal
        ("Distribución (FNC)", distribuir_or)
    ]
    
    for nombre, func in transformaciones:
        f_previa_str = str(f_actual)
        f_actual = func(f_actual)
        f_actual_str = str(f_actual)
        
        # Solo se registra el paso si hubo una transformación visual
        if f_actual_str != f_previa_str:
            pasos.append((nombre, f_actual_str))
    
    # Siempre incluimos un paso final que resuma el resultado como FNC
    # Si el último paso registrado fue la Distribución, ya está claro.
    # Si no, añadimos explícitamente el Resultado FNC.
    if pasos[-1][0] != "Distribución (FNC)":
        if pasos[-1][0] == "Original":
            # Si la fórmula ya estaba en FNC
            pasos.append(("Resultado FNC", str(f_actual)))
        else:
            # Renombramos o añadimos el paso final
            ultimo_nombre, ultimo_txt = pasos.pop()
            pasos.append((f"{ultimo_nombre} -> FNC", ultimo_txt))

    return pasos

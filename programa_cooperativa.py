from openai import OpenAI
import os

# Configuración del cliente local de LM Studio
client = OpenAI(
    base_url="http://localhost:1234/v1", 
    api_key="lm-studio"
)

# Factores de emisión (MCI): Kg de CO2 evitados por cada Kg de material reciclado
# (Valores aproximados de referencia)
FACTORES_EMISION = {
    "PET": 2.35,
    "Carton": 0.17,
    "Aluminio": 12.75
}

def limpiar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def esperar_y_limpiar():
    input("\nPresiona Enter para continuar...")
    limpiar_terminal()

# ==========================================
# IA: Interpretar Mitigación de Carbono (MCI)
# ==========================================
def interpretar_mci_con_ia(co2_evitado):
    """
    Envía el total de CO2 mitigado al modelo local para traducirlo a una analogía.
    """
    mensaje_sistema = (
        "Eres un experto en sostenibilidad comunicando logros ambientales. "
        "Tu objetivo es tomar una cantidad de CO2 mitigado (en kilogramos) y traducirla a "
        "una analogía sencilla, inspiradora y fácil de imaginar para el usuario común. "
        "Usa ejemplos como número de árboles plantados, días de electricidad de una casa, "
        "o kilómetros no recorridos por un coche. Responde en un solo párrafo corto, sin usar lenguaje técnico."
    )
    
    mensaje_usuario = f"Nuestra cooperativa acaba de lograr una Mitigación de Intensidad de Carbono (MCI) de {co2_evitado} kg de CO2. ¿A qué equivale esto?"
    
    try:
        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": mensaje_sistema},
                {"role": "user", "content": mensaje_usuario}
            ],
            temperature=0.6, # Temperatura media para permitir algo de creatividad en la analogía
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"(La IA local no está disponible en este momento. Asegúrate de iniciar el servidor. Error: {e})"
    
# ==========================================
# "Inventario" - diccionario
# ==========================================
inventario = {"PET":[1000, 2512],
              "Carton":[1720, 711],
              "Aluminio":[707, 6486]}

# ==========================================
# Agregar elementos al inventario
# ==========================================
def add_inventario():
    opciones = list(inventario.keys())
    cont = 1
    for key in opciones:
        print(f"{cont}. {key}")
        cont += 1
    
    # Solicitar el material
    try:
        entrada = input("[?] Que material desea agregar: ")
        material = int(entrada)
        
        if material < 1 or material > len(opciones):
            print(f"[!] Valor invalido, debe ser un numero entre 1 y {len(opciones)}. \n")
            return add_inventario()
            
    except ValueError:
        print(f"[!] ERROR: Por favor solo ingrese el numero de la opcion. \n")
        return add_inventario()

    # Solicitar peso del material
    peso_entrada = input("Escriba el valor del peso en KG a ingresar: ")
    
    try:
        peso = int(peso_entrada)
        nombre_material = opciones[material -1]
        inventario[nombre_material][0] += peso
        print(f"\n[!] Se agregaron {peso}KG, ahora hay {inventario[nombre_material][0]}KG de {nombre_material}\n")
        
    except ValueError:
        print("[!] Peso inválido. Operación cancelada.\n")
        return add_inventario()

# ==========================================
# Mostrar inventario
# ==========================================
def mostrar_inventario():
    print("\n" + "=" * 90)
    print("INVENTARIO ACTUAL DE LA COOPERATIVA")
    print("=" * 90)
    print(f"{'Material':<20} {'Peso (KG)':<15} {'Valor/KG ($)':<20} {'Valor Total ($)':<20}")
    print("-" * 90)
    
    # Recorrer el inventario y mostrar cada material
    for material, datos in inventario.items():
        peso = datos[0]
        precio_unitario = datos[1]
        valor_total = peso * precio_unitario
        
        print(f"{material:<20} {peso:<15} ${precio_unitario:<19,.2f} ${valor_total:,.2f}")
    
    print("=" * 90)
    
    # Calcular totales
    peso_total = sum(datos[0] for datos in inventario.values())
    valor_total_inventario = sum(datos[0] * datos[1] for datos in inventario.values())
    
    print(f"{'TOTAL':<20} {peso_total:<15} {'':<20} ${valor_total_inventario:,.2f}")
    print("=" * 90 + "\n")

# ==========================================
# Cargar el camion (Problema de la Mochila Fraccionaria)
# ==========================================
def cargar_camion():
    CAPACIDAD_CAMION = 1000  # KG
    
    # Crear lista con información de cada material
    materiales_valor = []
    for material, datos in inventario.items():
        peso_disponible = datos[0]
        precio_unitario = datos[1]
        valor_por_kg = precio_unitario  # El valor por kg es directamente el precio
        
        if peso_disponible > 0:
            materiales_valor.append({
                'nombre': material,
                'peso_disponible': peso_disponible,
                'valor_por_kg': valor_por_kg,
                'precio_unitario': precio_unitario
            })
    
    # Si no hay material disponible
    if not materiales_valor:
        print("\n[!] No hay material disponible en el inventario para cargar.\n")
    
    # Ordenar por valor por kg (mayor primero) 
    for i in range(1, len(materiales_valor)):
        key = materiales_valor[i]
        j = i - 1
        # Comparar y desplazar elementos (orden descendente)
        while j >= 0 and materiales_valor[j]['valor_por_kg'] < key['valor_por_kg']:
            materiales_valor[j + 1] = materiales_valor[j]
            j -= 1
        materiales_valor[j + 1] = key
    
    # Mostrar plan de carga recomendado
    print("\n" + "=" * 90)
    print("CARGA ÓPTIMA DEL CAMIÓN (Problema de la Mochila Fraccionaria)")
    print("=" * 90)
    print(f"Capacidad del camión: {CAPACIDAD_CAMION} KG")
    print(f"Estrategia: Priorizar materiales con mayor valor por KG\n")
    
    print(f"{'Material':<20} {'Valor/KG ($)':<20} {'Plan de Carga (KG)':<20}")
    print("-" * 90)
    
    # Calcular la carga óptima
    carga_planificada = {}
    peso_restante = CAPACIDAD_CAMION
    
    for material in materiales_valor:
        nombre = material['nombre']
        peso_disp = material['peso_disponible']
        valor_kg = material['valor_por_kg']
        
        # Cargar la cantidad mínima entre lo disponible y lo que falta
        peso_a_cargar = min(peso_disp, peso_restante)
        
        if peso_a_cargar > 0:
            carga_planificada[nombre] = peso_a_cargar
            peso_restante -= peso_a_cargar
            print(f"{nombre:<20} ${valor_kg:<19,.2f} {peso_a_cargar:<20}")
    
    print("-" * 90)
    print(f"{'TOTAL A CARGAR':<20} {'':<20} {CAPACIDAD_CAMION - peso_restante:<20}")
    print("=" * 90)
    
    # Calcular ganancia
    ganancia_total = 0
    for nombre, peso_cargado in carga_planificada.items():
        # Encontrar el precio unitario del material
        for material in materiales_valor:
            if material['nombre'] == nombre:
                ganancia_total += peso_cargado * material['precio_unitario']
                break
    
    print(f"\nGanancia estimada: ${ganancia_total:,.2f}\n")
    
    # Confirmación del usuario
    confirmacion = input("¿Deseas proceder con la carga del camión? (si/no): ").strip().lower()
    
    if confirmacion == 'si' or confirmacion == 's':
        # Actualizar inventario
        for material, peso_cargado in carga_planificada.items():
            inventario[material][0] -= peso_cargado
        
        print("\n" + "=" * 90)
        print("CARGA REALIZADA EXITOSAMENTE")
        print("=" * 90)
        print(f"Se cargaron {CAPACIDAD_CAMION - peso_restante} KG al camión")
        print(f"Ganancia por la carga: ${ganancia_total:,.2f}\n")
        
        print("Calculando Mitigación de Intensidad de Carbono (MCI)...")
        mci_total = 0
        for material, peso_cargado in carga_planificada.items():
            factor = FACTORES_EMISION.get(material, 0)
            mci_total += peso_cargado * factor
            
        print(f"MCI Total: {mci_total:,.2f} kg de CO2 evitados.")
        print("Generando interpretación ambiental con IA (esto puede tardar unos segundos)...\n")
        
        # Llamar a la IA
        analogia_ia = interpretar_mci_con_ia(mci_total)
        
        print("🌍 IMPACTO AMBIENTAL LOGRADO 🌍")
        print("-" * 90)
        print(analogia_ia)
        print("-" * 90 + "\n")
        
        # Mostrar inventario actualizado
        print("INVENTARIO DESPUÉS DE LA CARGA:")
        print("-" * 90)
        mostrar_inventario()
    else:
        print("\n[!] Carga cancelada. El inventario permanece sin cambios.\n")

        
# ==========================================
# Menu 
# ==========================================

def menu():
    while True:
        # ESTRUCTURA DE LAS OPCIONES
        print("=" * 37)
        print("ADMINISTRACION COOPERATIVA DE RECICLAJE") # [!] posible cambio del nombre del menu
        print("=" * 37)
        print("1. Agregar material al inventario.")
        print("2. Ver inventario en la cooperativa.")
        print("3. Cargar camion para venta.")
        print("4. Salir del programa.")
        print("-" * 37)
        print("")
        
        seleccion = int(input("Seleccione una opcion (1-4): "))
        
        try:    
            # opcion 1 (agregar elemento)
            if seleccion == 1:
                add_inventario()
                print()
            # opcion 2 (ver inventarrio)
            if seleccion == 2:
                mostrar_inventario()
                print()
            # opcion 3 (mejor carga)
            if seleccion == 3:
                cargar_camion()
                print()
            # opcion 4 (salir del programa)
            if seleccion == 4:
                print("Saliendo...")
                print("Programa terminado")
                break
        except KeyboardInterrupt:
            print("\nSe detectó una interrupción externa.")
        except:
            print("[!] Ingrese una opcion valida (1-4)")
        esperar_y_limpiar()

if __name__ == "__main__":
    menu()

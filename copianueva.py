from flask import Flask, request, jsonify, render_template
import random
import matplotlib.pyplot as plt

app = Flask(__name__)

class TareaDomestica:
    def __init__(self, nombre):
        self.nombre = nombre

class Miembro:
    def __init__(self, nombre, preferencias, disponibilidad, habilidades):
        self.nombre = nombre
        self.preferencias = preferencias
        self.disponibilidad = disponibilidad
        self.habilidades = habilidades

class Cromosoma:
    def __init__(self, num_miembros, tareas, dias, franjas_horarias): #Recibe 4 parametros que representaran el cromosoma
        self.asignacion = [] #se crea una lista vacia, para almacenar las asignaciones de tarea para todos lo miembros
        for _ in range(num_miembros): #Genera una secuencia de numeros desde 0 hasta el numero de miembros
            miembro_asignacion = [] # Se inicializa una nueva lista vacia, que almacenara las asignacionaciones de un solo miembro
            for _ in range(dias): # Bucle que se ejecuta una vez por cada dia de la semana
                dia_asignacion = [None] * franjas_horarias # Se crea lista de una longitud de franjas horarias, donde indica que cada franja no hay tareas
                miembro_asignacion.append(dia_asignacion) # Contiene la lista de los dias asignado para cada miembro, representando las franjas horarias de ese cada dia
            self.asignacion.append(miembro_asignacion) # Lista que representa las asignaciones de tareas de todo los miembros
        self.fitness = 0 # Se inicializa en 0 para despues ir aumentando o restando de acuerdo a las asignaciones si son correctas y incorrectas, lo cual nos permite comparar con diferentes cromosomas para indicar cual es la mejor solucion

    def generar_aleatorio(self, miembros, tareas): #Metodo que genera una asignacion aleatoria de tareas a los miembros
        tareas_pendientes = self.preparar_tareas(tareas) #Llamada del metodo para obtener todas las tareas pendientes, no asignadas
        while tareas_pendientes:
            tarea = tareas_pendientes.pop(0)
            miembros_preferidos = [miembro for miembro in miembros if tarea.nombre in miembro.preferencias] #Lista de miembros que prefieren la tarea actual
            if miembros_preferidos:
                posibles_asignaciones = self.encontrar_posibles_asignaciones(miembros_preferidos)
            else:
                posibles_asignaciones = self.encontrar_posibles_asignaciones(miembros)
            if posibles_asignaciones: #Verifica si hay al menos una posible asignación para la tarea actual
                miembro, dia, franja = random.choice(posibles_asignaciones)
                self.asignar_tarea(miembro, dia, franja, tarea, miembros) 

    def preparar_tareas(self, tareas): 
        tareas_pendientes = tareas[:] 
        random.shuffle(tareas_pendientes)
        return tareas_pendientes

    def encontrar_posibles_asignaciones(self, miembros):
        posibles_asignaciones = []
        for miembro in miembros:
            for dia in range(len(self.asignacion[0])):
                for franja in range(len(self.asignacion[0][0])): #Itera sobre cada franja horaria del dia y devuelve el numero de franjas horarias
                    if miembro.disponibilidad[dia * 24 + franja]: #Verifica si el miembro esta disponible en esa franja horaria
                        posibles_asignaciones.append((miembro, dia, franja)) 
        return posibles_asignaciones

    def asignar_tarea(self, miembro, dia, franja, tarea, miembros):
        self.asignacion[miembros.index(miembro)][dia][franja] = tarea #Asigna la tarea al miembro en la franja horaria del dia
        

def inicializar_poblacion(tamano_poblacion, miembros, tareas, dias, franjas_horarias):
    poblacion = [] 
    for _ in range(tamano_poblacion): 
        cromosoma = Cromosoma(len(miembros), tareas, dias, franjas_horarias) # cada iteración crea un cromosoma
        cromosoma.generar_aleatorio(miembros, tareas) # genera un cromosoma aleatorio asignando tareas a los miembros
        poblacion.append(cromosoma)
    return poblacion 

def calcular_fitness(cromosoma, miembros, tareas):
    fitness = 0 
    for i, miembro in enumerate(miembros): 
        tareas_asignadas = [tarea for dia in cromosoma.asignacion[i] for tarea in dia if tarea] #Lista de tareas asignadas al miembro
        preferencias_cumplidas = sum(1 for tarea in tareas_asignadas if tarea.nombre in miembro.preferencias) #Cuenta cuantas preferencias se han cumplido
        fitness += preferencias_cumplidas * 2 #Aumenta el fitness por cada preferencia cumplida
        habilidad_total = sum(miembro.habilidades.get(tarea.nombre, 0.5) for tarea in tareas_asignadas) 
        fitness += habilidad_total #Aumenta el fitness por la habilidad total
        for dia in range(len(cromosoma.asignacion[i])): #Itera sobre los dias de la semana
            for franja in range(len(cromosoma.asignacion[i][dia])): #Itera sobre las franjas horarias del dia  
                tarea = cromosoma.asignacion[i][dia][franja] #Obtiene la tarea
                if tarea:
                    if miembro.disponibilidad[dia * 24 + franja]: 
                        fitness += 1 
                    else:
                        fitness -= 10
    num_tareas_por_miembro = [sum(1 for dia in asignacion for tarea in dia if tarea) for asignacion in cromosoma.asignacion]
    desbalance = max(num_tareas_por_miembro) - min(num_tareas_por_miembro)
    fitness -= desbalance * 5  # Penalización por desbalance

    return fitness

def seleccion_torneo(poblacion, tamano_torneo=3):
    seleccionados = random.sample(poblacion, tamano_torneo) 
    return max(seleccionados, key=lambda x: x.fitness) #Retorna el cromosoma con el mejor fitness

def cruce(padre1, padre2):
    num_miembros = len(padre1.asignacion) #Obtiene el numero de miembros
    num_dias = len(padre1.asignacion[0]) #Obtiene el numero de dias
    num_franjas = len(padre1.asignacion[0][0]) #Obtiene el numero de franjas horarias
    hijo = Cromosoma(num_miembros, [], num_dias, num_franjas) #Crea un nuevo cromosoma hijo, con las mismas dimensiones que los padres pero vaios
    punto_cruce = random.randint(0, num_miembros - 1) #Selecciona un punto de cruce aleatorio
    for i in range(num_miembros):
        if i < punto_cruce: 
            hijo.asignacion[i] = [dia[:] for dia in padre1.asignacion[i]] #Copia las asignaciones del padre 1 al hijo hasta el punto de cruce
        else:
            hijo.asignacion[i] = [dia[:] for dia in padre2.asignacion[i]] #Copia las asignaciones del padre 2 al hijo despues del punto de cruce
    return hijo

def mutacion(cromosoma, tasa_mutacion, tareas, miembros):
    for i in range(len(cromosoma.asignacion)): #itera sobre los miembros
        for j in range(len(cromosoma.asignacion[i])): #itera sobre los dias de la semana para cada miembro
            for k in range(len(cromosoma.asignacion[i][j])):#itera sobre las franjas horarias del dia para cada miembro
                if random.random() < tasa_mutacion: #Verifica si se realiza la mutación
                    if miembros[i].disponibilidad[j * 24 + k]: #Verifica si el miembro esta disponible en esa franja horaria
                        cromosoma.asignacion[i][j][k] = random.choice([None] + tareas) #Asigna una tarea aleatoria al miembro en esa franja horaria

def poda(poblacion, tamano_maximo): 
    return sorted(poblacion, key=lambda x: x.fitness, reverse=True)[:tamano_maximo] #Ordena la población de acuerdo al fitness y selecciona los mejores cromosomas


def algoritmo_genetico(miembros, tareas, dias, franjas_horarias, tamano_poblacion, generaciones, tasa_mutacion):
    poblacion = inicializar_poblacion(tamano_poblacion, miembros, tareas, dias, franjas_horarias)
    aptitud_mejor = []
    
    for _ in range(generaciones):
        for cromosoma in poblacion:
            cromosoma.fitness = calcular_fitness(cromosoma, miembros, tareas)
        poblacion = poda(poblacion, tamano_poblacion)
        nueva_poblacion = poblacion[:2]
        
        while len(nueva_poblacion) < tamano_poblacion:
            padre1 = seleccion_torneo(poblacion)
            padre2 = seleccion_torneo(poblacion)
            hijo = cruce(padre1, padre2)
            mutacion(hijo, tasa_mutacion, tareas, miembros)
            nueva_poblacion.append(hijo)
        poblacion = poda(nueva_poblacion, tamano_poblacion)
        
        mejor_cromosoma = max(poblacion, key=lambda x: x.fitness)
        aptitud_mejor.append(mejor_cromosoma.fitness)
    
    return max(poblacion, key=lambda x: x.fitness), aptitud_mejor

@app.route('/')
def index():
    return render_template('index.html')

def graficar_aptitud(aptitudes_mejor):
    plt.plot(aptitudes_mejor)
    plt.xlabel('Generación')
    plt.ylabel('Aptitud del Mejor')
    plt.title('Aptitud del Mejor en Cada Generación')
    plt.grid(True)
    plt.show(block=True)
    
@app.route('/api/generar_planificacion', methods=['POST'])
def generar_planificacion():
    data = request.get_json()
    miembros = [Miembro(m['nombre'], m['preferencias'], m['disponibilidad'], m['habilidades']) for m in data['miembros']]
    tareas = [TareaDomestica(t['nombre']) for t in data['tareas']]
    mejor_solucion, aptitud_mejor = algoritmo_genetico(miembros, tareas, data['dias'], data['franjas_horarias'], data['tamano_poblacion'], data['generaciones'], data['tasa_mutacion'])
    resultado = []
    for dia in range(data['dias']):
        for franja in range(data['franjas_horarias']):
            for i, miembro in enumerate(miembros):
                tarea = mejor_solucion.asignacion[i][dia][franja]
                if tarea:
                    resultado.append({
                        'dia': dia,
                        'hora': franja,
                        'tarea': tarea.nombre,
                        'responsable': miembro.nombre
                    })
    graficar_aptitud(aptitud_mejor)
    return jsonify({'planificacion': resultado})

if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)

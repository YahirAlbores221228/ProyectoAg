from flask import Flask, request, jsonify, render_template
import random
import matplotlib.pyplot as plt

app = Flask(__name__)

class Miembro:
    def __init__(self, nombre, preferencias, disponibilidad, habilidades):
        self.nombre = nombre
        self.preferencias = preferencias
        self.disponibilidad = disponibilidad
        self.habilidades = habilidades
        
class TareaDomestica:
    def __init__(self, nombre):
        self.nombre = nombre

class Planificacion:
    def __init__(self, num_miembros, tareas, dias, franjas_horarias):
        self.asignacion = [] 
        for _ in range(num_miembros):
            miembro_asignacion = [] 
            for _ in range(dias): 
                dia_asignacion = [None] * franjas_horarias 
                miembro_asignacion.append(dia_asignacion) 
            self.asignacion.append(miembro_asignacion) 
        self.fitness = 0 

    def generar_aleatorio(self, miembros, tareas):
        tareas_pendientes = self.preparar_tareas(tareas) 
        while tareas_pendientes:
            tarea = tareas_pendientes.pop(0)
            miembros_preferidos = [miembro for miembro in miembros if tarea.nombre in miembro.preferencias] 
            if miembros_preferidos:
                posibles_asignaciones = self.encontrar_posibles_asignaciones(miembros_preferidos)
            else:
                posibles_asignaciones = self.encontrar_posibles_asignaciones(miembros)
            if posibles_asignaciones: 
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
                for franja in range(len(self.asignacion[0][0])): 
                    if miembro.disponibilidad[dia * 24 + franja]: 
                        posibles_asignaciones.append((miembro, dia, franja)) 
        return posibles_asignaciones

    def asignar_tarea(self, miembro, dia, franja, tarea, miembros):
        self.asignacion[miembros.index(miembro)][dia][franja] = tarea 
        

def inicializar_poblacion(tamano_poblacion, miembros, tareas, dias, franjas_horarias):
    poblacion = [] 
    for _ in range(tamano_poblacion): 
        planificacion = Planificacion(len(miembros), tareas, dias, franjas_horarias) 
        planificacion.generar_aleatorio(miembros, tareas) 
        poblacion.append(planificacion)
    return poblacion 

def calcular_fitness(planificacion, miembros, tareas):
    fitness = 0 
    for i, miembro in enumerate(miembros): 
        tareas_asignadas = [tarea for dia in planificacion.asignacion[i] for tarea in dia if tarea] 
        preferencias_cumplidas = sum(1 for tarea in tareas_asignadas if tarea.nombre in miembro.preferencias)
        fitness += preferencias_cumplidas * 2
        habilidad_total = sum(miembro.habilidades.get(tarea.nombre, 0.5) for tarea in tareas_asignadas) 
        fitness += habilidad_total
        for dia in range(len(planificacion.asignacion[i])): 
            for franja in range(len(planificacion.asignacion[i][dia])):
                tarea = planificacion.asignacion[i][dia][franja] 
                if tarea:
                    if miembro.disponibilidad[dia * 24 + franja]: 
                        fitness += 1 
                    else:
                        fitness -= 10
    num_tareas_por_miembro = [sum(1 for dia in asignacion for tarea in dia if tarea) for asignacion in planificacion.asignacion]
    desbalance = max(num_tareas_por_miembro) - min(num_tareas_por_miembro)
    fitness -= desbalance * 5  
    return fitness

def seleccion_torneo(poblacion, tamano_torneo=3):
    seleccionados = random.sample(poblacion, tamano_torneo) 
    return max(seleccionados, key=lambda x: x.fitness) 

def cruce(padre1, padre2):
    num_miembros = len(padre1.asignacion) 
    num_dias = len(padre1.asignacion[0]) 
    num_franjas = len(padre1.asignacion[0][0]) 
    hijo = Planificacion(num_miembros, [], num_dias, num_franjas) 
    punto_cruce = random.randint(0, num_miembros - 1) 
    for i in range(num_miembros):
        if i < punto_cruce: 
            hijo.asignacion[i] = [dia[:] for dia in padre1.asignacion[i]] 
        else:
            hijo.asignacion[i] = [dia[:] for dia in padre2.asignacion[i]] 
    return hijo

def mutacion(planificacion, tasa_mutacion, tareas, miembros):
    for i in range(len(planificacion.asignacion)):
        for j in range(len(planificacion.asignacion[i])): 
            for k in range(len(planificacion.asignacion[i][j])):
                if random.random() < tasa_mutacion: 
                    if miembros[i].disponibilidad[j * 24 + k]: 
                        planificacion.asignacion[i][j][k] = random.choice([None] + tareas) 

def poda(poblacion, tamano_maximo): 
    return sorted(poblacion, key=lambda x: x.fitness, reverse=True)[:tamano_maximo] 

def algoritmo_genetico(miembros, tareas, dias, franjas_horarias, tamano_poblacion, generaciones, tasa_mutacion):
    poblacion = inicializar_poblacion(tamano_poblacion, miembros, tareas, dias, franjas_horarias)
    aptitud_mejor = []
    for _ in range(generaciones):
        for planificacion in poblacion:
            planificacion.fitness = calcular_fitness(planificacion, miembros, tareas)
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

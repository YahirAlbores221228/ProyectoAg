let miembros = [];
let tareas = [];

function capturarDisponibilidad() {
    const dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'];
    const disponibilidad = Array(7 * 24).fill(false);

    dias.forEach((dia, diaIndex) => {
        const horas = document.getElementById(`disponibilidad-${dia}`).value.split(',');
        horas.forEach(horaRango => {
            const [inicio, fin] = horaRango.split('-').map(h => parseInt(h));
            for (let h = inicio; h < fin; h++) {
                disponibilidad[diaIndex * 24 + h] = true;
            }
        });
    });

    return disponibilidad;
}



function agregarMiembro() {
    const nombre = document.getElementById('nombre-miembro').value;
    const preferencias = document.getElementById('preferencias-miembro').value.split(',').map(pref => pref.trim());
    const habilidadesInput = document.getElementById('habilidades-miembro').value.split(',');
    const habilidades = {};

    habilidadesInput.forEach(hab => {
        const [tarea, tasa] = hab.split(':');
        habilidades[tarea.trim()] = parseFloat(tasa.trim());
    });
6
    const disponibilidad = capturarDisponibilidad();
    const miembro = { nombre, preferencias, disponibilidad, habilidades };
    miembros.push(miembro);

    alert(`Miembro ${nombre} agregado.`);
}

function agregarTarea() {
    const nombre = document.getElementById('nombre-tarea').value;

    const tarea = { nombre};
    tareas.push(tarea);

    alert(`Tarea ${nombre} agregada.`);
}

document.getElementById('input-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const response = await fetch('http://127.0.0.1:5000/api/generar_planificacion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            miembros, 
            tareas, 
            dias: 7, 
            franjas_horarias: 24, 
            tamano_poblacion: 100, 
            generaciones:200, 
            tasa_mutacion: 0.5 
        })
    });

    if (response.ok) {
        const resultado = await response.json();
        mostrarResultadosEnTabla(resultado.planificacion);
    } else {
        alert('Error en la generación de la planificación.');
    }
});

function mostrarResultadosEnTabla(planificacion) {
    const tbody = document.getElementById('resultados').getElementsByTagName('tbody')[0];
    tbody.innerHTML = ''; // Limpiar resultados anteriores
  
    for (let hora = 4; hora < 24; hora++) {
        const row = tbody.insertRow();
        const cellHora = row.insertCell();
        cellHora.textContent = `${hora}:00 - ${hora + 1}:00`;

        for (let dia = 0; dia < 7; dia++) {
            const cell = row.insertCell();
            const tareasDelDia = planificacion.filter(t => t.dia === dia && t.hora === hora);
            tareasDelDia.forEach(t => {
                const divTarea = document.createElement('div');
                divTarea.textContent = `${t.tarea} - ${t.responsable}`;
                cell.appendChild(divTarea);
            });
        }
    }
}

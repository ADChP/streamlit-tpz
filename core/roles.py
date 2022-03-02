import streamlit as st
from . import tools

def opciones(user_name):
    ops = ('Resumen', 'Asignar Postcampo', 'Finalizar Postcampo', 'Asignar GPKG', 'Finalizar GPKG', 'Consultas', 'Carga de información', 'Base de datos')

    rol_id = tools.role(user_name)
    rol_id = rol_id.loc[0,'usuario_rol']

    if rol_id == 1:
        opcion = st.selectbox('Escoja un opción', (ops[0], ops[1], ops[2]))
        if opcion == ops[0]:
            tools.resumen(rol_id, user_name)
        elif opcion == ops[1]:
            tools.asignar_cc(user_name)
        elif opcion == ops[2]:
            tools.finalizar_cc(user_name)
    elif rol_id == 2:
        opcion = st.selectbox('Escoja un opción', (ops[0], ops[3], ops[4]))
        if opcion == ops[0]:
            tools.resumen(rol_id, user_name)
        elif opcion == ops[3]:
            tools.asignar_gpkg(user_name)
        elif opcion == ops[4]:
            tools.finalizar_gpkg(user_name)
    elif rol_id == 3:
        opcion = st.selectbox('Escoja un opción', (ops[0], ops[3], ops[4], ops[5]))
        if opcion == ops[0]:
            tools.resumen(rol_id, user_name)
        elif opcion == ops[3]:
            tools.asignar_gpkg(user_name)
        elif opcion == ops[4]:
            tools.finalizar_gpkg(user_name)
        elif opcion == ops[5]:
            tools.consultas()
    elif rol_id == 4:
        opcion = st.selectbox('Escoja un opción', (ops[0], ops[1], ops[2], ops[3], ops[4], ops[5], ops[6], ops[7]))
        if opcion == ops[0]:
            tools.resumen(rol_id, user_name)
        elif opcion == ops[1]:
            tools.asignar_cc(user_name)
        elif opcion == ops[2]:
            tools.finalizar_cc(user_name)
        elif opcion == ops[3]:
            tools.asignar_gpkg(user_name)
        elif opcion == ops[4]:
            tools.finalizar_gpkg(user_name)
        elif opcion == ops[5]:
            tools.consultas()
        elif opcion == ops[6]:
            tools.cargar_info()
        elif opcion == ops[7]:
            tools.base_datos()
    elif rol_id == 5:
        tools.consultas()

import streamlit as st
import pandas as pd
from core import roles, tools

st.set_page_config(
     page_title="TPZ LADM-COL",
     page_icon="🌋",
     layout="wide",
     initial_sidebar_state="auto"
 )

user = st.sidebar.text_input('Usuario')
pwd = st.sidebar.text_input('Contraseña', type = 'password')

if st.sidebar.checkbox('Iniciar sesión'):
    if user == '' or pwd == '':
        st.error('Por favor, ingrese bien sus credenciales.')
    else:
        pwd_db = tools.password_db(user)

        if pwd_db.empty:
            st.error('No existe nadie con ese usuario.')
        else:
            pwd_db = pwd_db.loc[0,'contrasena']

            if pwd_db == pwd:
                st.success(f'¡Hola {user}!')
                roles.opciones(user)
            else:
                st.error('Contraseña incorrecta.')
else:
    '''
    # Telespazio - Área SIG
    ### Catastro multipropósito (LADM-COL).
    Para soporte del aplicativo, contacte a **andres.chavarria@tpzcr.com**
    '''

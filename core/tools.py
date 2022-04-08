import streamlit as st
import pandas as pd
import psycopg2
import sqlalchemy
from datetime import datetime

@st.cache
def password_db(user_name):
    pass_db = pd.read_sql(f"select contrasena from usuarios where usuario = '{user_name}'", st.secrets.con_uri)
    return pass_db

@st.cache
def role(user_name):
    rol = pd.read_sql(f"select usuario_rol from usuarios where usuario = '{user_name}'", st.secrets.con_uri)
    return rol

def u_state(user_name):
    user_state = pd.read_sql(f"select usuario_estado from usuarios where usuario = '{user_name}'", st.secrets.con_uri)
    return user_state

@st.cache
def u_id(user_name):
    user_id = pd.read_sql(f"select id from usuarios where usuario = '{user_name}'", st.secrets.con_uri)
    return user_id

def asigs(user_name):
    total_asig = pd.read_sql(f"select total_asig from usuarios where usuario = '{user_name}'", st.secrets.con_uri)
    return total_asig

def resumen(rol_id, user_name):
    if 'user_state' not in st.session_state:
        user_state = u_state(user_name)
        st.session_state.user_state = user_state.loc[0,'usuario_estado']

    if st.session_state.user_state == 1:
        st.info('Actualmente no tienes paquete asignado.')
    else:
        if rol_id == 1:
            con = psycopg2.connect(dbname=st.secrets.con_dbname, user=st.secrets.con_user, password=st.secrets.con_pass, host=st.secrets.con_host)
            cur = con.cursor()
            cur.execute(f"select cc.paquete paquete, m.municipio Municipio, cc.vereda vereda, cc.enlace Enlace, cc.observacion Observación, cc.nombre_paquete from control_calidad cc join usuarios u on cc.cc_usuario = u.id join d_municipio m on cc.cc_municipio = m.id where u.usuario = '{user_name}' and cc.cc_estado = 2")
            data = cur.fetchall()
            cols = []
            for elt in cur.description:
                cols.append(elt[0])
            query_1 = pd.DataFrame(data=data,columns=cols)
            con.close()
            #query_1 = pd.read_sql(f"select cc.paquete paquete, m.municipio Municipio, cc.vereda vereda, cc.enlace Enlace, cc.observacion Observación from control_calidad cc join usuarios u on cc.cc_usuario = u.id join d_municipio m on cc.cc_municipio = m.id where u.usuario = '{user_name}' and cc.cc_estado = 2", st.secrets.con_uri)
            st.info('Asignaciones de control de calidad en transcurso:')
            st.table(query_1)
        else:
            con = psycopg2.connect(dbname=st.secrets.con_dbname, user=st.secrets.con_user, password=st.secrets.con_pass, host=st.secrets.con_host)
            cur = con.cursor()
            cur.execute(f"select mlc.paquete paquete, m.municipio Municipio, mlc.vereda vereda, mlc.enlace_a Enlace, mlc.observacion Observación, cc.nombre_paquete from mlc join usuarios u on mlc.mlc_usuario = u.id join d_municipio m on mlc_municipio = m.id join control_calidad cc on mlc.cc_id = cc.id where u.usuario = '{user_name}' and mlc.mlc_estado = 2")
            data = cur.fetchall()
            cols = []
            for elt in cur.description:
                cols.append(elt[0])
            query_1 = pd.DataFrame(data=data,columns=cols)
            con.close()
            #query_1 = pd.read_sql(f"select mlc.paquete paquete, m.municipio Municipio, mlc.vereda vereda, mlc.enlace_a Enlace, mlc.observacion Observación from mlc join usuarios u on mlc.mlc_usuario = u.id join d_municipio m on mlc_municipio = m.id where u.usuario = '{user_name}' and mlc.mlc_estado = 2", st.secrets.con_uri)
            st.info('Asignaciones de modelo de levantamiento catastral en transcurso:')
            st.table(query_1)

def asignar_cc(user_name):
    if 'user_state' not in st.session_state:
        user_state = u_state(user_name)
        st.session_state.user_state = user_state.loc[0,'usuario_estado']

    if 'total_pack' not in st.session_state:
        total_pack = asigs(user_name)
        st.session_state.total_pack = total_pack.loc[0,'total_asig']

    user_id = u_id(user_name)
    user_id = user_id.loc[0,'id']

    if st.session_state.user_state  == 1 or (st.session_state.user_state == 2 and st.session_state.total_pack < 4):

        con = psycopg2.connect(dbname=st.secrets.con_dbname, user=st.secrets.con_user, password=st.secrets.con_pass, host=st.secrets.con_host)
        cur = con.cursor()
        cur.execute("select cc.id, cc.paquete, m.municipio, cc.vereda, cc.area, cc.cant_predios predios, cc.enlace, cc.observacion from control_calidad cc join d_municipio m on cc.cc_municipio = m.id where cc.cc_estado = 1 order by id")
        data = cur.fetchall()
        cols = []
        for elt in cur.description:
            cols.append(elt[0])
        query_2 = pd.DataFrame(data=data,columns=cols)
        #query_2 = pd.read_sql('select cc.id, cc.paquete, m.municipio, cc.vereda, cc.area, cc.cant_predios predios, cc.enlace, cc.observacion from control_calidad cc join d_municipio m on cc.cc_municipio = m.id where cc.cc_estado = 1', st.secrets.con_uri)

        if query_2.empty:
            st.info('No hay más datos para trabajar. En espera de nuevas entregas.')
        else:
            query_2_1 = query_2[['paquete', 'municipio', 'vereda', 'area', 'predios', 'observacion']].loc[:0]
            st.subheader('¿Desea asignarse el siguiente paquete?')
            st.table(query_2_1)
            btn_asign = st.button('Asignar')

            if btn_asign:
                con = psycopg2.connect(dbname=st.secrets.con_dbname, user=st.secrets.con_user, password=st.secrets.con_pass, host=st.secrets.con_host)
                cur = con.cursor()
                cur.execute("select cc.id, cc.enlace from control_calidad cc where cc.cc_estado = 1 order by id")
                data = cur.fetchall()
                cols = []
                for elt in cur.description:
                    cols.append(elt[0])
                query_2_b = pd.DataFrame(data=data,columns=cols)
                #query_2_b = pd.read_sql('select cc.id, cc.enlace from control_calidad cc where cc.cc_estado = 1', st.secrets.con_uri)

                query_2_2 = query_2_b[['id', 'enlace']].loc[:0]
                query_2_2_id = query_2_2.loc[0,'id']
                query_2_2_link = query_2_2.loc[0,'enlace']
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cur.execute(f"UPDATE control_calidad SET cc_estado = 2, cc_usuario = {user_id}, inicio = '{now}' WHERE id = {query_2_2_id}")
                cur.execute(f"UPDATE usuarios SET usuario_estado = 2, total_asig = total_asig+1 WHERE id = {user_id}")
                con.commit()

                total_pack = asigs(user_name)
                st.session_state.total_pack = total_pack.loc[0,'total_asig']
                user_state = u_state(user_name)
                st.session_state.user_state = user_state.loc[0,'usuario_estado']

                con.close()
                st.success(f'El paquete ha sido asignado. Por favor descargue la información [AQUÍ]({query_2_2_link})')
    else:
        st.error('Ya alcanzó el máximo de asignaciones. Finalice una de ellas antes de crear una nueva.')

def finalizar_cc(user_name):
    if 'user_state' not in st.session_state:
        user_state = u_state(user_name)
        st.session_state.user_state = user_state.loc[0,'usuario_estado']

    if 'total_pack' not in st.session_state:
        total_pack = asigs(user_name)
        st.session_state.total_pack = total_pack.loc[0,'total_asig']

    user_id = u_id(user_name)
    user_id = user_id.loc[0,'id']

    if st.session_state.user_state == 1:
        st.info('Actualmente no tienes paquetes asignados.')
    else:
        con = psycopg2.connect(dbname=st.secrets.con_dbname, user=st.secrets.con_user, password=st.secrets.con_pass, host=st.secrets.con_host)
        cur = con.cursor()
        cur.execute(f"select cc.id, cc.paquete, cc.cc_municipio, m.municipio, cc.vereda, cc.area area_ha, cc.cant_predios predios, u.usuario from control_calidad cc join usuarios u on cc.cc_usuario = u.id join d_municipio m on cc.cc_municipio = m.id where u.usuario = '{user_name}' and cc.cc_estado = 2")
        data = cur.fetchall()
        cols = []
        for elt in cur.description:
            cols.append(elt[0])
        query_3 = pd.DataFrame(data=data,columns=cols)
        #query_3 = pd.read_sql(f"select cc.id, cc.paquete, cc.cc_municipio, m.municipio, cc.vereda, cc.area area_ha, cc.cant_predios predios, u.usuario from control_calidad cc join usuarios u on cc.cc_usuario = u.id join d_municipio m on cc.cc_municipio = m.id where u.usuario = '{user_name}' and cc.cc_estado = 2", st.secrets.con_uri)

        col1, col2 = st.columns(2)

        with col1:
            quest_1 = st.radio('¿Coincide el área reportada con el área trabajada?', ('Sí', 'No'))

            if quest_1 == 'No':
                quest_1_area = st.number_input('Área (HA)', min_value = 1.0)

            quest_2 = st.radio('¿Coincide el número de predios reportados con el número de predios trabajados?', ('Sí', 'No'))

            if quest_2 == 'No':
                quest_2_predios = st.number_input('Cantidad de predios', min_value = 1)

            txt_1 = st.text_input('Nuevo enlace de descarga (*campo obligatorio)')
            txt_1 = txt_1.strip()
            txt_2 = st.text_area('Observaciones', max_chars = 300)
            txt_2 = txt_2.strip()

        with col2:
            if st.session_state.total_pack == 2:
                check_asigs = st.radio('Elija la asignación a finalizar.', ('Asignación # 1', 'Asignación # 2'))

                if check_asigs == 'Asignación # 1':
                    query_3_1 = query_3[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']].loc[:0]
                    query_3_2 = query_3[['id', 'cc_municipio']].loc[:0]

                    query_3_1_paq = query_3_1.loc[0,'paquete']
                    query_3_1_ver = query_3_1.loc[0,'vereda']
                    query_3_1_pre = query_3_1.loc[0,'predios']
                    query_3_1_area = query_3_1.loc[0,'area_ha']

                    query_3_2_id = query_3_2.loc[0,'id']
                    query_3_2_mun = query_3_2.loc[0,'cc_municipio']
                else:
                    query_3_1 = query_3[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']].loc[1:1]
                    query_3_2 = query_3[['id', 'cc_municipio']].loc[1:1]

                    query_3_1_paq = query_3_1.loc[1,'paquete']
                    query_3_1_ver = query_3_1.loc[1,'vereda']
                    query_3_1_pre = query_3_1.loc[1,'predios']
                    query_3_1_area = query_3_1.loc[1,'area_ha']

                    query_3_2_id = query_3_2.loc[1,'id']
                    query_3_2_mun = query_3_2.loc[1,'cc_municipio']

            elif st.session_state.total_pack == 3:
                check_asigs = st.radio('Elija la asignación a finalizar.', ('Asignación # 1', 'Asignación # 2', 'Asignación # 3'))

                if check_asigs == 'Asignación # 1':
                    query_3_1 = query_3[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']].loc[:0]
                    query_3_2 = query_3[['id', 'cc_municipio']].loc[:0]

                    query_3_1_paq = query_3_1.loc[0,'paquete']
                    query_3_1_ver = query_3_1.loc[0,'vereda']
                    query_3_1_pre = query_3_1.loc[0,'predios']
                    query_3_1_area = query_3_1.loc[0,'area_ha']

                    query_3_2_id = query_3_2.loc[0,'id']
                    query_3_2_mun = query_3_2.loc[0,'cc_municipio']

                elif check_asigs == 'Asignación # 2':
                    query_3_1 = query_3[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']].loc[1:1]
                    query_3_2 = query_3[['id', 'cc_municipio']].loc[1:1]

                    query_3_1_paq = query_3_1.loc[1,'paquete']
                    query_3_1_ver = query_3_1.loc[1,'vereda']
                    query_3_1_pre = query_3_1.loc[1,'predios']
                    query_3_1_area = query_3_1.loc[1,'area_ha']

                    query_3_2_id = query_3_2.loc[1,'id']
                    query_3_2_mun = query_3_2.loc[1,'cc_municipio']

                else:
                    query_3_1 = query_3[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']].loc[2:2]
                    query_3_2 = query_3[['id', 'cc_municipio']].loc[2:2]

                    query_3_1_paq = query_3_1.loc[2,'paquete']
                    query_3_1_ver = query_3_1.loc[2,'vereda']
                    query_3_1_pre = query_3_1.loc[2,'predios']
                    query_3_1_area = query_3_1.loc[2,'area_ha']

                    query_3_2_id = query_3_2.loc[2,'id']
                    query_3_2_mun = query_3_2.loc[2,'cc_municipio']

            elif st.session_state.total_pack == 4:
                check_asigs = st.radio('Elija la asignación a finalizar.', ('Asignación # 1', 'Asignación # 2', 'Asignación # 3', 'Asignación # 4'))

                if check_asigs == 'Asignación # 1':
                    query_3_1 = query_3[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']].loc[:0]
                    query_3_2 = query_3[['id', 'cc_municipio']].loc[:0]

                    query_3_1_paq = query_3_1.loc[0,'paquete']
                    query_3_1_ver = query_3_1.loc[0,'vereda']
                    query_3_1_pre = query_3_1.loc[0,'predios']
                    query_3_1_area = query_3_1.loc[0,'area_ha']

                    query_3_2_id = query_3_2.loc[0,'id']
                    query_3_2_mun = query_3_2.loc[0,'cc_municipio']

                elif check_asigs == 'Asignación # 2':
                    query_3_1 = query_3[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']].loc[1:1]
                    query_3_2 = query_3[['id', 'cc_municipio']].loc[1:1]

                    query_3_1_paq = query_3_1.loc[1,'paquete']
                    query_3_1_ver = query_3_1.loc[1,'vereda']
                    query_3_1_pre = query_3_1.loc[1,'predios']
                    query_3_1_area = query_3_1.loc[1,'area_ha']

                    query_3_2_id = query_3_2.loc[1,'id']
                    query_3_2_mun = query_3_2.loc[1,'cc_municipio']

                elif check_asigs == 'Asignación # 3':
                    query_3_1 = query_3[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']].loc[2:2]
                    query_3_2 = query_3[['id', 'cc_municipio']].loc[2:2]

                    query_3_1_paq = query_3_1.loc[2,'paquete']
                    query_3_1_ver = query_3_1.loc[2,'vereda']
                    query_3_1_pre = query_3_1.loc[2,'predios']
                    query_3_1_area = query_3_1.loc[2,'area_ha']

                    query_3_2_id = query_3_2.loc[2,'id']
                    query_3_2_mun = query_3_2.loc[2,'cc_municipio']

                else:
                    query_3_1 = query_3[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']].loc[3:3]
                    query_3_2 = query_3[['id', 'cc_municipio']].loc[3:3]

                    query_3_1_paq = query_3_1.loc[3,'paquete']
                    query_3_1_ver = query_3_1.loc[3,'vereda']
                    query_3_1_pre = query_3_1.loc[3,'predios']
                    query_3_1_area = query_3_1.loc[3,'area_ha']

                    query_3_2_id = query_3_2.loc[3,'id']
                    query_3_2_mun = query_3_2.loc[3,'cc_municipio']

            else:
                query_3_1 = query_3[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']]#.loc[:0]
                query_3_2 = query_3[['id', 'cc_municipio']]#.loc[:0]

                query_3_1_paq = query_3_1.loc[0,'paquete']
                query_3_1_ver = query_3_1.loc[0,'vereda']
                query_3_1_pre = query_3_1.loc[0,'predios']
                query_3_1_area = query_3_1.loc[0,'area_ha']

                query_3_2_id = query_3_2.loc[0,'id']
                query_3_2_mun = query_3_2.loc[0,'cc_municipio']


            st.subheader('Asignación pendiente')
            st.table(query_3_1)
            btn_fin = st.button('Finalizar asignación')

            if btn_fin:
                if txt_1 == '':
                    st.error('No ha ingresado el enlace de descarga.')
                else:
                    if quest_1 == 'Sí' and quest_2 == 'Sí':
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cur.execute(f"UPDATE control_calidad SET cc_estado = 3, final = '{now}' WHERE id = {query_3_2_id}")

                        if st.session_state.total_pack != 1:
                            cur.execute(f"UPDATE usuarios SET total_asig = total_asig-1 WHERE id = {user_id}")
                        else:
                            cur.execute(f"UPDATE usuarios SET usuario_estado = 1, total_asig = total_asig-1 WHERE id = {user_id}")

                        cur.execute(f"INSERT INTO mlc (paquete, mlc_municipio, vereda, cant_predios, area, mlc_estado, enlace_a, ingreso, cc_id) VALUES ({query_3_1_paq}, '{query_3_2_mun}', '{query_3_1_ver}', {query_3_1_pre}, {query_3_1_area}, 1, '{txt_1}', '{now}', {query_3_2_id})")
                        con.commit()

                        total_pack = asigs(user_name)
                        st.session_state.total_pack = total_pack.loc[0,'total_asig']
                        user_state = u_state(user_name)
                        st.session_state.user_state = user_state.loc[0,'usuario_estado']

                    elif quest_1 == 'No' and quest_2 == 'Sí':
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cur.execute(f"UPDATE control_calidad SET cc_estado = 3, final = '{now}' WHERE id = {query_3_2_id}")

                        if st.session_state.total_pack != 1:
                            cur.execute(f"UPDATE usuarios SET total_asig = total_asig-1 WHERE id = {user_id}")
                        else:
                            cur.execute(f"UPDATE usuarios SET usuario_estado = 1, total_asig = total_asig-1 WHERE id = {user_id}")

                        cur.execute(f"INSERT INTO mlc (paquete, mlc_municipio, vereda, cant_predios, area, mlc_estado, enlace_a, ingreso, cc_id) VALUES ({query_3_1_paq}, '{query_3_2_mun}', '{query_3_1_ver}', {query_3_1_pre}, {quest_1_area}, 1, '{txt_1}', '{now}', {query_3_2_id})")
                        con.commit()

                        total_pack = asigs(user_name)
                        st.session_state.total_pack = total_pack.loc[0,'total_asig']
                        user_state = u_state(user_name)
                        st.session_state.user_state = user_state.loc[0,'usuario_estado']

                    elif quest_1 == 'Sí' and quest_2 == 'No':
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cur.execute(f"UPDATE control_calidad SET cc_estado = 3, final = '{now}' WHERE id = {query_3_2_id}")

                        if st.session_state.total_pack != 1:
                            cur.execute(f"UPDATE usuarios SET total_asig = total_asig-1 WHERE id = {user_id}")
                        else:
                            cur.execute(f"UPDATE usuarios SET usuario_estado = 1, total_asig = total_asig-1 WHERE id = {user_id}")

                        cur.execute(f"INSERT INTO mlc (paquete, mlc_municipio, vereda, cant_predios, area, mlc_estado, enlace_a, ingreso, cc_id) VALUES ({query_3_1_paq}, '{query_3_2_mun}', '{query_3_1_ver}', {quest_2_predios}, {query_3_1_area}, 1, '{txt_1}', '{now}', {query_3_2_id})")
                        con.commit()

                        total_pack = asigs(user_name)
                        st.session_state.total_pack = total_pack.loc[0,'total_asig']
                        user_state = u_state(user_name)
                        st.session_state.user_state = user_state.loc[0,'usuario_estado']

                    else:
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cur.execute(f"UPDATE control_calidad SET cc_estado = 3, final = '{now}' WHERE id = {query_3_2_id}")

                        if st.session_state.total_pack != 1:
                            cur.execute(f"UPDATE usuarios SET total_asig = total_asig-1 WHERE id = {user_id}")
                        else:
                            cur.execute(f"UPDATE usuarios SET usuario_estado = 1, total_asig = total_asig-1 WHERE id = {user_id}")

                        cur.execute(f"INSERT INTO mlc (paquete, mlc_municipio, vereda, cant_predios, area, mlc_estado, enlace_a, ingreso, cc_id) VALUES ({query_3_1_paq}, '{query_3_2_mun}', '{query_3_1_ver}', {quest_2_predios}, {quest_1_area}, 1, '{txt_1}', '{now}', {query_3_2_id})")
                        con.commit()

                        total_pack = asigs(user_name)
                        st.session_state.total_pack = total_pack.loc[0,'total_asig']
                        user_state = u_state(user_name)
                        st.session_state.user_state = user_state.loc[0,'usuario_estado']

                    if txt_2 == '':
                        con.close()
                        st.success('Asignación finalizada.')
                    else:
                        cur = con.cursor()
                        cur.execute(f"UPDATE control_calidad SET observacion = '{txt_2}' WHERE id = {query_3_2_id}")
                        cur.execute(f"UPDATE mlc SET observacion = '{txt_2}' WHERE cc_id = {query_3_2_id}")
                        con.commit()
                        con.close()
                        st.success('Asignación finalizada.')

def asignar_gpkg(user_name):
    if 'user_state' not in st.session_state:
        user_state = u_state(user_name)
        st.session_state.user_state = user_state.loc[0,'usuario_estado']

    if 'total_pack' not in st.session_state:
        total_pack = asigs(user_name)
        st.session_state.total_pack = total_pack.loc[0,'total_asig']

    user_id = u_id(user_name)
    user_id = user_id.loc[0,'id']

    if st.session_state.user_state == 1 or (st.session_state.user_state == 2 and st.session_state.total_pack < 2):
        con = psycopg2.connect(dbname=st.secrets.con_dbname, user=st.secrets.con_user, password=st.secrets.con_pass, host=st.secrets.con_host)
        cur = con.cursor()
        cur.execute("select mlc.id, mlc.paquete, m.municipio, mlc.vereda, mlc.area area_ha, mlc.cant_predios predios, mlc.enlace_a, mlc.observacion from mlc join d_municipio m on mlc.mlc_municipio = m.id where mlc.mlc_estado = 1 order by id")
        data = cur.fetchall()
        cols = []
        for elt in cur.description:
            cols.append(elt[0])
        query_4 = pd.DataFrame(data=data,columns=cols)
        #query_4 = pd.read_sql('select mlc.id, mlc.paquete paquete, m.municipio Municipio, mlc.vereda vereda, mlc.area Área, mlc.cant_predios predios, mlc.enlace_a, mlc.observacion Observación from mlc join d_municipio m on mlc.mlc_municipio = m.id where mlc.mlc_estado = 1', st.secrets.con_uri)

        if query_4.empty:
            st.info('No hay más datos para trabajar. En espera de nuevas entregas.')
        else:
            query_4_1 = query_4[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'observacion']].loc[:0]
            st.subheader('¿Desea asignarse el siguiente paquete?')
            st.table(query_4_1)
            btn_asign = st.button('Asignar')

            if btn_asign:
                cur.execute("select mlc.id, mlc.enlace_a from mlc where mlc.mlc_estado = 1 order by id")
                data = cur.fetchall()
                cols = []
                for elt in cur.description:
                    cols.append(elt[0])
                query_4_b = pd.DataFrame(data=data,columns=cols)
                #query_4 = pd.read_sql('select mlc.id, mlc.paquete paquete, m.municipio Municipio, mlc.vereda vereda, mlc.area Área, mlc.cant_predios predios, mlc.enlace_a, mlc.observacion Observación from mlc join d_municipio m on mlc.mlc_municipio = m.id where mlc.mlc_estado = 1', con)

                query_4_2 = query_4_b[['id', 'enlace_a']].loc[:0]
                query_4_2_id = query_4_2.loc[0,'id']
                query_4_2_link = query_4_2.loc[0,'enlace_a']
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur = con.cursor()
                cur.execute(f"UPDATE mlc SET mlc_estado = 2, mlc_usuario = {user_id}, inicio = '{now}' WHERE id = {query_4_2_id}")
                cur.execute(f"UPDATE usuarios SET usuario_estado = 2, total_asig = total_asig+1 WHERE id = {user_id}")
                con.commit()

                total_pack = asigs(user_name)
                st.session_state.total_pack = total_pack.loc[0,'total_asig']
                user_state = u_state(user_name)
                st.session_state.user_state = user_state.loc[0,'usuario_estado']
                con.close()
                st.success(f'El paquete ha sido asignado. Por favor descargue la información [AQUÍ]({query_4_2_link})')
    else:
        st.error('Ya alcanzó el máximo de asignaciones. Finalice una de ellas antes de crear una nueva.')

def finalizar_gpkg(user_name):
    if 'user_state' not in st.session_state:
        user_state = u_state(user_name)
        st.session_state.user_state = user_state.loc[0,'usuario_estado']

    if 'total_pack' not in st.session_state:
        total_pack = asigs(user_name)
        st.session_state.total_pack = total_pack.loc[0,'total_asig']

    user_id = u_id(user_name)
    user_id = user_id.loc[0,'id']

    if st.session_state.user_state == 1:
        st.info('Actualmente no tienes paquetes asignados.')
    else:
        con = psycopg2.connect(dbname=st.secrets.con_dbname, user=st.secrets.con_user, password=st.secrets.con_pass, host=st.secrets.con_host)
        cur = con.cursor()
        cur.execute(f"select mlc.id, mlc.paquete, mlc.mlc_municipio, m.municipio, mlc.vereda, mlc.area area_ha, mlc.cant_predios predios, u.usuario from mlc join usuarios u on mlc.mlc_usuario = u.id join d_municipio m on mlc.mlc_municipio = m.id where u.usuario = '{user_name}' and mlc.mlc_estado = 2")
        data = cur.fetchall()
        cols = []
        for elt in cur.description:
            cols.append(elt[0])
        query_5 = pd.DataFrame(data=data,columns=cols)
        #query_5 = pd.read_sql(f'select mlc.id, mlc.paquete paquete, mlc.mlc_municipio, m.municipio Municipio, mlc.vereda vereda, mlc.area area_ha, mlc.cant_predios predios, u.usuario Usuario from mlc join usuarios u on mlc.mlc_usuario = u.id join d_municipio m on mlc.mlc_municipio = m.id where u.usuario = "{user_name}" and mlc.mlc_estado = 2', st.secrets.con_uri)

        col1, col2 = st.columns(2)

        with col1:
            quest_3 = st.radio('¿Coincide el área reportada con el área trabajada?', ('Sí', 'No'))

            if quest_3 == 'No':
                quest_3_area = st.number_input('Área (HA)', min_value = 1.0)

            quest_4 = st.radio('¿Coincide el número de predios reportados con el número de predios trabajados?', ('Sí', 'No'))

            if quest_4 == 'No':
                quest_4_predios = st.number_input('Cantidad de predios', min_value = 1)

            txt_3 = st.text_input('Nuevo enlace de descarga (*campo obligatorio)')
            txt_3 = txt_3.strip()
            txt_4 = st.text_area('Observaciones', max_chars = 300)
            txt_4 = txt_4.strip()

        with col2:
            if st.session_state.total_pack == 2:
                check_asigs = st.radio('Elija la asignación a finalizar.', ('Asignación # 1', 'Asignación # 2'))

                if check_asigs == 'Asignación # 1':
                    query_5_1 = query_5[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']].loc[:0]
                    query_5_2 = query_5[['id', 'mlc_municipio']].loc[:0]

                    query_5_1_paq = query_5_1.loc[0,'paquete']
                    query_5_1_ver = query_5_1.loc[0,'vereda']
                    query_5_1_pre = query_5_1.loc[0,'predios']
                    query_5_1_area = query_5_1.loc[0,'area_ha']

                    query_5_2_id = query_5_2.loc[0,'id']
                    query_5_2_mun = query_5_2.loc[0,'mlc_municipio']
                else:
                    query_5_1 = query_5[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']].loc[1:1]
                    query_5_2 = query_5[['id', 'mlc_municipio']].loc[1:1]

                    query_5_1_paq = query_5_1.loc[1,'paquete']
                    query_5_1_ver = query_5_1.loc[1,'vereda']
                    query_5_1_pre = query_5_1.loc[1,'predios']
                    query_5_1_area = query_5_1.loc[1,'area_ha']

                    query_5_2_id = query_5_2.loc[1,'id']
                    query_5_2_mun = query_5_2.loc[1,'mlc_municipio']

            else:
                query_5_1 = query_5[['paquete', 'municipio', 'vereda', 'area_ha', 'predios', 'usuario']]#.loc[:0]
                query_5_2 = query_5[['id', 'mlc_municipio']]#.loc[:0]

                query_5_1_paq = query_5_1.loc[0,'paquete']
                query_5_1_ver = query_5_1.loc[0,'vereda']
                query_5_1_pre = query_5_1.loc[0,'predios']
                query_5_1_area = query_5_1.loc[0,'area_ha']

                query_5_2_id = query_5_2.loc[0,'id']
                query_5_2_mun = query_5_2.loc[0,'mlc_municipio']

            st.subheader('Asignación pendiente')
            st.table(query_5_1)
            btn_fin = st.button('Finalizar asignación')

            if btn_fin:
                if txt_3 == '':
                    st.error('No ha ingresado el enlace de descarga.')
                else:
                    if quest_3 == 'Sí' and quest_4 == 'Sí':
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cur.execute(f"UPDATE mlc SET mlc_estado = 3, final = '{now}', enlace_b = '{txt_3}' WHERE id = {query_5_2_id}")

                        if st.session_state.total_pack == 2:
                            cur.execute(f"UPDATE usuarios SET total_asig = total_asig-1 WHERE id = {user_id}")
                        else:
                            cur.execute(f"UPDATE usuarios SET usuario_estado = 1, total_asig = total_asig-1 WHERE id = {user_id}")

                        con.commit()

                        total_pack = asigs(user_name)
                        st.session_state.total_pack = total_pack.loc[0,'total_asig']
                        user_state = u_state(user_name)
                        st.session_state.user_state = user_state.loc[0,'usuario_estado']

                    elif quest_3 == 'No' and quest_4 == 'Sí':
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cur = con.cursor()
                        cur.execute(f"UPDATE mlc SET mlc_estado = 3, area = {quest_3_area}, final = '{now}', enlace_b = '{txt_3}' WHERE id = {query_5_2_id}")

                        if st.session_state.total_pack == 2:
                            cur.execute(f"UPDATE usuarios SET total_asig = total_asig-1 WHERE id = {user_id}")
                        else:
                            cur.execute(f"UPDATE usuarios SET usuario_estado = 1, total_asig = total_asig-1 WHERE id = {user_id}")

                        con.commit()

                        total_pack = asigs(user_name)
                        st.session_state.total_pack = total_pack.loc[0,'total_asig']
                        user_state = u_state(user_name)
                        st.session_state.user_state = user_state.loc[0,'usuario_estado']

                    elif quest_3 == 'Sí' and quest_4 == 'No':
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cur = con.cursor()
                        cur.execute(f"UPDATE mlc SET mlc_estado = 3, cant_predios = {quest_4_predios}, final = '{now}', enlace_b = '{txt_3}' WHERE id = {query_5_2_id}")

                        if st.session_state.total_pack == 2:
                            cur.execute(f"UPDATE usuarios SET total_asig = total_asig-1 WHERE id = {user_id}")
                        else:
                            cur.execute(f"UPDATE usuarios SET usuario_estado = 1, total_asig = total_asig-1 WHERE id = {user_id}")

                        con.commit()

                        total_pack = asigs(user_name)
                        st.session_state.total_pack = total_pack.loc[0,'total_asig']
                        user_state = u_state(user_name)
                        st.session_state.user_state = user_state.loc[0,'usuario_estado']

                    else:
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cur = con.cursor()
                        cur.execute(f"UPDATE mlc SET mlc_estado = 3, area = {quest_3_area}, cant_predios = {quest_4_predios}, final = '{now}', enlace_b = '{txt_3}' WHERE id = {query_5_2_id}")

                        if st.session_state.total_pack == 2:
                            cur.execute(f"UPDATE usuarios SET total_asig = total_asig-1 WHERE id = {user_id}")
                        else:
                            cur.execute(f"UPDATE usuarios SET usuario_estado = 1, total_asig = total_asig-1 WHERE id = {user_id}")

                        con.commit()

                        total_pack = asigs(user_name)
                        st.session_state.total_pack = total_pack.loc[0,'total_asig']
                        user_state = u_state(user_name)
                        st.session_state.user_state = user_state.loc[0,'usuario_estado']

                    if txt_4 == '':
                        st.success('Asignación finalizada.')
                    else:
                        cur = con.cursor()
                        cur.execute(f"UPDATE mlc SET observacion = '{txt_4}' WHERE id = {query_5_2_id}")
                        con.commit()
                        con.close()
                        st.success('Asignación finalizada.')

def consultas():
    col1, col2 = st.columns(2)

    with col1:
        radio = st.radio('', ('Validación', 'Procesamiento con modelos'))
    with col2:
        muni = st.selectbox('Municipio', ('Todos', 'Beteitiva', 'Busbanza', 'Corrales','Paz de Rio', 'Sativasur', 'Socha', 'Socota', 'Tasco'))

    if radio == 'Validación':
        if muni == 'Todos':
            query_6_1 = pd.read_sql('select paquete, municipio, vereda, cant_predios, area, estado, usuario, ingreso, inicio, final, enlace, observacion, nombre_paquete from control_calidad cc join d_municipio m on cc.cc_municipio = m.id join d_estadoentrega ee on cc.cc_estado = ee.id left join usuarios u on cc.cc_usuario = u.id order by municipio, estado, paquete', st.secrets.con_uri)
        else:
            query_6_1 = pd.read_sql(f"select paquete, municipio, vereda, cant_predios, area, estado, usuario, ingreso, inicio, final, enlace, observacion, nombre_paquete from control_calidad cc join d_municipio m on cc.cc_municipio = m.id join d_estadoentrega ee on cc.cc_estado = ee.id left join usuarios u on cc.cc_usuario = u.id where municipio = '{muni}' order by municipio, estado, paquete", st.secrets.con_uri)
        st.write(query_6_1)
        csv = query_6_1.to_csv(index = False).encode('utf-8')
        st.download_button(label="CSV", data=csv, file_name='consulta_cc.csv', mime='text/csv')
    else:
        if muni == 'Todos':
            query_6_2 = pd.read_sql('select paquete, municipio, vereda, cant_predios, area, estado, usuario, ingreso, inicio, final, enlace_a, enlace_b, observacion, cc.nombre_paquete from mlc join d_municipio m on mlc.mlc_municipio = m.id join d_estadoentrega ee on mlc.mlc_estado = ee.id left join usuarios u on mlc.mlc_usuario = u.id join control_calidad cc on mlc.cc_id = cc.id order by municipio, estado, paquete', st.secrets.con_uri)
        else:
            query_6_2 = pd.read_sql(f"select paquete, municipio, vereda, cant_predios, area, estado, usuario, ingreso, inicio, final, enlace_a, enlace_b, observacion, cc.nombre_paquete from mlc join d_municipio m on mlc.mlc_municipio = m.id join d_estadoentrega ee on mlc.mlc_estado = ee.id left join usuarios u on mlc.mlc_usuario = u.id join control_calidad cc on mlc.cc_id = cc.id where municipio = '{muni}' order by municipio, estado, paquete", st.secrets.con_uri)
        st.write(query_6_2)
        csv = query_6_2.to_csv(index = False).encode('utf-8')
        st.download_button(label="CSV", data=csv, file_name='consulta_mlc.csv', mime='text/csv')

def cargar_info():
    file_1 = st.file_uploader('Archivo de control', type = 'csv')
    if file_1 is not None:
        df = pd.read_csv(file_1, decimal=',')
        st.write(df)

    btn_upload = st.button('Cargar información')
    if btn_upload:
        if file_1 is not None:
            engine = sqlalchemy.create_engine(st.secrets.con_uri)
            con_b = engine.connect()
            df.to_sql('control_calidad', con_b, if_exists='append', index=False)
            con_b.close()
            st.success('Información cargada correctamente.')
        else:
            st.error('No tiene cargado el archivo .csv')

def base_datos():
    query_7 = 'No hay consultas.'
    col1, col2 = st.columns(2)

    with col1:
        tipo_sql = st.radio('Tipo de acción', ('Consulta', 'Modificación'))

        if tipo_sql == 'Consulta':
            txt_5 = st.text_area('Consulta')

            if st.button('Ejecutar'):
                try:
                    query_7 = pd.read_sql(f'{txt_5}', st.secrets.con_uri)
                    st.download_button('CSV', data = query_7.to_csv().encode('utf-8'), file_name = 'consulta.csv', mime = 'text/csv')
                except:
                    st.error('Consulta mal ejecutada.')

        else:
            txt_5 = st.text_area('Consulta')

            if st.button('Ejecutar'):
                try:
                    con = psycopg2.connect(dbname=st.secrets.con_dbname, user=st.secrets.con_user, password=st.secrets.con_pass, host=st.secrets.con_host)
                    cur = con.cursor()
                    cur.execute(f"{txt_5}")
                    con.commit()
                    con.close()
                    st.success('Tarea ejecutada.')
                except:
                    st.error('Tarea mal ejecutada.')

    with col2:
        st.write(query_7)

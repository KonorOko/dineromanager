from datetime import datetime
import pytz
import streamlit as st
import pandas as pd
from sqlalchemy.sql import text
from components.header import Header
from components.footer import Footer

# CRUD
def connect_database():
  # connect to database
  try:
    ssl_args = {'ssl': {'ca': 'cacert.pem'}}
    conn = st.connection("mydb", type="sql", autocommit=False,
                      dialect = st.secrets.connections.mydb.dialect,
                      username= st.secrets.connections.mydb.username,
                      password = st.secrets.connections.mydb.password,
                      host = st.secrets.connections.mydb.host,
                      database = st.secrets.connections.mydb.database,
                      connect_args=ssl_args)
    return conn
  except Exception as e:
    print(e)
    return None

def get_data(conn, query: str, params: dict = None):
    # get data from database
    try:
        data = conn.query(query, params=params)
        return data
    except Exception as e:
        print(e)
        st.error("Failed to get data", e)
        return None
    
def insert_data(conn, query, data):
    # insert data into database
    connect_insert = conn
    with connect_insert.session as session:
        try:
            session.execute(query, data)
            session.commit()
            return 0
        except Exception as e:
            session.rollback()
            print("Insert data failed:", e)
            st.error("Failed to insert data")
            raise

def delete_data(conn, query, params: dict = None):
    # delete data from database
    with conn.session as session:
        try:
            session.execute(query, params)
            session.commit()
            return 0
        except Exception as e:
            session.rollback()
            print("Delete data failed: ", e)
            st.error("Failed to delete data")
            raise


class Manager:
    def __init__(self) -> None:
        self.conn = connect_database()
    
    def builder(self):
      st.text("Programa para administrar los ingresos de dinero")
      cantidad = st.text_input("Ingresos", placeholder="Monto total del dinero")
      motivo = st.text_input("Motivo", placeholder="Ingrese el motivo del monto")

      col1,col2,col3 = st.columns([0.3, 0.3, 0.3])
      with col2:
        button_data = st.button("Agregar monto", use_container_width=True, type="primary")
      if button_data:
        try:
          zona_horaria_mexico = pytz.timezone('America/Mexico_City')
          date_mexico = datetime.now(zona_horaria_mexico).strftime("%Y/%m/%d")
          insert_data(self.conn, 
                      text("INSERT INTO Dinero (Cantidad, Motivo, Fecha) VALUES (:Cantidad, :Motivo, :Fecha)"),
                      data={"Cantidad": float(cantidad), "Motivo": motivo, "Fecha": date_mexico})
          st.cache_data.clear()
          st.rerun()
          st.toast("Información agregada con éxito")
        except Exception as e:
           print(e)
           st.toast("No se pudo agregar la información a la base de datos")
      

      st.dataframe(get_data(self.conn, "SELECT * FROM Dinero"),
                   hide_index=True, use_container_width=True)
      
      st.divider()
      st.text("Elimina un registro")
      id_reg = st.text_input("ID del monto a eliminar", placeholder="Ingrese número de regístro")
      delete_button = st.button("Eliminar", type="primary")
      if delete_button:
        try:
          delete_data(self.conn, text("DELETE FROM Dinero WHERE ID_Dinero = :ID_Dinero"),
                      params={"ID_Dinero": id_reg})
          st.cache_data.clear()
          st.rerun()
          st.toast("Se elimino el regístro correctamente")
        except:
           st.toast("No se pudo eliminar el regístro")

def main():
    # settings
    st.set_page_config(page_title="Add to DB", 
                       layout='wide', 
                       initial_sidebar_state="collapsed")
    st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
    hide_footer_style = """
    <style>
    .reportview-container .main footer {visibility: hidden;}    
    """
    st.markdown(hide_footer_style, unsafe_allow_html=True)

    # instances
    header: Header = Header("Administrador de dinero")
    footer: Footer = Footer()
    manager: Manager = Manager()


    header.builder()
    manager.builder()
    footer.builder()

if __name__ == "__main__":
    main()
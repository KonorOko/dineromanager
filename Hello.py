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

def get_date():
   zona_horaria_mexico = pytz.timezone('America/Mexico_City')
   date_mexico = datetime.now(zona_horaria_mexico).strftime("%Y-%m-%d")
   return date_mexico


class Manager:
    def __init__(self) -> None:
        self.conn = connect_database()
    
    def builder(self):
      st.text("Programa para administrar los ingresos de dinero")
      cantidad = st.text_input("Ingresos", placeholder="Monto total del dinero")
      motivo = st.text_input("Motivo", placeholder="Ingrese el motivo del monto")
      with st.expander("Avanzado"):
         fecha = st.date_input("Fecha", value=None, format="DD/MM/YYYY")
      col1,col2,spacer,col3,col4 = st.columns([0.23, 0.25, 0.04, 0.25, 0.23])
      with col2:
        button_data = st.button("Agregar", type="primary", use_container_width=True)
      with col3:
         actualizar = st.button("Actualizar", type="primary", use_container_width=True)
      if actualizar:
         st.cache_data.clear()
         st.rerun()
      if button_data:
        try:
          if fecha is not None:
            date_mexico = fecha
          else:
            date_mexico = get_date()
          insert_data(self.conn, 
                      text("INSERT INTO Dinero (Cantidad, Motivo, Fecha) VALUES (:Cantidad, :Motivo, :Fecha)"),
                      data={"Cantidad": float(cantidad), "Motivo": motivo, "Fecha": date_mexico})
          st.cache_data.clear()
          st.rerun()
          st.toast("Información agregada con éxito")
        except Exception as e:
           print(e)
           st.toast("No se pudo agregar la información a la base de datos")
      
      data = get_data(self.conn, "SELECT * FROM Dinero")
      data["Fecha"] = pd.to_datetime(data["Fecha"], format='%d-%m-%Y').dt.date

      st.divider()

      filters = st.multiselect("Filtro", data["Fecha"].unique())
      if filters:
         st.dataframe(data[data["Fecha"].isin(filters)], hide_index=True, use_container_width=True)
      else:
         st.dataframe(data, hide_index=True, use_container_width=True)

      st.divider()

      st.subheader("Data Info", help="Flecha: Indica el cambio diario")
      fecha_hoy = pd.to_datetime(get_date()).date()
      spacer1, col1, spacer2, col2, spacer3, col3, spacer4 = st.columns([0.03, 0.3, 0.03, 0.3, 0.03, 0.3, 0.03])
      data_today = data[data["Fecha"] == fecha_hoy]
      with col1:
        total = data["Cantidad"].sum()
        balance_today = data_today["Cantidad"].sum()
        st.metric("Balance Total", total, balance_today)
      with col2:
         count_reg = data.shape[0]
         count_reg_today = data_today.shape[0]
         st.metric("Número de montos", count_reg, count_reg_today)
      with col3:
         prom_today = data_today["Cantidad"].mean()
         st.metric("Promedio de ingresos", F"{prom_today: .1f}")

      st.divider()

      st.subheader("Elimina un registro")
      id_reg = st.text_input("ID del monto a eliminar", placeholder="Ingrese número de regístro")
      delete_button = st.button("Eliminar", type="primary")
      if delete_button:
        try:
          delete_data(self.conn, text("DELETE FROM Dinero WHERE ID_Dinero = :ID_Dinero"),
                      params={"ID_Dinero": id_reg})
          st.cache_data.clear()
          st.toast("Se elimino el regístro correctamente")
        except:
           st.cache_data.clear()
           st.rerun()

      st.divider()

      st.subheader("Ingresos vs Tiempo")
      data_group = data.groupby(["Fecha"]).sum().reset_index()
      st.line_chart(data_group, x="Fecha", y="Cantidad")

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
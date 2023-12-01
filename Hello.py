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
      col1t, col2t = st.columns([0.8, 0.2])
      with col1t:
        st.text("Programa para administrar los ingresos de dinero.")
      with col2t:
         st.caption(str(get_date()))
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

      with st.expander("Filtros"):
        st.markdown("**Fechas**")
        col1, col2 = st.columns(2)
        with col1:
           min_date = st.date_input("Mínimo", value=None)
        with col2:
           max_date = st.date_input("Máximo", value=None)

      if min_date and not max_date:
         st.dataframe(data[data["Fecha"] > min_date], hide_index=True, use_container_width=True)
      elif max_date and not min_date:
         st.dataframe(data[data["Fecha"] < max_date], hide_index=True, use_container_width=True)
      else:
         st.dataframe(data, hide_index=True, use_container_width=True)

      st.divider()

      st.subheader("Data Info")
      fecha_hoy = pd.to_datetime(get_date()).date()
      data_today = data[data["Fecha"] == fecha_hoy]
      st.markdown("#### Mensual", help="Flecha: Indica el cambio diario")
      spacer1, col1, spacer2, col2, spacer3, col3, spacer4 = st.columns([0.03, 0.3, 0.03, 0.3, 0.03, 0.3, 0.03])

      with col1:
        data_mensual = data[pd.to_datetime(data["Fecha"]).dt.month == fecha_hoy.month]
        balance_mesual = data_mensual["Cantidad"].sum()
        balance_today = data_today["Cantidad"].sum()
        st.metric("Balance", f"${balance_mesual: ,.2f}", f"${balance_today: ,.2f}")

      with col2:
         count_reg = data.shape[0]
         count_mensual = data_mensual.shape[0]
         count_reg_today = data_today.shape[0]
         st.metric("Numero de montos", count_mensual, count_reg_today)

      with col3:
         prom_mensual = data_mensual["Cantidad"].mean()
         prom_data = data["Cantidad"].mean()
         st.metric("Promedio de ingresos", f"${prom_mensual: ,.2f}")

      st.markdown("#### Anual", help="Flecha: Indica el cambio mensual")
      spacer1_2, col1_2, spacer2_2, col2_2, spacer_2, col3_2, spacer4_2 = st.columns([0.03, 0.3, 0.03, 0.3, 0.03, 0.3, 0.03])
      with col1_2:
        
        total = data["Cantidad"].sum()
        st.metric("Balance Total", f"${total: ,.2f}", f"${balance_mesual: ,.2f}")

      with col2_2:
         st.metric("Número de montos", count_reg, count_mensual)

      with col3_2:
         st.metric("Promedio de ingresos", f"${prom_data: ,.2f}")

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

      st.divider()

      st.subheader("No. de montos vs tiempo")
      data_group['Numero de montos'] = data.groupby('Fecha')['Cantidad'].count().reset_index()['Cantidad']
      st.line_chart(data_group, x="Fecha", y="Numero de montos")

def main():
    # settings
    st.set_page_config(page_title="Add to DB", 
                       layout='wide', 
                       initial_sidebar_state="collapsed")
    st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
    style = """
    <style>
    div[data-testid="stMetricValue"] > div {
    box-shadow: 0 0 1.5px #cccccc;
    padding: 10px;
    border-radius: 10px;
    }
    .reportview-container .main footer {visibility: hidden;}    
    """
    st.markdown(style, unsafe_allow_html=True)

    # instances
    header: Header = Header("Manager")
    footer: Footer = Footer()
    manager: Manager = Manager()

    header.builder()
    manager.builder()
    footer.builder()

if __name__ == "__main__":
    main()
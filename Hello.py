import streamlit as st
import pandas as pd
#from sqlalchemy.sql import text
from components.header import Header
from components.footer import Footer

"""
database: project
username: 1m2kyjelmm79d5aurtsf
host: aws.connect.psdb.cloud
password: pscale_pw_PJRNr4brLtlrQPHrwk7qA7nBQdntx92scxw3ufSpsu8
"""
class Manager:
    def __init__(self) -> None:
        def conection_database():
          try:
            ssl_args = {'ssl': {'ca': 'cacert.pem'}}
            self.conn = st.connection("mydb", type="sql", autocommit=False,
                              dialect = st.secrets.connections.mydb.dialect,
                              username= st.secrets.connections.mydb.username,
                              password = st.secrets.connections.mydb.password,
                              host = st.secrets.connections.mydb.host,
                              database = st.secrets.connections.mydb.database,
                              connect_args=ssl_args)
            return
          except:
            pass
    
    def builder(self):
      st.text("Programa para administrar los ingresos de dinero")
      st.text_input("Ingresos", placeholder="Monto total del dinero")
      st.text_input("Nombre", placeholder="Nombre de la persona que dio el dinero")

      st.dataframe()


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
import streamlit as st

class Header:
    def __init__(self, title: str):
        self.title = title
        
    def builder(self):
        col1, col2, col3 = st.columns([0.11, 0.58, 0.11])
        with col1:
            st.text("Ganthaus - Dashboard")
            
        with col2:
            st.divider()
            
        with col3:
            st.text(self.title)
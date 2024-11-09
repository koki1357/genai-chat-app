import streamlit as st

def custom_notification(type, message):
    colors = {
        'success': '#1e4620',  # 濃い緑色
        'warning': '#4d3800',  # 濃いオレンジ色
    }
    text_colors = {
        'success': '#a5d6a7',  # 薄い緑色
        'warning': '#ffe082',  # 薄いオレンジ色
    }
    border_colors = {
        'success': '#4caf50',  # 明るい緑色
        'warning': '#ffa000',  # 明るいオレンジ色
    }
    
    html = f"""
    <div style="
        padding: 10px;
        border-radius: 5px;
        background-color: {colors[type]};
        border-left: 5px solid {border_colors[type]};
        margin-bottom: 10px;
        color: {text_colors[type]};
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 1rem;
        ">
        {message}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

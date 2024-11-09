import streamlit as st
import streamlit.components.v1 as components
import json


def chat_message_with_copy(content):
    # HTMLテンプレート
    html_content = f"""
    <div id="copyContainer">
        <textarea id="hiddenTextArea" style="opacity: 0; position: absolute; z-index: -1;">{content}</textarea>
        <button onclick="handleCopy()">📋</button>
        <div id="notification" class="notification">
            <span id="notificationIcon"></span>
            <span id="notificationText"></span>
        </div>
    </div>
    <script>
    function handleCopy() {{
        const copyTextArea = document.getElementById("hiddenTextArea");
        const notification = document.getElementById("notification");
        const notificationIcon = document.getElementById("notificationIcon");
        const notificationText = document.getElementById("notificationText");
        
        copyTextArea.focus();
        copyTextArea.select();
        
        try {{
            const copiedSuccessful = document.execCommand('copy');
            let message, icon;
            
            if (copiedSuccessful) {{
                message = "Copied!";
                icon = "✅";
                notification.className = "notification show success";
            }} else {{
                message = "Failed to copy";
                icon = "❌";
                notification.className = "notification show error";
            }}
            
            notificationIcon.textContent = icon;
            notificationText.textContent = message;
            
            setTimeout(() => {{
                notification.className = "notification";
            }}, 3000);
            
        }} catch (err) {{
            console.error('Oops, unable to copy', err);
            notificationIcon.textContent = "❌";
            notificationText.textContent = "Failed to copy";
            notification.className = "notification show error";
            
            setTimeout(() => {{
                notification.className = "notification";
            }}, 3000);
        }}
    }}
    </script>
    <style>
    #copyContainer {{
        display: flex;
        align-items: center;
        font-family: Arial, sans-serif;
    }}
    #copyContainer button {{
        margin-left: 10px;
        cursor: pointer;
        background: none;
        border: none;
        font-size: 1.2em;
    }}
    .notification {{
        display: flex;
        align-items: center;
        margin-left: 10px;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 14px;
        opacity: 0;
        transition: opacity 0.3s ease-in-out;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }}
    .notification.show {{
        opacity: 1;
    }}
    .notification.success {{
        background-color: #4CAF50;
        color: white;
    }}
    .notification.error {{
        background-color: #f44336;
        color: white;
    }}
    #notificationIcon {{
        margin-right: 8px;
    }}
    </style>
    """

    # 表示
    components.html(html_content, height=50)

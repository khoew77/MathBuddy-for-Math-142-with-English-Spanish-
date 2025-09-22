# -*- coding: utf-8 -*-
import pymysql
import streamlit as st
from openai import OpenAI
import os
import json
from datetime import datetime
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import matplotlib.pyplot as plt
import numpy as np
import re

# --- 1. TRANSLATIONS DICTIONARY ---
translations = {
    "en": {
        "page_title": "MathBuddy",
        "welcome_title": "📚 Welcome to MathBuddy",
        "welcome_image_caption": "Your Study Companion for Math Success 📱",
        "welcome_prompt": "Please enter your student ID and name to get started.",
        "student_id_label": "🆔 Student ID",
        "name_label": "👤 Name",
        "next_button": "▶️ Next",
        "error_missing_info": "⚠️ Oops! Please enter both your student ID and name.",
        "instructions_title": "📖 How to Use MathBuddy",
        "instructions_body": """
           **1. Start a Conversation:** Explain your math question, problem, or goal.
           **2. Get Guided Feedback:** MathBuddy will ask questions and suggest improvements.
           **3. Ask Anything:** Don't hesitate to ask for clarification.
           **4. Move On When Ready:** When you're done, just click the **Next** button.
        """,
        "previous_button": "◀️ Previous",
        "chat_title": "💬 Start Chatting with MathBuddy",
        "chat_prompt": "Describe your math question or upload a document to begin!",
        "tab_direct_chat": "✍️ Direct Chat",
        "tab_document_chat": "📄 Chat with a Document",
        "header_type_question": "Type your question here",
        "chat_placeholder": "Ask MathBuddy a question and press Enter...",
        "header_upload_file": "Upload a file to discuss",
        "file_uploader_label": "📁 Choose a PDF or image file",
        "file_process_spinner": "Processing file...",
        "file_process_success": "✅ Successfully processed **{file_name}**.",
        "doc_chat_placeholder": "Ask a question about your document...",
        "subheader_recent_exchange": "📌 Most Recent Exchange",
        "info_first_exchange": "Your first exchange will appear here.",
        "subheader_full_history": "📜 Full Chat History",
        "graph_error": "⚠️ An error occurred while generating the graph:\n{e}",
        "wrap_up_title": "🎉 Wrap-Up: Final Reflection",
        "spinner_generating_feedback": "Generating your feedback summary...",
        "subheader_feedback_summary": "📋 Feedback Summary",
        "feedback_not_generated": "No summary generated yet.",
        "save_failed": "❌ Failed to save conversation. Please try again!",
        "initial_prompt": (
            "You are a helpful, supportive chatbot named MathBuddy. Your job is to guide college-level math students without solving problems for them. "
            "Your tone is friendly, clear, and educational. Do not use LaTeX or special symbols. Explain math in plain English. "
            "If the user asks for a graph of a specific function (e.g., 'graph y=x^2'), your response MUST start immediately with the Python code block and contain NOTHING ELSE. "
            "The code must be enclosed in a single Python code block (```python...). "
            "Your code will be executed in an environment where `fig, ax = plt.subplots()` has ALREADY been run. "
            "Therefore, you MUST NOT include `import matplotlib.pyplot as plt` or `fig, ax = plt.subplots()` in your code. "
            "You MUST use the pre-existing `ax` variable to plot (e.g., `ax.plot(...)`, `ax.set_title(...)`, `ax.grid(True)`). "
            "Do NOT provide code for a different function than the one requested. Do not include `plt.show()`."
        )
    },
    "es": {
        "page_title": "MathBuddy",
        "welcome_title": "📚 Bienvenido a MathBuddy",
        "welcome_image_caption": "Tu Compañero de Estudio para el Éxito en Matemáticas 📱",
        "welcome_prompt": "Por favor, ingresa tu número de estudiante y tu nombre para comenzar.",
        "student_id_label": "🆔 Número de Estudiante",
        "name_label": "👤 Nombre",
        "next_button": "▶️ Siguiente",
        "error_missing_info": "⚠️ ¡Uy! Por favor, ingresa tanto tu número de estudiante como tu nombre.",
        "instructions_title": "📖 Cómo Usar MathBuddy",
        "instructions_body": """
           **1. Inicia una Conversación:** Explica tu pregunta de matemáticas, problema u objetivo.
           **2. Recibe Orientación:** MathBuddy te hará preguntas y sugerirá mejoras.
           **3. Pregunta lo que Quieras:** No dudes en pedir aclaraciones.
           **4. Avanza Cuando Estés Listo:** Cuando termines, simplemente haz clic en el botón **Siguiente**.
        """,
        "previous_button": "◀️ Anterior",
        "chat_title": "💬 Comienza a Chatear con MathBuddy",
        "chat_prompt": "¡Describe tu pregunta de matemáticas o sube un documento para empezar!",
        "tab_direct_chat": "✍️ Chat Directo",
        "tab_document_chat": "📄 Chatear con un Documento",
        "header_type_question": "Escribe tu pregunta aquí",
        "chat_placeholder": "Haz una pregunta a MathBuddy y presiona Enter...",
        "header_upload_file": "Sube un archivo para discutir",
        "file_uploader_label": "📁 Elige un archivo PDF o de imagen",
        "file_process_spinner": "Procesando archivo...",
        "file_process_success": "✅ Se procesó exitosamente **{file_name}**.",
        "doc_chat_placeholder": "Haz una pregunta sobre tu documento...",
        "subheader_recent_exchange": "📌 Intercambio Más Reciente",
        "info_first_exchange": "Tu primer intercambio aparecerá aquí.",
        "subheader_full_history": "📜 Historial de Chat Completo",
        "graph_error": "⚠️ Ocurrió un error al generar el gráfico:\n{e}",
        "wrap_up_title": "🎉 Conclusión: Reflexión Final",
        "spinner_generating_feedback": "Generando tu resumen de retroalimentación...",
        "subheader_feedback_summary": "📋 Resumen de Retroalimentación",
        "feedback_not_generated": "Aún no se ha generado un resumen.",
        "save_failed": "❌ No se pudo guardar la conversación. ¡Inténtalo de nuevo!",
        "initial_prompt": (
            "Eres un chatbot servicial y de apoyo llamado MathBuddy. Tu trabajo es guiar a estudiantes universitarios de matemáticas sin resolver los problemas por ellos. "
            "Tu tono es amigable, claro y educativo. No uses LaTeX ni símbolos especiales. Explica las matemáticas en español sencillo. "
            "Si el usuario pide un gráfico de una función específica (por ejemplo, 'grafica y=x^2'), tu respuesta DEBE comenzar inmediatamente con el bloque de código de Python y no contener NADA MÁS. "
            "El código debe estar dentro de un único bloque de código de Python (```python...). "
            "Tu código se ejecutará en un entorno donde `fig, ax = plt.subplots()` YA ha sido ejecutado. "
            "Por lo tanto, NO DEBES incluir `import matplotlib.pyplot as plt` ni `fig, ax = plt.subplots()` en tu código. "
            "DEBES usar la variable preexistente `ax` para graficar (por ejemplo, `ax.plot(...)`, `ax.set_title(...)`, `ax.grid(True)`). "
            "NO proporciones código para una función diferente a la solicitada. No incluyas `plt.show()`."
        )
    }
}

# --- GLOBAL CONFIGURATION AND SETUP ---
st.set_page_config(page_title="MathBuddy", page_icon="🧮", layout="centered")

# --- LANGUAGE SELECTOR IN SIDEBAR ---
st.sidebar.title("Language / Idioma")
language_options = ('English', 'Español')
selected_language = st.sidebar.radio("lang_select", options=language_options, label_visibility="collapsed")

lang_code = 'es' if selected_language == 'Español' else 'en'
if 'language' not in st.session_state or st.session_state.language != lang_code:
    st.session_state.language = lang_code
    st.rerun()

# --- HELPER FUNCTIONS ---
def t(key):
    return translations.get(st.session_state.language, {}).get(key, f"<{key}>")

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
MODEL = 'gpt-4o'
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_file(file):
    try:
        if file.type == "application/pdf":
            doc = fitz.open(stream=file.read(), filetype="pdf")
            return "".join(page.get_text() for page in doc)
        elif file.type.startswith("image/"):
            return pytesseract.image_to_string(Image.open(file))
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
        return None

def save_to_db(all_data):
    number = st.session_state.get('user_number', '').strip()
    name = st.session_state.get('user_name', '').strip()
    if not number or not name:
        st.error(t("error_missing_info"))
        return False
    try:
        db = pymysql.connect(host=st.secrets["DB_HOST"], user=st.secrets["DB_USER"], password=st.secrets["DB_PASSWORD"], database=st.secrets["DB_DATABASE"], charset="utf8mb4", autocommit=True)
        cursor = db.cursor()
        chat = json.dumps(all_data, ensure_ascii=False)
        sql = "INSERT INTO qna (number, name, chat, time) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (number, name, chat, datetime.now()))
        cursor.close()
        db.close()
        return True
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
        return False

def get_chatgpt_response(prompt, context=""):
    system_prompt = t('initial_prompt')
    system_messages = [{"role": "system", "content": system_prompt}]
    if context:
        context_prompt_text = "Use the following content from an uploaded document to answer the user's questions.\n\nDOCUMENT CONTENT:\n"
        if st.session_state.language == 'es':
            context_prompt_text = "Usa el siguiente contenido de un documento subido para responder las preguntas del usuario.\n\nCONTENIDO DEL DOCUMENTO:\n"
        system_messages.append({"role": "system", "content": context_prompt_text + context[:4000]})
    
    messages_to_send = system_messages + st.session_state.get("messages", []) + [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=MODEL, messages=messages_to_send)
    answer = response.choices[0].message.content
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.recent_message = {"user": prompt, "assistant": answer}

def handle_direct_chat():
    prompt = st.session_state.direct_chat_box
    if prompt and prompt.strip():
        get_chatgpt_response(prompt)
        st.session_state.direct_chat_box = ""

def render_message_content(content):
    match = re.search(r"```(python)?\n?(.*)```", content, re.DOTALL)
    if match and ('ax.plot' in content or 'ax.scatter' in content):
        code = match.group(2).strip()
        try:
            fig, ax = plt.subplots()
            exec(code, {'plt': plt, 'np': np, 'ax': ax, 'fig': fig})
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.error(t("graph_error").format(e=e))
            st.code(code, language='python')
    else:
        st.markdown(content)

# --- PAGE DEFINITIONS ---

def page_1():
    st.title(t("welcome_title"))
    st.image("mathbuddy_promo.png", caption=t("welcome_image_caption"), width=300)
    st.write(t("welcome_prompt"))
    st.session_state.user_number = st.text_input(t("student_id_label"), value=st.session_state.get("user_number", ""))
    st.session_state.user_name = st.text_input(t("name_label"), value=st.session_state.get("user_name", ""))
    if st.button(t("next_button"), key="page1_next"):
        if not st.session_state.user_number.strip() or not st.session_state.user_name.strip():
            st.error(t("error_missing_info"))
        else:
            st.session_state.step = 2
            st.rerun()

def page_2():
    st.title(t("instructions_title"))
    st.info(t("instructions_body"))
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("previous_button")):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button(t("next_button"), key="page2_next"):
            st.session_state.step = 3
            st.rerun()

def page_3():
    st.title(t("chat_title"))
    st.write(t("chat_prompt"))
    tab1, tab2 = st.tabs([t("tab_direct_chat"), t("tab_document_chat")])

    with tab1:
        st.header(t("header_type_question"))
        st.text_input("...", key="direct_chat_box", on_change=handle_direct_chat, placeholder=t("chat_placeholder"), label_visibility="collapsed")

    with tab2:
        st.header(t("header_upload_file"))
        uploaded_file = st.file_uploader(t("file_uploader_label"), type=["pdf", "png", "jpg", "jpeg"])
        if uploaded_file and st.session_state.get("processed_file_name") != uploaded_file.name:
            with st.spinner(t("file_process_spinner")):
                st.session_state.file_text = extract_text_from_file(uploaded_file)
                st.session_state.processed_file_name = uploaded_file.name
        if st.session_state.get("file_text"):
            st.success(t("file_process_success").format(file_name=st.session_state.processed_file_name))
            if prompt := st.chat_input(t("doc_chat_placeholder")):
                get_chatgpt_response(prompt, context=st.session_state.file_text)
                st.rerun()

    st.divider()
    st.subheader(t("subheader_recent_exchange"))
    recent = st.session_state.get("recent_message", {"user": "", "assistant": ""})
    if recent["user"] or recent["assistant"]:
        with st.chat_message("user"):
            st.markdown(recent["user"])
        with st.chat_message("assistant"):
            render_message_content(recent["assistant"])
    else:
        st.info(t("info_first_exchange"))
    
    st.divider()
    st.subheader(t("subheader_full_history"))
    if st.session_state.messages:
        for msg in reversed(st.session_state.messages):
            with st.chat_message(msg["role"]):
                render_message_content(msg["content"])

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("previous_button")):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button(t("next_button"), key="page3_next"):
            st.session_state.step = 4
            st.session_state.feedback_saved = False
            st.rerun()

def page_4():
    st.title(t("wrap_up_title"))
    if not st.session_state.get("feedback_saved"):
        with st.spinner(t("spinner_generating_feedback")):
            chat_history = "\n".join(f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages)
            prompt_summary_en = f"This is a conversation between a student and MathBuddy:\n{chat_history}\n\nPlease summarize the key concepts discussed, note the student's areas of strength, and suggest improvements or study tips for them to continue their learning."
            prompt_summary_es = f"Esta es una conversación entre un estudiante y MathBuddy:\n{chat_history}\n\nPor favor, resume los conceptos clave discutidos, señala las fortalezas del estudiante y sugiere mejoras o consejos de estudio para que continúen aprendiendo."
            prompt = prompt_summary_es if st.session_state.language == 'es' else prompt_summary_en
            response = client.chat.completions.create(model=MODEL, messages=[{"role": "system", "content

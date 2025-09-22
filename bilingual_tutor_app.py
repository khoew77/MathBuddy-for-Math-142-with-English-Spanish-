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
        "lang_selector_label": "Select your language:",
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
            "You are a helpful, supportive chatbot named MathBuddy... (Your full English prompt here)"
        )
    },
    "es

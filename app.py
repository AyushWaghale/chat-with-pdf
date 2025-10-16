import streamlit as st
import google.generativeai as genai
import PyPDF2

# -----------------------
# Theme Toggle Functions
# -----------------------
st.set_page_config(page_title="🖊️PDF Summarizer Chatbot")
ms = st.session_state
if "themes" not in ms:
    ms.themes = {
        "current_theme": "light",   
        "refreshed": True,
        "light": {
            "theme.base": "dark",
            "theme.backgroundColor": "#FFFFFF",
            "theme.primaryColor": "#6200EE",
            "theme.secondaryBackgroundColor": "#F5F5F5",
            "theme.textColor": "000000",
            "button_face": "🌜"
        },
        "dark": {
            "theme.base": "light",
            "theme.backgroundColor": "#121212",
            "theme.primaryColor": "#BB86FC",
            "theme.secondaryBackgroundColor": "#1F1B24",
            "theme.textColor": "#E0E0E0",
            "button_face": "🌞"
        }
    }

def ChangeTheme():
    previous_theme = ms.themes["current_theme"]
    tdict = ms.themes["light"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]
    for vkey, vval in tdict.items():
        if vkey.startswith("theme"):
            st._config.set_option(vkey, vval)
    ms.themes["refreshed"] = False
    if previous_theme == "dark":
        ms.themes["current_theme"] = "light"
    elif previous_theme == "light":
        ms.themes["current_theme"] = "dark"

btn_face = ms.themes["light"]["button_face"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]["button_face"]
st.button(btn_face, on_click=ChangeTheme)

if ms.themes["refreshed"] == False:
    ms.themes["refreshed"] = True
    st.rerun()

# -----------------------
# PDF Extraction Function
# -----------------------
def extract_text_from_pdf(pdf_file):
    """Extract text from an uploaded PDF file."""
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

# -----------------------
# Sidebar: API Key & Upload
# -----------------------
with st.sidebar:
    st.title('🖊️PDF Summarizer Chatbot')
    if 'GEMINI_API_KEY' in st.secrets:
        # st.success('Gemini API key already provided!', icon='✅')
        gemini_api_key = st.secrets['GEMINI_API_KEY']
    else:
        gemini_api_key = st.text_input('Enter Gemini API key:', type='password')
        if not (gemini_api_key and len(gemini_api_key) >= 20):
            st.warning('Please enter your Gemini API credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    pdf_text = ""
    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            pdf_text = extract_text_from_pdf(uploaded_file)
        st.success("PDF uploaded and text extracted!")

    

# -----------------------
# LLM Generation Function
# -----------------------
def generate_gemini_response(text, question, gemini_api_key):
    genai.configure(api_key=gemini_api_key)
    prompt = f"Here is the context:\n\n{text[:5000]}\n\nNow answer this question:\n{question}"
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    if hasattr(response, 'text'):
        return response.text
    return str(response)

# -----------------------
# Chat Message Display Logic
# -----------------------
if "messages" not in ms:
    ms.messages = [{"role": "assistant", "content": "Upload a PDF file from the sidebar to get started."}]

for message in ms.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    ms.messages = [{"role": "assistant", "content": "Upload a PDF file from the sidebar to get started."}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# -----------------------
# Main Q&A Logic (Chatbot)
# -----------------------
if pdf_text and gemini_api_key and len(gemini_api_key) >= 20:
    question = st.text_input("Enter your question:")
    if question:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_gemini_response(pdf_text, question, gemini_api_key)
                st.write(response)
        message = {"role": "assistant", "content": response}
        ms.messages.append(message)

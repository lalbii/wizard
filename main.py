import streamlit as st
import google.generativeai as genai

# 🔐 Configure Gemini
genai.configure(api_key="AIzaSyBuHM-pPVIiC-hfr0_LXF0vqRqBgL4faBs")  # Replace with your actual API key
model = genai.GenerativeModel("models/gemini-1.5-flash")
# Initialize chat + message history
# Init session
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "json_prompt_sent" not in st.session_state:
    st.session_state.json_prompt_sent = False

# UI
st.set_page_config(page_title="Brief Wizard Chat", page_icon="💬", layout="centered")
uploaded_file = st.file_uploader("📁 Upload your brief file (TXT or PDF)", type=["txt", "pdf"])

st.title("Brief Wizard powered by Ai")
st.markdown("Chat until Ai gets everything it needs for your brief.")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
user_input = st.chat_input("Type your answer...")

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # First message: format prompt + user input
    if not st.session_state.json_prompt_sent:
        prompt = (
            f"Ham Brief: {user_input}\n\n"
            "Please fill in the values into the following JSON format for the project brief while keeping the descriptions. "
            "Ask me questions to fill in missing values. Once all is known, output only the final JSON.\n\n"
            "{\n"
            "  \"project_name\": \"<Insert Project Name Here>\",\n"
            "  \"goal\": \"<Insert Project Goal Here>\",\n"
            "  \"target_audience\": {\n"
            "    \"age_range\": \"<Insert Age Range Here>\",\n"
            "    \"gender\": \"<Insert Gender Here>\",\n"
            "    \"interests\": \"<Insert Interests Here>\",\n"
            "    \"demographics\": \"<Insert Demographics Here>\"\n"
            "  },\n"
            "  \"message\": \"<Insert Message Here>\",\n"
            "  \"tone_and_style\": \"<Insert Tone and Style Here>\",\n"
            "  \"delivery_content\": \"<Insert Content Type Here>\",\n"
            "  \"delivery_deadline\": \"<Insert Delivery Deadline Here>\",\n"
            "  \"required_elements\": {\n"
            "    \"text\": \"<Insert Text Elements Here>\",\n"
            "    \"images\": \"<Insert Images Required Here>\",\n"
            "    \"image_references\": \"<Insert Image References Here>\"\n"
            "  }\n"
            "}"
        )
        response = st.session_state.chat.send_message(prompt)
        st.session_state.json_prompt_sent = True
    else:
        # Continue chat with user reply
        response = st.session_state.chat.send_message(user_input)

    # Show assistant response
    ai_reply = response.text
    st.chat_message("assistant").markdown(ai_reply)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
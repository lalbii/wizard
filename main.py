import streamlit as st
import google.generativeai as genai
from PIL import Image
import re
import json
import os

# 🔐 Configure Gemini
  # Replace with your actual API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.0-flash")
# Initialize chat + message history
# Init session
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "json_prompt_sent" not in st.session_state:
    st.session_state.json_prompt_sent = False
if "brief_json" not in st.session_state:
    st.session_state.brief_json = None
# UI
st.set_page_config(page_title="Brief Wizard Chat", page_icon="💬", layout="centered")




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

    # Try to extract JSON from Gemini response
    json_match = re.search(r"{[\s\S]*}", ai_reply)
    if json_match:
        json_text = json_match.group(0)

        try:
            json.loads(json_text)  # Validate it
            st.session_state.brief_json = json_text
            st.success("✅ Brief JSON completed!")
        except json.JSONDecodeError:
            st.warning("⚠️ Gemini replied with something that looks like JSON, but it’s not valid.")


# 2. Show image upload and feedback only after brief is complete
if st.session_state.brief_json:
    uploaded_image = st.file_uploader("🖼️ Upload your design (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        img = Image.open(uploaded_image)
        st.image(img, caption="Uploaded design", use_column_width=True)

        if st.button("💬 Ask Gemini for Design Feedback"):
            prompt_text = (
                "You are a brand consultant reviewing a design image.\n"
                "Based on the following completed brief, provide detailed feedback:\n"
                f"{st.session_state.brief_json}\n\n"
                "- Does the design align with the brand tone, message, and audience?\n"
                "- Suggest improvements and comment on style consistency."
            )
        
            # Convert image to byte data
            #image_bytes = uploaded_image.read()
        
            # Call Gemini Vision with image + text
            with st.spinner("🧠 Gemini is thinking..."):
                response = model.generate_content(
                    [img, prompt_text]
                )
        
            st.subheader("🎯 Gemini's Feedback:")
            st.markdown(response.text)
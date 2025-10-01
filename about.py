import streamlit as st
import json
import datetime
from typing import Dict, List

# Configure the page
st.set_page_config(
    page_title="Engr. Shabir Bot",
    page_icon="🤖",
    layout="centered"
)

# Bot knowledge base
BOT_KNOWLEDGE = {
    "skills": {
        "python": "Expert in Python for ML, web development, and automation",
        "django": "Full-stack development with Django framework",
        "fastapi": "Building high-performance APIs with FastAPI",
        "streamlit": "Creating interactive web apps with Streamlit",
        "machine learning": "Scikit-learn, TensorFlow, PyTorch for ML models",
        "power bi": "Data visualization and business intelligence dashboards",
        "mongodb": "NoSQL database management and operations",
        "mysql": "Relational database design and SQL queries"
    },
    "experience": {
        "current": "Working as Data Analyst at SnippRetail (2025-Present), built Power BI dashboards and automated reporting",
        "freelance": "Fiverr freelancer since 2021, completed 100+ data analysis projects",
        "kyc": "KYC Agent at Revolut via Mindbridge, handled global client verification",
        "ml intern": "ML Intern at BiStarX, built segmentation and prediction models"
    },
    "education": {
        "degree": "BSc Computer Systems Engineering from Islamia University, Bahawalpur",
        "gpa": "CGPA: 3.62/4.00",
        "certification": "Registered Engineer with PEC (Reg# COMP/024380)"
    },
    "personal": {
        "status": "Focused on career growth and professional development",
        "relationship": "Currently single and dedicated to building my career",
        "appearance": "Professional and well-groomed engineer with a passion for technology",
        "dream": "To become a leading AI/ML engineer and contribute to open-source projects"
    },
    "projects": {
        "email extractor": "OCR-based email extraction app using Streamlit + Tesseract",
        "ai agent": "LangChain chatbot with PDF retrieval capabilities",
        "decision tree": "Interactive ML app for hyperparameter tuning",
        "text to image": "Prompt-based image generation application"
    }
}


def get_bot_response(user_input: str) -> str:
    """Generate bot response based on user input"""
    input_lower = user_input.lower()

    # Greeting responses
    if any(word in input_lower for word in ["hi", "hello", "hey", "hola"]):
        return "Hello! I'm Engr. Shabir's AI assistant. 🤖 How can I help you learn about his skills, experience, or projects today?"

    # Skills related
    elif any(word in input_lower for word in ["skill", "what can you do", "expert", "technology"]):
        skills_list = "\n".join([f"• {skill}: {desc}" for skill, desc in BOT_KNOWLEDGE["skills"].items()])
        return f"**Engr. Shabir's Technical Skills:**\n\n{skills_list}"

    # Experience related
    elif any(word in input_lower for word in ["experience", "work", "job", "career"]):
        exp_text = "\n".join([f"• **{key.title()}**: {value}" for key, value in BOT_KNOWLEDGE["experience"].items()])
        return f"**Professional Experience:**\n\n{exp_text}"

    # Education related
    elif any(word in input_lower for word in ["education", "degree", "study", "university"]):
        edu_text = "\n".join([f"• {key.title()}: {value}" for key, value in BOT_KNOWLEDGE["education"].items()])
        return f"**Education & Certifications:**\n\n{edu_text}"

    # Personal questions
    elif any(word in input_lower for word in ["married", "girlfriend", "relationship", "single"]):
        return f"**Relationship Status:** {BOT_KNOWLEDGE['personal']['relationship']} 💼"

    elif any(word in input_lower for word in ["beautiful", "handsome", "look", "appearance"]):
        return f"**About Appearance:** {BOT_KNOWLEDGE['personal']['appearance']} 👨‍💻"

    elif any(word in input_lower for word in ["dream", "goal", "aspiration", "future"]):
        return f"**Career Dream:** {BOT_KNOWLEDGE['personal']['dream']} 🚀"

    # Projects related
    elif any(word in input_lower for word in ["project", "app", "application", "demo"]):
        projects_text = "\n".join([f"• **{key.title()}**: {value}" for key, value in BOT_KNOWLEDGE["projects"].items()])
        return f"**Featured Projects:**\n\n{projects_text}\n\nCheck the live demos in the main app!"

    # Current work
    elif any(word in input_lower for word in ["doing now", "current work", "now", "present"]):
        return f"**Current Focus:** {BOT_KNOWLEDGE['experience']['current']} - Also working on freelance projects and skill enhancement."

    # Contact information
    elif any(word in input_lower for word in ["contact", "connect", "linkedin", "github", "email"]):
        contacts = """
        **Connect with Engr. Shabir:**
        
        • 📧 Email: muhammadshabir594@gmail.com  
        • 💼 LinkedIn: linkedin.com/in/engr-shabir-411357262  
        • 💻 GitHub: github.com/EngrShabir135  
        • 📊 Kaggle: kaggle.com/engrshabir  
        • 🛠️ Fiverr: fiverr.com/sellers/engrshabir683/edit
        """
        return contacts

    # Default response
    else:
        return "I'm Engr. Shabir's AI assistant! I can tell you about his skills, experience, education, projects, or personal details. What would you like to know? 🤔"


def main():
    # ✅ Initialize session state safely inside main()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_info" not in st.session_state:
        st.session_state.user_info = {}

    # Header section
    st.title("🤖 Engr. Shabir Bot")
    st.markdown("""
    Hi! I'm an interactive bot built by **Engr. Muhammad Shabir** 🤖
    
    💬 **Ask me anything like:**
    - What is he doing now?
    - Is he married or has a girlfriend?
    - What are his skills, education or dream?
    - Is Engr. Shabir beautiful?
    
    🧠 **I store your conversation & answer smartly.**
    """)

    st.divider()

    # Display conversation history
    for message in st.session_state.get("messages", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about Engr. Shabir..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        response = get_bot_response(prompt)

        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

    # Sidebar with additional info
    with st.sidebar:
        st.header("📊 Quick Info")
        st.markdown("""
        **Engr. Muhammad Shabir**
        
        🎓 Computer Systems Engineer  
        📈 Data Analyst & ML Developer  
        🌍 Open Source Contributor
        
        **Technical Stack:**
        - Python, Django, FastAPI
        - Machine Learning
        - Power BI, Streamlit
        - MongoDB, MySQL
        """)

        st.divider()

        st.subheader("🎯 Conversation Stats")
        st.write(f"Messages exchanged: {len(st.session_state.get('messages', []))}")

        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.rerun()

        st.divider()

        st.markdown("""
        **Live Project Demos:**
        - [Email Extractor](https://emails-extraction-app.streamlit.app/)
        - [AI Agent](https://free-ai-agent-u7xnwhxsavuvwshjvjxnen.streamlit.app/)
        - [Decision Tree Tuner](https://hyperparameter-on-decision-treegit-4glhczrbnhjbjxnnur8fkx.streamlit.app/)
        - [Text-to-Image Generator](https://text-to-image-convertor-dqhy2cld5rverkmq6mdoht.streamlit.app/)
        """)


if __name__ == "__main__":
    main()

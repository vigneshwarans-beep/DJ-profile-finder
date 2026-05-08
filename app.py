import asyncio
import sys
import os

# Ensure Playwright browser is installed (required for Streamlit Cloud deployment)
os.system("playwright install chromium")

# Fix for Playwright NotImplementedError on Windows with Streamlit
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
from datetime import datetime
from scraper import run_job_search
from database import init_db, JobSearchQuery, Candidate

# Initialize DB to fetch history
engine, session = init_db()

AVATAR_IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mouse_avatar.png")

# Page Config
st.set_page_config(page_title="DJ Profile Finder", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# Custom CSS to mimic ChatGPT Light Mode
st.markdown("""
<style>
    /* Force light mode background */
    .stApp {
        background-color: #FFFFFF;
        color: #202123;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #F9F9F9;
        border-right: 1px solid #E5E5E5;
    }
    
    /* Make sidebar toggle visible by keeping header */
    
    /* Chat inputs */
    .stChatInput {
        background-color: #FFFFFF;
        border: 1px solid #D9D9E3 !important;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
    
    /* User Message Bubble */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #FFFFFF;
        border-bottom: 1px solid #E5E5E5;
        padding: 20px 10%;
    }
    /* Assistant Message Bubble */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #F7F7F8;
        border-bottom: 1px solid #E5E5E5;
        padding: 20px 10%;
    }
    
    /* Make Streamlit buttons in sidebar look like ChatGPT items */
    [data-testid="stSidebar"] [data-testid="stButton"] button {
        background-color: transparent;
        border: none;
        color: #343541;
        text-align: left;
        padding: 5px 10px;
        width: 100%;
        border-radius: 5px;
        justify-content: flex-start;
        font-weight: normal;
        box-shadow: none;
        margin-bottom: 0px;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        background-color: #ECECEC;
        color: #343541;
    }
    
    /* Primary button style for 'New Chat' */
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
        background-color: #000000;
        color: #FFFFFF;
        font-weight: 500;
        justify-content: center;
        margin-bottom: 15px;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #333333;
        color: #FFFFFF;
    }
    
    /* Hide Streamlit branding */
    footer {visibility: hidden;}
    
    /* Header customization */
    header[data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
    }

    /* Right Sidebar custom CSS */
    div[data-testid="column"]:has(.right-sidebar-marker),
    div[data-testid="stColumn"]:has(.right-sidebar-marker) {
        position: fixed !important;
        right: 0;
        top: 0;
        height: 100vh !important;
        background-color: #F9F9F9 !important;
        border-left: 1px solid #E5E5E5 !important;
        padding: 20px !important;
        padding-top: 60px !important; /* Make room for the floating buttons */
        z-index: 9999 !important;
        overflow-y: auto;
    }
    
    div[data-testid="column"]:has(.chat-col-marker),
    div[data-testid="stColumn"]:has(.chat-col-marker) {
        width: 100% !important;
        flex: none !important;
    }

    div[data-testid="column"]:has(.open-sidebar-marker),
    div[data-testid="stColumn"]:has(.open-sidebar-marker) {
        position: fixed !important;
        right: 20px;
        top: 20px;
        z-index: 100;
        width: auto !important;
        flex: none !important;
    }
    
    /* Typography */
    * {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- AUTHENTICATION -----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    import streamlit.components.v1 as components
    
    # Render the full screen Vanta background via a fixed iframe
    components.html("""
        <!DOCTYPE html>
        <html>
        <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js"></script>
        <style>
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; }
            #vanta-bg { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; }
        </style>
        </head>
        <body>
        <div id="vanta-bg"></div>
        <script>
        VANTA.NET({
          el: "#vanta-bg",
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 200.00,
          minWidth: 200.00,
          scale: 1.00,
          scaleMobile: 1.00,
          color: 0x3b82f6,
          backgroundColor: 0xffffff,
          points: 15.00,
          maxDistance: 25.00,
          spacing: 18.00
        });
        
        // Hack to make the Streamlit iframe full screen
        const doc = window.parent.document;
        const iframes = doc.querySelectorAll('iframe');
        for (let iframe of iframes) {
            if (iframe.srcdoc && iframe.srcdoc.includes('vanta-bg')) {
                iframe.style.position = 'fixed';
                iframe.style.top = '0';
                iframe.style.left = '0';
                iframe.style.width = '100vw';
                iframe.style.height = '100vh';
                iframe.style.zIndex = '0';
                iframe.style.border = 'none';
            }
        }
        
        // Make Streamlit's main block transparent so we can see the iframe behind it
        const stApp = doc.querySelector('.stApp');
        if (stApp) {
            stApp.style.background = 'transparent';
        }
        </script>
        </body>
        </html>
    """, height=0)

    # Now render the login card on top
    st.markdown("""
        <style>
        /* Force the login card to be elevated above the background */
        [data-testid="stAppViewBlockContainer"] {
            z-index: 10;
            position: relative;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; margin-top: 10vh;'>Welcome to DJ Profile Finder</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555; margin-bottom: 50px;'>Sign in to access your recruitment dashboard</p>", unsafe_allow_html=True)
    
    _, center_col, _ = st.columns([1, 1.2, 1])
    
    with center_col:
        st.markdown("<div style='padding: 40px; border-radius: 16px; background-color: rgba(255, 255, 255, 0.85); box-shadow: 0 8px 32px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.5); backdrop-filter: blur(10px);'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top: 0; text-align: center;'>Login</h3>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            
            if submitted:
                if username == "admin" and password == "admin":
                    st.session_state.authenticated = True
                    # Reset background back to white when logged in
                    components.html("<script>window.parent.document.querySelector('.stApp').style.background = '#FFFFFF';</script>", height=0)
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.stop()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    # Black and White Logo + Title Header
    st.markdown('''
    <div style="display: flex; align-items: center; margin-bottom: 15px; padding-left: 5px;">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2ZM4 12C4 7.58172 7.58172 4 12 4C16.4183 4 20 7.58172 20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12Z" fill="black"/>
            <path d="M12 6C8.68629 6 6 8.68629 6 12C6 15.3137 8.68629 18 12 18C15.3137 18 18 15.3137 18 12C18 8.68629 15.3137 6 12 6Z" fill="black"/>
            <path d="M12 10C10.8954 10 10 10.8954 10 12C10 13.1046 10.8954 14 12 14C13.1046 14 14 13.1046 14 12C14 10.8954 13.1046 10 12 10Z" fill="white"/>
        </svg>
        <span style="font-size: 20px; font-weight: 600; margin-left: 10px; color: black; letter-spacing: -0.5px;">DJ Profile Finder</span>
    </div>
    ''', unsafe_allow_html=True)
    
    if st.button("📝 New chat", type="primary"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("<p style='font-size: 12px; color: #8E8EA0; font-weight: 600; padding-left: 10px; margin-top: 15px; margin-bottom: 5px;'>🎯 Search Filters</p>", unsafe_allow_html=True)
    target_location = st.text_input("Location", placeholder="e.g., San Francisco, CA", key="target_location")
    
    st.markdown("<p style='font-size: 12px; color: #8E8EA0; font-weight: 600; padding-left: 10px; margin-top: 10px; margin-bottom: 5px;'>Recents</p>", unsafe_allow_html=True)
    
    recent_searches = session.query(JobSearchQuery).order_by(JobSearchQuery.id.desc()).limit(5).all()
    for search in recent_searches:
        title = search.job_description[:25].replace('\n', ' ') + "..."
        if st.button(f"🔍 {title}", key=f"hist_{search.id}"):
            st.session_state.messages.append({"role": "assistant", "content": f"You clicked on a past search! That JD was:\n\n> {search.job_description[:100]}..."})
            st.rerun()
    
    st.markdown("<p style='font-size: 12px; color: #8E8EA0; font-weight: 600; padding-left: 10px; margin-top: 15px; margin-bottom: 5px;'>📁 My Folders</p>", unsafe_allow_html=True)
    if st.button("📁 Engineering Roles", key="fold_eng"):
        st.session_state.messages.append({"role": "assistant", "content": "Opening your **Engineering Roles** folder... Here you will be able to organize URLs by role soon."})
        st.rerun()
    if st.button("📁 Sales / Marketing", key="fold_sales"):
        st.session_state.messages.append({"role": "assistant", "content": "Opening your **Sales / Marketing** folder..."})
        st.rerun()
    if st.button("⭐ Saved Profiles", key="fold_saved"):
        from scraper import extract_keywords
        # Fetch all saved candidates from the SQLite database
        candidates = session.query(Candidate).all()
        if candidates:
            response = "### ⭐ Your Saved Profiles Database:\n\n"
            for c in candidates:
                skills = ", ".join(extract_keywords(c.headline, top_n=4)) if c.headline else "None"
                
                location_text = f" - {c.location}" if c.location else ""
                response += f"**{c.name}**{location_text}\n"
                
                if c.headline:
                    response += f"*{c.headline}*\n"
                    
                response += f"🔗 [LinkedIn Profile]({c.linkedin_url})\n"
                response += f"💡 **Matching Skills:** {skills.title()}\n\n---\n"
        else:
            response = "You don't have any saved profiles yet. Run a search to find some!"
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    st.markdown("<p style='font-size: 12px; color: #8E8EA0; font-weight: 600; padding-left: 10px; margin-top: 15px; margin-bottom: 5px;'>📄 Resume Database</p>", unsafe_allow_html=True)
    
    # Initialize resume list in session state
    if "resumes" not in st.session_state:
        st.session_state.resumes = ["John_Doe_Resume.pdf", "Sarah_Smith_CV.pdf"]
        
    uploaded_files = st.file_uploader("Upload Resume PDF / Docx", accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files:
        for f in uploaded_files:
            if f.name not in st.session_state.resumes:
                st.session_state.resumes.append(f.name)
                
    # Display the dynamic list of resumes
    for resume in st.session_state.resumes:
        if st.button(f"📄 {resume}", key=f"res_{resume}"):
            st.session_state.messages.append({"role": "assistant", "content": f"Viewing **{resume}**... Looks like a strong candidate! I've saved this to your Resume Database."})
            st.rerun()

    st.markdown("<p style='font-size: 12px; color: #8E8EA0; font-weight: 600; padding-left: 10px; margin-top: 15px; margin-bottom: 5px;'>📧 Email Settings</p>", unsafe_allow_html=True)
    with st.expander("Configure Outreach Email"):
        with st.form("email_settings_form"):
            email_sender_val = st.text_input("Gmail Address", value=st.session_state.get("email_sender", ""))
            email_pwd_val = st.text_input("App Password", type="password", value=st.session_state.get("email_password", ""))
            if st.form_submit_button("Save Credentials"):
                st.session_state.email_sender = email_sender_val
                st.session_state.email_password = email_pwd_val
                st.success("Credentials saved!")

    st.markdown("<p style='font-size: 12px; color: #8E8EA0; font-weight: 600; padding-left: 10px; margin-top: 15px; margin-bottom: 5px;'>🛂 I-94 Verification</p>", unsafe_allow_html=True)
    with st.expander("Verify Travel History"):
        with st.form("i94_form"):
            i94_fname = st.text_input("First Name")
            i94_lname = st.text_input("Last Name")
            i94_dob = st.date_input("Date of Birth", min_value=datetime(1900, 1, 1), max_value=datetime.today())
            i94_passport = st.text_input("Passport Number")
            i94_country = st.text_input("Country of Citizenship", value="India")
            i94_submit = st.form_submit_button("Pull I-94 History")
            
            if i94_submit:
                if i94_fname and i94_lname and i94_passport:
                    st.session_state.messages.append({"role": "user", "content": f"Please verify I-94 history for {i94_fname} {i94_lname} ({i94_passport})."})
                    st.session_state.run_i94 = {
                        "first_name": i94_fname,
                        "last_name": i94_lname,
                        "dob": i94_dob.strftime("%Y-%m-%d"),
                        "passport_number": i94_passport,
                        "country_of_citizenship": i94_country
                    }
                    st.rerun()
                else:
                    st.error("Please fill in Name and Passport.")

# ----------------- MAIN UI -----------------

if "show_right_sidebar" not in st.session_state:
    st.session_state.show_right_sidebar = True

if "sidebar_width" not in st.session_state:
    st.session_state.sidebar_width = 380

if st.session_state.show_right_sidebar:
    import streamlit.components.v1 as components
    components.html("""
        <script>
            const doc = window.parent.document;
            let savedWidth = doc.defaultView.localStorage.getItem('right_sidebar_width') || 380;
            
            function updateWidth(width) {
                let styleTag = doc.getElementById('dynamic-right-sidebar');
                if (!styleTag) {
                    styleTag = doc.createElement('style');
                    styleTag.id = 'dynamic-right-sidebar';
                    doc.head.appendChild(styleTag);
                }
                styleTag.innerHTML = `
                    div[data-testid="column"]:has(.right-sidebar-marker),
                    div[data-testid="stColumn"]:has(.right-sidebar-marker) {
                        width: ${width}px !important;
                    }
                    [data-testid="stAppViewBlockContainer"] {
                        padding-right: ${parseInt(width) + 20}px !important;
                    }
                `;
            }
            
            updateWidth(savedWidth);
            
            const cols = doc.querySelectorAll('div[data-testid="column"], div[data-testid="stColumn"]');
            let rightSidebar = null;
            for (let col of cols) {
                if (col.querySelector('.right-sidebar-marker')) {
                    rightSidebar = col;
                    break;
                }
            }
            
            if (rightSidebar && !rightSidebar.querySelector('.custom-resizer')) {
                const resizer = doc.createElement('div');
                resizer.className = 'custom-resizer';
                resizer.style.width = '10px';
                resizer.style.height = '100%';
                resizer.style.position = 'absolute';
                resizer.style.left = '-5px'; 
                resizer.style.top = '0';
                resizer.style.cursor = 'ew-resize';
                resizer.style.zIndex = '100000';
                resizer.style.backgroundColor = 'transparent';
                
                let isResizing = false;
                
                resizer.addEventListener('mouseenter', () => {
                    resizer.style.borderLeft = '2px solid #FF4B4B';
                });
                resizer.addEventListener('mouseleave', () => {
                    if (!isResizing) resizer.style.borderLeft = 'none';
                });
                
                rightSidebar.appendChild(resizer);
                
                resizer.addEventListener('mousedown', function(e) {
                    isResizing = true;
                    resizer.style.borderLeft = '2px solid #FF4B4B';
                    doc.body.style.cursor = 'ew-resize';
                    e.preventDefault();
                });
                
                doc.addEventListener('mousemove', function(e) {
                    if (!isResizing) return;
                    let newWidth = doc.body.clientWidth - e.clientX;
                    if (newWidth < 250) newWidth = 250;
                    if (newWidth > 800) newWidth = 800;
                    updateWidth(newWidth);
                });
                
                doc.addEventListener('mouseup', function(e) {
                    if (isResizing) {
                        isResizing = false;
                        doc.body.style.cursor = '';
                        resizer.style.borderLeft = 'none';
                        let currentWidth = doc.body.clientWidth - e.clientX;
                        if (currentWidth < 250) currentWidth = 250;
                        if (currentWidth > 800) currentWidth = 800;
                        doc.defaultView.localStorage.setItem('right_sidebar_width', currentWidth);
                    }
                });
            }
        </script>
    """, height=0, width=0)
    chat_col, right_col = st.columns([10, 1])
    with chat_col:
        st.markdown('<div class="chat-col-marker"></div>', unsafe_allow_html=True)
    with right_col:
        st.markdown('<div class="right-sidebar-marker"></div>', unsafe_allow_html=True)
else:
    chat_col, open_col = st.columns([10, 1])
    with chat_col:
        st.markdown('<div class="chat-col-marker"></div>', unsafe_allow_html=True)
    with open_col:
        st.markdown('<div class="open-sidebar-marker"></div>', unsafe_allow_html=True)
        if st.button("‹", help="Open Right Panel"):
            st.session_state.show_right_sidebar = True
            st.rerun()
    right_col = None

def generate_friendly_response(user_input):
    """Simple rule-based conversational agent"""
    text = user_input.lower()
    if len(text) < 50 and not any(word in text for word in ["role", "require", "experience", "skills", "job"]):
        if "hi" in text or "hello" in text or "hey" in text:
            return "Hey! Great to see you. Got any tricky roles you're trying to fill today?"
        elif "how are you" in text:
            return "I'm doing fantastic, just hanging out in your hard drive! Ready to do some sourcing whenever you are. What's on the agenda?"
        elif "thanks" in text or "thank you" in text:
            return "You're very welcome! Let me know if you need anything else."
        elif "friend" in text:
            return "Aww, you're the best! I'm always here to help you out, friend. Drop a JD whenever you're ready to get to work."
        else:
            return "Haha, got it! Listen, whenever you're ready to start sourcing, just paste the Job Description for the role and I'll go scour LinkedIn for you."
    return None

with chat_col:
    st.markdown('''
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2ZM4 12C4 7.58172 7.58172 4 12 4C16.4183 4 20 7.58172 20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12Z" fill="black"/>
            <path d="M12 6C8.68629 6 6 8.68629 6 12C6 15.3137 8.68629 18 12 18C15.3137 18 18 15.3137 18 12C18 8.68629 15.3137 6 12 6Z" fill="black"/>
            <path d="M12 10C10.8954 10 10 10.8954 10 12C10 13.1046 10.8954 14 12 14C13.1046 14 14 13.1046 14 12C14 10.8954 13.1046 10 12 10Z" fill="white"/>
        </svg>
        <span style="font-family: cursive; font-size: 20px; font-weight: 600; margin-left: 10px; color: black; letter-spacing: -0.5px;">DJ Profile Finder</span>
    </div>
    <br>
    ''', unsafe_allow_html=True)

    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hey there! 👋 I'm your recruiting assistant. How's your day going? If you've got a role to fill, just paste the Job Description here and I'll track down some great candidates for you!"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"]=="user" else AVATAR_IMG):
            st.markdown(message["content"])
            if "image" in message:
                st.image(message["image"])

    if prompt := st.chat_input("Ask anything or paste a Job Description..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=AVATAR_IMG):
            message_placeholder = st.empty()
        
            friendly_reply = generate_friendly_response(prompt)
            
            if friendly_reply:
                message_placeholder.markdown(friendly_reply)
                st.session_state.messages.append({"role": "assistant", "content": friendly_reply})
            else:
                message_placeholder.markdown("Alright, I see you gave me some job details! Give me just a few seconds to scour the web and find you the best matches... 🕵️‍♂️")
                
                try:
                    location_filter = st.session_state.get("target_location", "")
                    
                    response_so_far = ""
                    total_profiles_found = 0
                    
                    from scraper import extract_keywords, run_job_search
                    
                    for batch_idx, results in enumerate(run_job_search(prompt, location=location_filter)):
                        if not results and batch_idx == 0:
                            response_so_far = "Ah, bummer! 😔 I couldn't find any good matches for that one. Do you think we could try tweaking the keywords or making it a bit more specific?"
                            message_placeholder.markdown(response_so_far)
                            break
                            
                        if not results:
                            break
                            
                        if batch_idx == 0:
                            response_so_far = f"### Awesome! I'm finding candidates for you in batches:\n\n"
                        
                        for res in results:
                            total_profiles_found += 1
                            skills = ", ".join(extract_keywords(res.get('headline', ''), top_n=4)) if res.get('headline') else "None"
                            match_pct = res.get('match_percentage', 75)
                            response_so_far += f"#### {total_profiles_found}. {res['name']} - **{match_pct}% Match**\n"
                            
                            if res.get('headline'):
                                response_so_far += f"*{res['headline']}*\n\n"
                                
                            if res.get('location'):
                                response_so_far += f"📍 {res['location']} | 🔗 [View LinkedIn Profile]({res['url']})\n"
                            else:
                                response_so_far += f"🔗 [View LinkedIn Profile]({res['url']})\n"
                                
                            response_so_far += f"💡 **Matching Skills:** {skills.title()}\n\n"
                            response_so_far += "---\n"
                        
                        if batch_idx < 2 and total_profiles_found > 0:
                            message_placeholder.markdown(response_so_far + "\n\n*(Waiting 3 minutes to bypass rate limits before fetching the next batch...)*")
                        else:
                            message_placeholder.markdown(response_so_far)
                    
                    if total_profiles_found > 0:
                        response_so_far += f"\n\n*All done! Found {total_profiles_found} candidates and saved them to your database. Want me to search for another role?*"
                        message_placeholder.markdown(response_so_far)
                    
                    st.session_state.messages.append({"role": "assistant", "content": response_so_far})
                    
                except Exception as e:
                    error_msg = f"Oops, something went wrong on my end! 🛑 Here's what happened: {str(e)}"
                    message_placeholder.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if st.session_state.show_right_sidebar and right_col:
    with right_col:
        
        # Header and toggle button
        r_col1, r_col2 = st.columns([8, 2])
        with r_col2:
            if st.button("›", help="Close Panel"):
                st.session_state.show_right_sidebar = False
                st.rerun()
        
        with r_col1:
            st.markdown("<h3 style='margin-top: 0; padding-top: 5px; font-size: 20px; color: #202123;'>🛂 Passport Upload & I-94</h3>", unsafe_allow_html=True)
            
        st.markdown("<p style='font-size: 14px; color: #8E8EA0; margin-bottom: 20px;'>Upload a document to extract details and verify travel history instantly.</p>", unsafe_allow_html=True)
        
        st.divider()
        
        uploaded_passport = st.file_uploader("Upload Passport/Visa", type=["png", "jpg", "jpeg", "pdf"], label_visibility="collapsed")
        
        if uploaded_passport:
            if st.session_state.get("last_processed_passport") != uploaded_passport.name:
                st.session_state.last_processed_passport = uploaded_passport.name
                with st.spinner("Extracting details via OCR..."):
                    import os
                    file_ext = os.path.splitext(uploaded_passport.name)[1].lower()
                    temp_file = f"temp_passport{file_ext}"
                    with open(temp_file, "wb") as f:
                        f.write(uploaded_passport.read())
                    
                    from ocr_extractor import extract_text_from_image, parse_passport_details
                    text = extract_text_from_image(temp_file)
                    details = parse_passport_details(text)
                    
                    if details["first_name"] != "UNKNOWN" and details["passport_number"] != "UNKNOWN":
                        st.session_state.run_i94 = {
                            "first_name": details["first_name"],
                            "last_name": details["last_name"],
                            "dob": details["dob"],
                            "passport_number": details["passport_number"],
                            "country_of_citizenship": details["country"]
                        }
                        st.success(f"Extracted: **{details['first_name']} {details['last_name']}** (Passport: {details['passport_number']})")
                    else:
                        st.error("Could not extract sufficient details from the uploaded document. Please ensure it is a clear image.")
                        st.session_state.run_i94 = None
        else:
            st.session_state.last_processed_passport = None
            st.session_state.run_i94 = None

        if st.session_state.get("run_i94"):
            req = st.session_state.run_i94
            st.markdown("---")
            st.markdown(f"**Pulling I-94 for {req['first_name']} {req['last_name']}**")
            
            result_key = f"i94_res_{req['passport_number']}"
            
            if result_key not in st.session_state:
                with st.spinner("Navigating CBP site and pulling records..."):
                    from i94_retriever import retrieve_i94_history
                    import os
                    try:
                        safe_name = req["first_name"].replace(" ", "_")
                        img_path = f"i94_{safe_name}.png"
                        asyncio.run(retrieve_i94_history(
                            req["first_name"], req["last_name"], req["dob"], 
                            req["passport_number"], req["country_of_citizenship"],
                            output_path=img_path
                        ))
                        
                        if os.path.exists(img_path):
                            st.session_state[result_key] = {"status": "success", "image": img_path}
                        else:
                            st.session_state[result_key] = {"status": "error", "msg": "Screenshot could not be generated."}
                    except Exception as e:
                        st.session_state[result_key] = {"status": "error", "msg": str(e)}

            if result_key in st.session_state:
                res = st.session_state[result_key]
                if res["status"] == "success":
                    st.success("✅ Travel history retrieved!")
                    st.image(res["image"])
                else:
                    st.error(f"❌ Failed to retrieve I-94: {res['msg']}")

        st.divider()
        st.markdown("<h3 style='margin-top: 0; padding-top: 5px; font-size: 20px; color: #202123;'>✉️ Candidate Outreach</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px; color: #8E8EA0; margin-bottom: 20px;'>Draft and send emails directly to sourced candidates.</p>", unsafe_allow_html=True)
        
        # Get candidates for email
        candidates = session.query(Candidate).all()
        if not candidates:
            st.info("No candidates saved yet. Run a search first!")
        else:
            candidate_options = {c.id: c.name for c in candidates}
            selected_cand_id = st.selectbox("Select Candidate", options=list(candidate_options.keys()), format_func=lambda x: candidate_options[x])
            selected_cand = next((c for c in candidates if c.id == selected_cand_id), None)
            
            with st.form("email_composer_form"):
                cand_email = st.text_input("Candidate's Email Address")
                
                default_subject = f"Interview Opportunity: Your experience aligns perfectly"
                
                default_body = f"Hi {selected_cand.name.split()[0] if selected_cand else ''},\n\nI came across your profile on LinkedIn and was really impressed by your background, particularly your recent experience.\n\nI'm reaching out because we are currently looking to fill a role that seems to align perfectly with your skill set. We are moving quickly with the interview process and I'd love to connect.\n\nWould you be open to a brief 10-minute chat sometime this week to discuss the opportunity in more detail?\n\nLooking forward to hearing from you!\n\nBest regards,\n[Your Name]\n[Your Company]"
                
                email_subject = st.text_input("Subject", value=default_subject)
                email_body = st.text_area("Message", value=default_body, height=200)
                
                send_pressed = st.form_submit_button("Send Email", type="primary", use_container_width=True)
                
                if send_pressed:
                    if not st.session_state.get("email_sender") or not st.session_state.get("email_password"):
                        st.error("Please configure your Email Settings in the left sidebar first.")
                    elif not cand_email:
                        st.error("Please provide the candidate's email address.")
                    else:
                        from email_sender import send_email
                        success, msg = send_email(
                            st.session_state.email_sender,
                            st.session_state.email_password,
                            cand_email,
                            email_subject,
                            email_body
                        )
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

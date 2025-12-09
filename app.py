import streamlit as st
import os
from PIL import Image
from tryon_logic import VirtualTryOnApp

# Page Config
st.set_page_config(
    page_title="Aurélie Virtual Fitting Room",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #e0e0e0;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    h1 {
        text-align: center;
        margin-bottom: 2rem;
        background: -webkit-linear-gradient(#eee, #aaa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
    }

    /* Cards/Containers */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(45deg, #e94560, #d63447);
        border: none;
        color: white;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(233, 69, 96, 0.4);
    }

    /* File Uploader */
    .stFileUploader {
        border: 2px dashed #444;
        border-radius: 12px;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.05);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(22, 33, 62, 0.95);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Application Logic
def main():
    st.title("Aurélie Virtual Fitting")
    st.markdown("<p style='text-align: center; color: #888; margin-top: -1.5em; margin-bottom: 2em;'>Premium Virtual Try-On Experience</p>", unsafe_allow_html=True)

    # Initialize App Logic
    logic = VirtualTryOnApp()

    with st.sidebar:
        st.header("Settings")
        
        # Category Selection
        category_map = {
            "Femme": "femme", 
            "Enceinte (Pregnant)": "enceinte", 
            "Homme": "homme", 
            "Enfant": "enfant", 
            "Bébé": "bebe"
        }
        selected_category_label = st.radio(
            "Target Audience", 
            list(category_map.keys()),
            index=0
        )
        selected_category = category_map[selected_category_label]
        
        # Background Selection
        # Get dynamic options based on category
        bg_options = logic.get_background_options(selected_category)
        selected_bg = st.selectbox("Atmosphere", bg_options)
        
        st.markdown("---")
        st.info("💡 **Tips:** Upload a clear photo of the garment on a hanger or flat surface for best results.")

    # Main Content
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("1. Upload Garment")
        uploaded_file = st.file_uploader("Choose a garment image...", type=['png', 'jpg', 'jpeg', 'webp'])
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.image(uploaded_file, caption="Selected Garment", use_container_width=True)
            
            # Generate Button
            if st.button("✨ Generate Look"):
                with st.spinner("Creating your virtual presentation..."):
                    # Call logic
                    output_path, error = logic.generate_tryon(
                        garment_path=temp_path, 
                        category=selected_category,
                        background_name=selected_bg
                    )
                    
                    if error:
                        st.error(error)
                    elif output_path:
                        st.session_state["last_result"] = output_path
                        # Cleanup temp
                        # os.remove(temp_path) 

    with col2:
        st.subheader("2. Result")
        if "last_result" in st.session_state and os.path.exists(st.session_state["last_result"]):
            st.image(st.session_state["last_result"], caption="Virtual Look", use_container_width=True)
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                with open(st.session_state["last_result"], "rb") as file:
                    st.download_button(
                        label="Download Image",
                        data=file,
                        file_name="tryon_result.png",
                        mime="image/png"
                    )
        else:
            # Placeholder
            st.markdown(
                """
                <div style='
                    border: 2px dashed #444; 
                    border-radius: 12px; 
                    height: 400px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    color: #666;
                    background: rgba(255,255,255,0.03);
                '>
                    p.s. Your masterpiece will appear here
                </div>
                """, 
                unsafe_allow_html=True
            )

if __name__ == "__main__":
    main()

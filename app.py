import streamlit as st
import os
import tempfile
import shutil
from ultralytics import solutions
from PIL import Image

# Create temp directories safely
def get_temp_dirs():
    if "temp_data_dir" not in st.session_state:
        try:
            st.session_state.temp_data_dir = tempfile.mkdtemp()
            st.session_state.temp_index_dir = tempfile.mkdtemp()
        except Exception:
            # Fallback to current directory if temp creation fails
            st.session_state.temp_data_dir = "temp_data"
            st.session_state.temp_index_dir = "temp_index"
            os.makedirs(st.session_state.temp_data_dir, exist_ok=True)
            os.makedirs(st.session_state.temp_index_dir, exist_ok=True)

# Initialize the searcher with temp directory
@st.cache_resource
def init_searcher():
    get_temp_dirs()
    return solutions.VisualAISearch(data=st.session_state.temp_data_dir, device="cpu")

def upload_page():
    get_temp_dirs()
    st.title("📤 SemanticLens - Upload Images")
    st.write("Upload your images to search through them")
    
    uploaded_files = st.file_uploader(
        "Choose images", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} images")
        
        if st.button("Add Images"):
            with st.spinner("Processing images..."):
                success_count = 0
                for uploaded_file in uploaded_files:
                    try:
                        # Save to temp directory
                        file_path = os.path.join(st.session_state.temp_data_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        success_count += 1
                    except Exception as e:
                        st.error(f"Error saving {uploaded_file.name}: {str(e)}")
                
                if success_count > 0:
                    st.success(f"Successfully added {success_count} images!")
                    # Clear cache to rebuild index
                    st.cache_resource.clear()
                    st.info("Images ready for search! Go to Search page.")

def search_page():
    get_temp_dirs()
    st.title("🔍 SemanticLens - Search Images")
    
    # Check if images exist
    if not os.listdir(st.session_state.temp_data_dir):
        st.warning("No images uploaded yet. Please upload images first!")
        return
    
    # Initialize searcher
    searcher = init_searcher()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "images" in message:
                cols = st.columns(2)
                for i, img_path in enumerate(message["images"][:4]):
                    with cols[i % 2]:
                        if os.path.exists(img_path):
                            image = Image.open(img_path)
                            st.image(image, caption=os.path.basename(img_path))
    
    # Chat input
    if prompt := st.chat_input("Describe what you're looking for..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get search results
        with st.chat_message("assistant"):
            with st.spinner("Searching..."):
                try:
                    results = searcher(prompt)
                    
                    if results and len(results) > 0:
                        # Get top 4 results with full paths
                        top_results = [os.path.join(st.session_state.temp_data_dir, img) for img in results[:4]]
                        
                        st.markdown(f"Found {len(results)} matching images. Here are the top 4:")
                        
                        # Display images in 2x2 grid
                        cols = st.columns(2)
                        for i, img_path in enumerate(top_results):
                            with cols[i % 2]:
                                if os.path.exists(img_path):
                                    image = Image.open(img_path)
                                    st.image(image, caption=os.path.basename(img_path))
                        
                        # Add assistant message
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"Found {len(results)} matching images. Here are the top 4:",
                            "images": top_results
                        })
                    else:
                        st.markdown("No matching images found. Try a different search term.")
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "No matching images found. Try a different search term."
                        })
                        
                except Exception as e:
                    st.error(f"Error during search: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"Sorry, there was an error: {str(e)}"
                    })

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Upload Images", "Search Images"])
    
    if page == "Upload Images":
        upload_page()
    elif page == "Search Images":
        search_page()

if __name__ == "__main__":
    main()

import streamlit as st
import os
import tempfile
from ultralytics import solutions
from PIL import Image

# Initialize the searcher with temp directory
@st.cache_resource
def init_searcher():
    if "temp_data_dir" not in st.session_state:
        try:
            st.session_state.temp_data_dir = tempfile.mkdtemp()
        except Exception:
            st.session_state.temp_data_dir = "temp_data"
            os.makedirs(st.session_state.temp_data_dir, exist_ok=True)
    
    return solutions.VisualAISearch(data=st.session_state.temp_data_dir, device="cpu")

def main():
    st.title("🔍 SemanticLens")
    
    # Initialize temp directory only when needed
    if "temp_data_dir" not in st.session_state:
        try:
            st.session_state.temp_data_dir = tempfile.mkdtemp()
        except Exception:
            st.session_state.temp_data_dir = "temp_data"
            os.makedirs(st.session_state.temp_data_dir, exist_ok=True)
    
    # Upload section
    st.subheader("📤 Upload Images")
    uploaded_files = st.file_uploader(
        "Choose images to search through", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Add Images"):
            with st.spinner("Processing images..."):
                # Clear existing index files
                for file in ["faiss.index", "paths.npy"]:
                    if os.path.exists(file):
                        os.remove(file)
                
                success_count = 0
                for uploaded_file in uploaded_files:
                    try:
                        file_path = os.path.join(st.session_state.temp_data_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        success_count += 1
                    except Exception as e:
                        st.error(f"Error saving {uploaded_file.name}: {str(e)}")
                
                if success_count > 0:
                    st.success(f"Successfully added {success_count} images!")
                    st.cache_resource.clear()
    
    # Chat section
    try:
        if os.path.exists(st.session_state.temp_data_dir) and os.listdir(st.session_state.temp_data_dir):
            st.subheader("💬 Search Images")
            
            searcher = init_searcher()
            
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
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("Searching..."):
                        try:
                            results = searcher(prompt)
                            
                            if results and len(results) > 0:
                                top_results = [os.path.join(st.session_state.temp_data_dir, img) for img in results[:4]]
                                
                                st.markdown(f"Found {len(results)} matching images. Here are the top 4:")
                                
                                cols = st.columns(2)
                                for i, img_path in enumerate(top_results):
                                    with cols[i % 2]:
                                        if os.path.exists(img_path):
                                            image = Image.open(img_path)
                                            st.image(image, caption=os.path.basename(img_path))
                                
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
        else:
            st.info("👆 Upload some images above to start searching!")
    except Exception:
        st.info("👆 Upload some images above to start searching!")

if __name__ == "__main__":
    main()

# SemanticLens 🔍

A semantic image search engine built with Streamlit and Ultralytics, powered by OpenAI's CLIP and Meta's FAISS for intelligent visual content discovery.

![CLIP Multimodal Architecture](sample/CLIP%20Multimodal.png)

## Features

- **Upload & Search**: Upload your own images and search through them using natural language
- **Semantic Understanding**: Powered by CLIP for deep visual-text understanding
- **Real-time Results**: Get top 4 matching images instantly
- **Temporary Storage**: Runtime-only storage - everything resets on page refresh
- **Interactive Chat**: Chatbot-style interface for intuitive searching

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Devparihar5/SemanticLens.git
   cd SemanticLens
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## How to Use

1. **Upload Images**: Start by uploading multiple images (PNG, JPG, JPEG)
2. **Search**: Use natural language to describe what you're looking for
3. **Results**: View the top 4 matching images in a clean grid layout

## Example Searches

- "blue sky with clouds"
- "person walking"
- "red car"
- "sunset landscape"
- "cat sitting"

## Technology Stack

- **Frontend**: Streamlit
- **AI Model**: Ultralytics (CLIP implementation)
- **Vector Search**: FAISS
- **Image Processing**: PIL/Pillow

## Architecture

The application uses a three-phase approach:
1. **Upload Phase**: Images stored in temporary directory
2. **Indexing Phase**: CLIP embeddings generated and FAISS index built
3. **Search Phase**: Natural language queries matched against image embeddings
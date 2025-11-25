import streamlit as st
import json
import tempfile
import os
from typing import Dict, Any, List, Optional
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
import io
import base64
from auth import is_authenticated, show_auth_dialog, show_user_profile_sidebar
# Import unstructured components
try:
    from unstructured.partition.auto import partition
    from unstructured.partition.pdf import partition_pdf
    from unstructured.partition.docx import partition_docx
    from unstructured.partition.html import partition_html
    from unstructured.partition.pptx import partition_pptx
    from unstructured.partition.xlsx import partition_xlsx
    from unstructured.staging.base import dict_to_elements, elements_to_json
    from unstructured.documents.elements import Element, Text, Title, NarrativeText, Table, Image
    from unstructured.chunking.title import chunk_by_title
    from unstructured.chunking.basic import chunk_elements
    from unstructured.cleaners.core import clean_extra_whitespace, clean_non_ascii_chars, clean_bullets
    from unstructured.embed.openai import OpenAIEmbeddingEncoder
    from unstructured.staging.base import convert_to_isd
    from unstructured.staging.huggingface import stage_for_transformers
except ImportError as e:
    st.error(f"Unstructured library not found. Please install it: pip install unstructured[all]")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Advanced Document Processing Suite",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.2rem;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    .card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
        margin: 1rem 0;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .upload-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 3px dashed #007bff;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-card:hover {
        border-color: #0056b3;
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .processing-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .result-viewer {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 15px;
        padding: 1.5rem;
        max-height: 600px;
        overflow-y: auto;
        font-family: 'Monaco', 'Consolas', monospace;
    }
    
    .element-card {
        background: white;
        border-left: 4px solid #007bff;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .element-title {
        font-weight: 600;
        color: #007bff;
        margin-bottom: 0.5rem;
    }
    
    .element-text {
        color: #495057;
        line-height: 1.6;
    }
    
    .element-meta {
        font-size: 0.8rem;
        color: #6c757d;
        margin-top: 0.5rem;
        font-style: italic;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    .success-animation {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .sidebar .stSelectbox > div > div {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
    }
    
    .json-viewer {
        background: #2d3748;
        color: #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        font-family: 'Monaco', monospace;
        font-size: 0.9rem;
        max-height: 500px;
        overflow-y: auto;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'processed_elements' not in st.session_state:
        st.session_state.processed_elements = None
    if 'schema_fields' not in st.session_state:
        st.session_state.schema_fields = []
    if 'final_json' not in st.session_state:
        st.session_state.final_json = None
    if 'processing_history' not in st.session_state:
        st.session_state.processing_history = []
    if 'current_file_info' not in st.session_state:
        st.session_state.current_file_info = {}

def add_schema_field():
    """Add a new schema field"""
    st.session_state.schema_fields.append({
        'field_name': '',
        'field_type': 'string',
        'description': '',
        'required': False
    })

def remove_schema_field(index):
    """Remove a schema field"""
    if 0 <= index < len(st.session_state.schema_fields):
        st.session_state.schema_fields.pop(index)

def get_partition_function(file_type: str):
    """Get the appropriate partition function based on file type"""
    partition_map = {
        'pdf': partition_pdf,
        'docx': partition_docx,
        'html': partition_html,
        'pptx': partition_pptx,
        'xlsx': partition_xlsx
    }
    return partition_map.get(file_type, partition)

def process_document(uploaded_file, processing_options):
    """Enhanced document processing with poppler-free PDF handling"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_file_path = tmp_file.name

        file_type = uploaded_file.name.split('.')[-1].lower()
        
        # Special handling for PDF files without poppler
        if file_type == 'pdf':
            try:
                # Try using PyPDF for basic text extraction
                import PyPDF2
                
                # First attempt: Use unstructured with basic strategy
                elements = partition(
                    filename=tmp_file_path,
                    strategy='fast',  # Use fast strategy to avoid poppler
                    include_page_breaks=processing_options.get('include_page_breaks', True),
                )
                
            except Exception as pdf_error:
                st.warning(f"Advanced PDF processing failed: {str(pdf_error)}")
                st.info("🔄 Falling back to basic PDF text extraction...")
                
                try:
                    # Fallback: Manual PDF text extraction using PyPDF2
                    import PyPDF2
                    from unstructured.documents.elements import Text, Title
                    
                    with open(tmp_file_path, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        elements = []
                        
                        for page_num, page in enumerate(pdf_reader.pages, 1):
                            try:
                                text = page.extract_text()
                                if text.strip():
                                    # Split text into paragraphs
                                    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                                    
                                    for para in paragraphs:
                                        # Simple heuristic: if paragraph is short and capitalized, treat as title
                                        if len(para) < 100 and para.isupper():
                                            element = Title(text=para)
                                        else:
                                            element = Text(text=para)
                                        
                                        # Add metadata
                                        element.metadata.page_number = page_num
                                        element.metadata.filename = uploaded_file.name
                                        elements.append(element)
                                        
                            except Exception as page_error:
                                st.warning(f"Error processing page {page_num}: {str(page_error)}")
                                continue
                    
                    if not elements:
                        st.error("Could not extract any text from PDF")
                        return None
                        
                    st.success(f"✅ Successfully extracted text from {len(pdf_reader.pages)} pages using basic method")
                    
                except ImportError:
                    st.error("PyPDF2 not installed. Installing now...")
                    try:
                        import subprocess
                        import sys
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
                        st.success("PyPDF2 installed! Please refresh the page and try again.")
                        return None
                    except Exception as install_error:
                        st.error(f"Failed to install PyPDF2: {str(install_error)}")
                        return None
                        
                except Exception as fallback_error:
                    st.error(f"All PDF processing methods failed: {str(fallback_error)}")
                    st.markdown("""
                    ### 💡 Alternative Solutions:
                    1. **Convert PDF to text first**: Use online tools to convert PDF to TXT
                    2. **Use different file format**: Try DOCX or HTML instead
                    3. **Install poppler**: Follow the installation guide for full PDF support
                    """)
                    return None
        else:
            # Non-PDF files - use original logic
            partition_func = get_partition_function(file_type)
            
            # Build partition arguments
            partition_args = {
                'filename': tmp_file_path,
                'strategy': processing_options.get('strategy', 'auto'),
                'include_page_breaks': processing_options.get('include_page_breaks', True),
                'infer_table_structure': processing_options.get('infer_table_structure', True),
            }
            
            # Add specific options based on strategy
            if processing_options.get('strategy') == 'hi_res':
                partition_args['hi_res'] = True
            elif processing_options.get('strategy') == 'ocr_only':
                partition_args['ocr_languages'] = ['eng']
            
            # Add coordinates extraction if requested
            if processing_options.get('extract_coordinates', False):
                partition_args['coordinates'] = True
            
            # Process with unstructured
            elements = partition_func(**partition_args)
        
        # Apply advanced cleaning (common for all file types)
        cleaned_elements = []
        for element in elements:
            if hasattr(element, 'text') and element.text:
                # Basic cleaning
                if processing_options.get('clean_text', False):
                    element.text = clean_extra_whitespace(element.text)
                
                if processing_options.get('clean_non_ascii', False):
                    element.text = clean_non_ascii_chars(element.text)
                
                if processing_options.get('clean_bullets', False):
                    element.text = clean_bullets(element.text)
                
                # Filter by minimum text length
                min_length = processing_options.get('min_text_length', 0)
                if len(element.text.strip()) >= min_length:
                    cleaned_elements.append(element)
            else:
                cleaned_elements.append(element)
        
        elements = cleaned_elements
        
        # Apply chunking strategies
        if processing_options.get('chunking_strategy') == 'by_title':
            elements = chunk_by_title(
                elements,
                max_characters=processing_options.get('max_chunk_size', 1000),
                new_after_n_chars=processing_options.get('new_after_chars', 800),
                combine_text_under_n_chars=processing_options.get('combine_under_chars', 200)
            )
        elif processing_options.get('chunking_strategy') == 'basic':
            elements = chunk_elements(
                elements,
                max_characters=processing_options.get('max_chunk_size', 1000)
            )
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return elements

    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        
        # Show helpful error message for PDF files
        if uploaded_file.name.lower().endswith('.pdf'):
            st.markdown("""
            ### 🔧 PDF Processing Tips:
            
            **Option 1: Use Basic PDF Processing**
            ```bash
            pip install PyPDF2
            ```
            Then refresh and try again.
            
            **Option 2: Convert Your PDF**
            - Convert PDF to DOCX using online tools
            - Save PDF as text file
            - Use Google Docs to convert PDF to text
            
            **Option 3: Install Poppler (Advanced)**
            ```bash
            sudo apt install -y poppler-utils
            ```
            """)
        
        return None

def apply_custom_schema(elements, schema_fields):
    """Enhanced schema application with more field types"""
    try:
        element_dicts = [element.to_dict() for element in elements]
        
        schema_output = {
            "metadata": {
                "total_elements": len(element_dicts),
                "schema_version": "2.0",
                "processing_timestamp": pd.Timestamp.now().isoformat(),
                "element_types": {}
            },
            "schema": {
                field['field_name']: {
                    "type": field['field_type'],
                    "description": field['description'],
                    "required": field['required']
                } for field in schema_fields if field['field_name']
            },
            "content": []
        }
        
        # Calculate element type distribution
        element_types = {}
        for element_dict in element_dicts:
            elem_type = element_dict.get("type", "unknown")
            element_types[elem_type] = element_types.get(elem_type, 0) + 1
        
        schema_output["metadata"]["element_types"] = element_types
        
        # Process each element according to schema
        for idx, element_dict in enumerate(element_dicts):
            processed_element = {
                "element_id": element_dict.get("element_id", f"elem_{idx}"),
                "type": element_dict.get("type", ""),
                "text": element_dict.get("text", ""),
                "metadata": element_dict.get("metadata", {})
            }
            
            # Apply custom schema fields
            for field in schema_fields:
                if field['field_name']:
                    field_type = field['field_type']
                    
                    if field_type == 'extracted_text':
                        processed_element[field['field_name']] = element_dict.get("text", "")
                    elif field_type == 'element_type':
                        processed_element[field['field_name']] = element_dict.get("type", "")
                    elif field_type == 'page_number':
                        processed_element[field['field_name']] = element_dict.get("metadata", {}).get("page_number", None)
                    elif field_type == 'coordinates':
                        processed_element[field['field_name']] = element_dict.get("metadata", {}).get("coordinates", None)
                    elif field_type == 'text_length':
                        processed_element[field['field_name']] = len(element_dict.get("text", ""))
                    elif field_type == 'word_count':
                        processed_element[field['field_name']] = len(element_dict.get("text", "").split())
                    elif field_type == 'parent_id':
                        processed_element[field['field_name']] = element_dict.get("metadata", {}).get("parent_id", None)
                    elif field_type == 'filename':
                        processed_element[field['field_name']] = element_dict.get("metadata", {}).get("filename", None)
                    elif field_type == 'custom':
                        processed_element[field['field_name']] = f"Custom field: {field['description']}"
            
            schema_output["content"].append(processed_element)
        
        return schema_output

    except Exception as e:
        st.error(f"Error applying schema: {str(e)}")
        return None

def render_json_viewer(json_data):
    """Render an interactive JSON viewer"""
    json_str = json.dumps(json_data, indent=2)
    
    # Color-coded JSON display
    st.markdown(f"""
    <div class="json-viewer">
        <pre><code>{json_str}</code></pre>
    </div>
    """, unsafe_allow_html=True)

def render_element_cards(elements):
    """Render elements as interactive cards"""
    for idx, element in enumerate(elements):
        element_dict = element.to_dict() if hasattr(element, 'to_dict') else element
        
        element_type = element_dict.get('type', 'Unknown')
        text = element_dict.get('text', '')[:500] + ('...' if len(element_dict.get('text', '')) > 500 else '')
        metadata = element_dict.get('metadata', {})
        
        # Color coding by element type
        color_map = {
            'Title': '#007bff',
            'NarrativeText': '#28a745',
            'Table': '#ffc107',
            'Image': '#dc3545',
            'ListItem': '#6f42c1',
            'Header': '#fd7e14',
            'Footer': '#20c997'
        }
        
        border_color = color_map.get(element_type, '#6c757d')
        
        st.markdown(f"""
        <div class="element-card" style="border-left-color: {border_color};">
            <div class="element-title">
                {element_type} #{idx + 1}
            </div>
            <div class="element-text">
                {text}
            </div>
            <div class="element-meta">
                Page: {metadata.get('page_number', 'N/A')} | 
                Characters: {len(element_dict.get('text', ''))} |
                ID: {element_dict.get('element_id', 'N/A')}
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_analytics_dashboard(json_data):
    """Create comprehensive analytics dashboard"""
    if not json_data or 'content' not in json_data:
        st.warning("No data available for analytics")
        return
    
    content = json_data['content']
    
    # Element type distribution pie chart
    if 'element_types' in json_data.get('metadata', {}):
        element_types = json_data['metadata']['element_types']
        
        fig_pie = px.pie(
            values=list(element_types.values()),
            names=list(element_types.keys()),
            title="Element Type Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(
            showlegend=True,
            height=400,
            font=dict(size=14)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Text length distribution
    text_lengths = [len(item.get('text', '')) for item in content]
    if text_lengths:
        fig_hist = px.histogram(
            x=text_lengths,
            title="Text Length Distribution",
            labels={'x': 'Text Length (characters)', 'y': 'Frequency'},
            color_discrete_sequence=['#667eea']
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # Page-wise element count (if available)
    page_data = {}
    for item in content:
        page = item.get('metadata', {}).get('page_number', 'Unknown')
        if page != 'Unknown' and page is not None:
            page_data[page] = page_data.get(page, 0) + 1
    
    if page_data:
        pages = sorted(page_data.keys())
        counts = [page_data[p] for p in pages]
        
        fig_bar = px.bar(
            x=pages,
            y=counts,
            title="Elements per Page",
            labels={'x': 'Page Number', 'y': 'Element Count'},
            color=counts,
            color_continuous_scale='viridis'
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

def main():
    initialize_session_state()
    
    # Header with gradient
    st.markdown('<h1 class="main-header">🚀 Advanced Document Processing Suite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Powered by Atlas.ai - Transform any document into structured data</p>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Processing Configuration")
        
        # Processing strategy
        processing_strategy = st.selectbox(
            "🎯 Processing Strategy",
            ["auto", "hi_res", "fast", "ocr_only"],
            help="Auto: Best strategy selection\nHi-res: Maximum accuracy\nFast: Quick processing\nOCR-only: Force OCR"
        )
        
        # Advanced options
        st.markdown("#### 🔧 Advanced Options")
        hi_res_mode = st.checkbox("🔍 High Resolution Mode", value=False)
        include_page_breaks = st.checkbox("📄 Include Page Breaks", value=True)
        infer_table_structure = st.checkbox("📊 Infer Table Structure", value=True)
        extract_coordinates = st.checkbox("📍 Extract Coordinates", value=False)
        extract_images = st.checkbox("🖼️ Extract Images (PDF)", value=False)
        
        # Text processing
        st.markdown("#### 📝 Text Processing")
        clean_text = st.checkbox("🧹 Clean Extra Whitespace", value=True)
        clean_non_ascii = st.checkbox("🔤 Clean Non-ASCII Characters", value=False)
        clean_bullets = st.checkbox("🔗 Clean Bullet Points", value=False)
        min_text_length = st.number_input("📏 Minimum Text Length", min_value=0, value=10)
        
        # Chunking options
        st.markdown("#### ✂️ Chunking Options")
        chunking_strategy = st.selectbox(
            "Chunking Strategy",
            ["none", "by_title", "basic"],
            help="None: No chunking\nBy Title: Chunk by document titles\nBasic: Simple character-based chunking"
        )
        
        if chunking_strategy != "none":
            max_chunk_size = st.slider("Max Chunk Size", 100, 5000, 1000)
            new_after_chars = st.slider("New Chunk After", 100, 2000, 800)
            combine_under_chars = st.slider("Combine Under", 50, 500, 200)
        else:
            max_chunk_size = new_after_chars = combine_under_chars = 0
    
    # Processing options dictionary
    processing_options = {
        'strategy': processing_strategy,
        'hi_res': hi_res_mode,
        'include_page_breaks': include_page_breaks,
        'infer_table_structure': infer_table_structure,
        'extract_coordinates': extract_coordinates,
        'extract_images': extract_images,
        'clean_text': clean_text,
        'clean_non_ascii': clean_non_ascii,
        'clean_bullets': clean_bullets,
        'min_text_length': min_text_length,
        'chunking_strategy': chunking_strategy if chunking_strategy != "none" else None,
        'max_chunk_size': max_chunk_size,
        'new_after_chars': new_after_chars,
        'combine_under_chars': combine_under_chars
    }
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Upload & Process", 
        "📋 Schema Designer", 
        "📊 Results Viewer", 
        "📈 Analytics", 
        "📁 History"
    ])
    
    with tab1:
        st.markdown("### 📤 Document Upload & Processing")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="upload-card">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Drop your document here or click to browse",
                type=['pdf', 'docx', 'txt', 'html', 'xml', 'pptx', 'xlsx', 'csv', 'md', 'rtf', 'odt'],
                help="Supported: PDF, DOCX, TXT, HTML, XML, PPTX, XLSX, CSV, MD, RTF, ODT"
            )
            
            if uploaded_file:
                st.success("✅ File uploaded successfully!")
                file_info = {
                    'name': uploaded_file.name,
                    'size': f"{uploaded_file.size / 1024:.2f} KB",
                    'type': uploaded_file.name.split('.')[-1].upper()
                }
                st.session_state.current_file_info = file_info
                
                # Display file info
                st.info(f"📁 **{file_info['name']}** | 📊 {file_info['size']} | 📋 {file_info['type']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🎯 Quick Stats")
            if st.session_state.final_json:
                total_elements = st.session_state.final_json.get('metadata', {}).get('total_elements', 0)
                st.markdown(f"""
                <div class="metric-card">
                    <h2>{total_elements}</h2>
                    <p>Elements Processed</p>
                </div>
                """, unsafe_allow_html=True)
            
            if st.session_state.current_file_info:
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <h3>{st.session_state.current_file_info.get('type', 'N/A')}</h3>
                    <p>File Format</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Processing button and progress
        if uploaded_file:
            st.markdown("---")
            
            col_process, col_info = st.columns([1, 2])
            
            with col_process:
                if st.button("🚀 Process Document", type="primary", use_container_width=True):
                    with st.spinner("🔄 Processing your document..."):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Simulate processing steps
                        steps = [
                            "📄 Reading document...",
                            "🔍 Analyzing structure...",
                            "📝 Extracting text...",
                            "🏗️ Building elements...",
                            "✨ Applying enhancements...",
                            "✅ Finalizing results..."
                        ]
                        
                        for i, step in enumerate(steps):
                            status_text.text(step)
                            progress_bar.progress((i + 1) / len(steps))
                            time.sleep(0.5)
                        
                        elements = process_document(uploaded_file, processing_options)
                        
                        if elements:
                            st.session_state.processed_elements = elements
                            
                            # Add to history
                            st.session_state.processing_history.append({
                                'filename': uploaded_file.name,
                                'timestamp': datetime.now().isoformat(),
                                'elements_count': len(elements),
                                'strategy': processing_options['strategy']
                            })
                            
                            # Apply schema or create standard output
                            if st.session_state.schema_fields:
                                schema_output = apply_custom_schema(elements, st.session_state.schema_fields)
                                if schema_output:
                                    st.session_state.final_json = schema_output
                            else:
                                standard_output = {
                                    "metadata": {
                                        "total_elements": len(elements),
                                        "processing_timestamp": pd.Timestamp.now().isoformat(),
                                        "filename": uploaded_file.name,
                                        "processing_options": processing_options
                                    },
                                    "elements": [element.to_dict() for element in elements]
                                }
                                st.session_state.final_json = standard_output
                            
                            st.success("🎉 Document processed successfully!")
                            st.balloons()
            
            with col_info:
                st.markdown("### 📋 Processing Options Summary")
                st.json({
                    "strategy": processing_options['strategy'],
                    "advanced_features": [k for k, v in processing_options.items() if v is True],
                    "chunking": processing_options.get('chunking_strategy', 'none')
                })
    
    with tab2:
        st.markdown("### 📋 Custom Schema Designer")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 🎨 Build Your Schema")
            
            col_add, col_clear, col_preset = st.columns([1, 1, 1])
            
            with col_add:
                if st.button("➕ Add Field", use_container_width=True):
                    add_schema_field()
            
            with col_clear:
                if st.button("🗑️ Clear All", use_container_width=True):
                    st.session_state.schema_fields = []
            
            with col_preset:
                if st.button("🎯 Load Preset", use_container_width=True):
                    # Load a preset schema
                    st.session_state.schema_fields = [
                        {'field_name': 'title', 'field_type': 'extracted_text', 'description': 'Document title', 'required': True},
                        {'field_name': 'content', 'field_type': 'extracted_text', 'description': 'Main content', 'required': True},
                        {'field_name': 'page', 'field_type': 'page_number', 'description': 'Page number', 'required': False},
                        {'field_name': 'element_type', 'field_type': 'element_type', 'description': 'Type of element', 'required': False}
                    ]
            
            # Schema field definitions
            for i, field in enumerate(st.session_state.schema_fields):
                with st.expander(f"🔧 Field {i+1}: {field.get('field_name', 'New Field')}", expanded=True):
                    col_name, col_type = st.columns([2, 1])
                    
                    with col_name:
                        field['field_name'] = st.text_input(
                            "Field Name",
                            value=field.get('field_name', ''),
                            key=f"field_name_{i}",
                            placeholder="e.g., document_title"
                        )
                    
                    with col_type:
                        field['field_type'] = st.selectbox(
                            "Type",
                            [
                                "string", "extracted_text", "element_type", "page_number", 
                                "coordinates", "text_length", "word_count", "parent_id", 
                                "filename", "custom"
                            ],
                            index=[
                                "string", "extracted_text", "element_type", "page_number", 
                                "coordinates", "text_length", "word_count", "parent_id", 
                                "filename", "custom"
                            ].index(field.get('field_type', 'string')),
                            key=f"field_type_{i}"
                        )
                    
                    field['description'] = st.text_area(
                        "Description",
                        value=field.get('description', ''),
                        key=f"field_desc_{i}",
                        height=60,
                        placeholder="Describe this field's purpose..."
                    )
                    
                    col_req, col_remove = st.columns([1, 1])
                    with col_req:
                        field['required'] = st.checkbox(
                            "Required Field",
                            value=field.get('required', False),
                            key=f"field_req_{i}"
                        )
                    
                    with col_remove:
                        if st.button(f"🗑️ Remove", key=f"remove_{i}", type="secondary"):
                            remove_schema_field(i)
                            st.rerun()
        
        with col2:
            st.markdown("#### 📖 Field Type Guide")
            
            field_guide = {
                "🔤 string": "Generic text field",
                "📝 extracted_text": "Raw extracted text content",
                "🏷️ element_type": "Type of document element (Title, Text, etc.)",
                "📄 page_number": "Page number where element appears",
                "📍 coordinates": "Position coordinates in document",
                "📏 text_length": "Character count of text",
                "🔢 word_count": "Number of words in text",
                "🔗 parent_id": "ID of parent element",
                "📁 filename": "Original document filename",
                "⚙️ custom": "User-defined custom field"
            }
            
            for field_type, description in field_guide.items():
                st.markdown(f"**{field_type}**: {description}")
            
            if st.session_state.schema_fields:
                st.markdown("#### 🎯 Current Schema Preview")
                schema_preview = {
                    field['field_name']: field['field_type'] 
                    for field in st.session_state.schema_fields 
                    if field['field_name']
                }
                st.json(schema_preview)
    
    with tab3:
        st.markdown("### 📊 Results Viewer")
        
        if st.session_state.final_json:
            # Results overview
            col1, col2, col3, col4 = st.columns(4)
            
            metadata = st.session_state.final_json.get('metadata', {})
            
            with col1:
                total_elements = metadata.get('total_elements', 0)
                st.metric("📊 Total Elements", total_elements)
            
            with col2:
                processing_time = metadata.get('processing_timestamp', 'N/A')
                if processing_time != 'N/A':
                    time_str = processing_time.split('T')[1][:8]
                    st.metric("⏱️ Processed At", time_str)
                else:
                    st.metric("⏱️ Processed At", "N/A")
            
            with col3:
                filename = metadata.get('filename', st.session_state.current_file_info.get('name', 'N/A'))
                st.metric("📁 Document", filename[:15] + "..." if len(filename) > 15 else filename)
            
            with col4:
                schema_version = metadata.get('schema_version', '1.0')
                st.metric("🏷️ Schema Ver.", schema_version)
            
            st.markdown("---")
            
            # View options
            view_col1, view_col2, view_col3 = st.columns([1, 1, 1])
            
            with view_col1:
                view_mode = st.selectbox(
                    "👁️ View Mode",
                    ["Element Cards", "JSON Viewer", "Table View", "Raw Data"]
                )
            
            with view_col2:
                if 'content' in st.session_state.final_json:
                    max_elements = len(st.session_state.final_json['content'])
                    if max_elements > 1:
                        elements_to_show = st.slider(
                            "Elements to Display", 
                            1, min(max_elements, 100), 
                            min(10, max_elements)
                        )
                    else:
                        elements_to_show = max_elements
                        st.info(f"Showing {max_elements} element(s)")
                else:
                    elements_to_show = 10
            
            with view_col3:
                if st.session_state.processed_elements:
                    element_filter = st.selectbox(
                        "🔍 Filter by Type",
                        ["All"] + list(set([elem.to_dict().get('type', 'Unknown') for elem in st.session_state.processed_elements]))
                    )
                else:
                    element_filter = "All"
            
            st.markdown("---")
            
            # Display based on view mode
            if view_mode == "Element Cards":
                st.markdown("#### 🎴 Element Cards View")
                
                if st.session_state.processed_elements:
                    filtered_elements = st.session_state.processed_elements
                    if element_filter != "All":
                        filtered_elements = [
                            elem for elem in st.session_state.processed_elements 
                            if elem.to_dict().get('type', 'Unknown') == element_filter
                        ]
                    
                    elements_subset = filtered_elements[:elements_to_show]
                    render_element_cards(elements_subset)
                else:
                    st.info("No processed elements available")
            
            elif view_mode == "JSON Viewer":
                st.markdown("#### 🔍 JSON Viewer")
                
                # Limit JSON for display
                display_json = st.session_state.final_json.copy()
                if 'content' in display_json:
                    display_json['content'] = display_json['content'][:elements_to_show]
                
                render_json_viewer(display_json)
            
            elif view_mode == "Table View":
                st.markdown("#### 📋 Table View")
                
                if 'content' in st.session_state.final_json:
                    try:
                        df = pd.json_normalize(st.session_state.final_json['content'][:elements_to_show])
                        
                        # Clean up column names
                        df.columns = [col.replace('metadata.', '').replace('_', ' ').title() for col in df.columns]
                        
                        # Display with filtering options
                        st.dataframe(
                            df,
                            use_container_width=True,
                            height=600,
                            column_config={
                                "Text": st.column_config.TextColumn(
                                    "Text Content",
                                    width="large",
                                    help="Extracted text content"
                                )
                            }
                        )
                        
                        # Quick stats
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        with col_stat1:
                            st.metric("Rows", len(df))
                        with col_stat2:
                            st.metric("Columns", len(df.columns))
                        with col_stat3:
                            avg_text_len = df['Text'].str.len().mean() if 'Text' in df.columns else 0
                            st.metric("Avg Text Length", f"{avg_text_len:.0f}")
                        
                    except Exception as e:
                        st.error(f"Error creating table view: {str(e)}")
                        st.json(st.session_state.final_json['content'][:5])
                else:
                    st.warning("No content available for table view")
            
            elif view_mode == "Raw Data":
                st.markdown("#### 🗂️ Raw Data View")
                st.json(st.session_state.final_json)
            
            # Download section
            st.markdown("---")
            st.markdown("### 💾 Download Options")
            
            col_down1, col_down2, col_down3 = st.columns(3)
            
            with col_down1:
                # JSON Download
                json_str = json.dumps(st.session_state.final_json, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name=f"processed_{st.session_state.current_file_info.get('name', 'document').split('.')[0]}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col_down2:
                # CSV Download
                if 'content' in st.session_state.final_json:
                    try:
                        df_export = pd.json_normalize(st.session_state.final_json['content'])
                        csv_str = df_export.to_csv(index=False)
                        st.download_button(
                            label="📊 Download CSV",
                            data=csv_str,
                            file_name=f"processed_{st.session_state.current_file_info.get('name', 'document').split('.')[0]}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.button("📊 CSV Not Available", disabled=True, use_container_width=True)
            
            with col_down3:
                # Excel Download
                if 'content' in st.session_state.final_json:
                    try:
                        df_export = pd.json_normalize(st.session_state.final_json['content'])
                        
                        # Create Excel file in memory
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df_export.to_excel(writer, sheet_name='Processed_Data', index=False)
                            
                            # Add metadata sheet
                            metadata_df = pd.DataFrame([st.session_state.final_json['metadata']])
                            metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                        
                        st.download_button(
                            label="📈 Download Excel",
                            data=output.getvalue(),
                            file_name=f"processed_{st.session_state.current_file_info.get('name', 'document').split('.')[0]}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.button("📈 Excel Not Available", disabled=True, use_container_width=True)
        
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin: 2rem 0;">
                <h3>📄 No Results Yet</h3>
                <p>Upload and process a document to see results here!</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 📈 Analytics Dashboard")
        
        if st.session_state.final_json:
            create_analytics_dashboard(st.session_state.final_json)
            
            # Additional analytics
            if 'content' in st.session_state.final_json:
                st.markdown("---")
                st.markdown("#### 🔍 Advanced Analytics")
                
                content = st.session_state.final_json['content']
                
                # Text statistics
                col_stats1, col_stats2 = st.columns(2)
                
                with col_stats1:
                    st.markdown("##### 📊 Text Statistics")
                    
                    texts = [item.get('text', '') for item in content]
                    text_stats = {
                        'Total Characters': sum(len(text) for text in texts),
                        'Total Words': sum(len(text.split()) for text in texts),
                        'Average Words per Element': sum(len(text.split()) for text in texts) / len(texts) if texts else 0,
                        'Longest Text': max(len(text) for text in texts) if texts else 0,
                        'Shortest Text': min(len(text) for text in texts if text) if texts else 0
                    }
                    
                    for stat, value in text_stats.items():
                        if isinstance(value, float):
                            st.metric(stat, f"{value:.1f}")
                        else:
                            st.metric(stat, f"{value:,}")
                
                with col_stats2:
                    st.markdown("##### 🏷️ Element Analysis")
                    
                    # Element type analysis
                    element_types = {}
                    for item in content:
                        elem_type = item.get('type', 'Unknown')
                        element_types[elem_type] = element_types.get(elem_type, 0) + 1
                    
                    # Create a more detailed breakdown
                    for elem_type, count in sorted(element_types.items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / len(content)) * 100
                        st.metric(f"{elem_type}", f"{count} ({percentage:.1f}%)")
                
                # Word cloud or frequency analysis could go here
                st.markdown("##### 🔤 Common Terms Analysis")
                
                # Simple word frequency (you could enhance this with nltk or spacy)
                all_text = " ".join([item.get('text', '') for item in content]).lower()
                words = all_text.split()
                
                if len(words) > 0:  # Check if we have any words
                    word_freq = {}
                    
                    # Filter common words
                    stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'a', 'an', 'this', 'that', 'these', 'those'}
                    
                    for word in words:
                        cleaned_word = ''.join(c for c in word if c.isalnum())
                        if len(cleaned_word) > 3 and cleaned_word not in stop_words:
                            word_freq[cleaned_word] = word_freq.get(cleaned_word, 0) + 1
                    
                    if word_freq and len(word_freq) > 0:
                        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
                        
                        if top_words and len(top_words) > 0:
                            words_df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
                            
                            fig_words = px.bar(
                                words_df,
                                x='Frequency',
                                y='Word',
                                orientation='h',
                                title="Top 20 Most Frequent Words",
                                color='Frequency',
                                color_continuous_scale='viridis'
                            )
                            fig_words.update_layout(height=600, yaxis={'categoryorder':'total ascending'})
                            st.plotly_chart(fig_words, use_container_width=True)
                        else:
                            st.info("No significant words found for analysis.")
                    else:
                        st.info("No words found after filtering stop words.")
                else:
                    st.info("No text content available for word frequency analysis.")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin: 2rem 0;">
                <h3>📊 No Analytics Available</h3>
                <p>Process a document first to see detailed analytics!</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### 📁 Processing History")
        
        if st.session_state.processing_history:
            st.markdown("#### 🕒 Recent Processing Sessions")
            
            # Convert history to DataFrame for better display
            history_df = pd.DataFrame(st.session_state.processing_history)
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Display as cards
            for idx, session in enumerate(reversed(st.session_state.processing_history)):
                with st.expander(f"📄 {session['filename']} - {session['timestamp'][:19]}", expanded=idx==0):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📊 Elements", session['elements_count'])
                    with col2:
                        st.metric("🎯 Strategy", session['strategy'])
                    with col3:
                        st.metric("📅 Date", session['timestamp'][:10])
                    
                    st.markdown(f"**File:** {session['filename']}")
                    st.markdown(f"**Processing Strategy:** {session['strategy']}")
                    st.markdown(f"**Elements Found:** {session['elements_count']}")
            
            # Summary statistics
            st.markdown("---")
            st.markdown("#### 📊 History Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sessions", len(st.session_state.processing_history))
            
            with col2:
                total_elements = sum(s['elements_count'] for s in st.session_state.processing_history)
                st.metric("Total Elements", total_elements)
            
            with col3:
                strategies = [s['strategy'] for s in st.session_state.processing_history]
                most_used = max(set(strategies), key=strategies.count) if strategies else "N/A"
                st.metric("Most Used Strategy", most_used)
            
            with col4:
                avg_elements = total_elements / len(st.session_state.processing_history) if st.session_state.processing_history else 0
                st.metric("Avg Elements/Doc", f"{avg_elements:.0f}")
            
            # Clear history button
            if st.button("🗑️ Clear History", type="secondary"):
                st.session_state.processing_history = []
                st.rerun()
        
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin: 2rem 0;">
                <h3>📂 No Processing History</h3>
                <p>Your document processing sessions will appear here!</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-top: 2rem;'>
        <h4>🌐 Advanced Document Processing Suite</h4>
        <p>🔧 Built with ❤️  by Atlas.ai, a company by Suryansh Gupta | 📄 Transform Documents into Structured Intelligence</p>
        <p>💡 <strong>Pro Tip:</strong> Use custom schemas for better data extraction tailored to your needs!</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

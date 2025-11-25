#!/bin/bash
source streamlit_env/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

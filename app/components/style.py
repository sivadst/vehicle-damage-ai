import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        /* Modern Glassmorphism Styling */
        .stApp {
            background-color: #f4f6f9;
        }
        
        .main {
            background-color: transparent;
        }

        /* Metric Cards */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            color: #1f77b4;
        }
        
        /* Custom Cards */
        .result-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            transition: transform 0.2s;
            border-left: 5px solid #1f77b4;
        }
        .result-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        
        /* Severity Badges */
        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
            display: inline-block;
        }
        .badge-minor { background-color: #2ecc71; }
        .badge-moderate { background-color: #f1c40f; color: #333;}
        .badge-severe { background-color: #e74c3c; animation: pulse 2s infinite; }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(231, 76, 60, 0); }
            100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }
        }

        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Buttons */
        .stButton>button {
            border-radius: 8px;
            background: linear-gradient(90deg, #1f77b4 0%, #00529b 100%);
            color: white;
            border: none;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #00529b 0%, #1f77b4 100%);
            transform: scale(1.02);
        }
        </style>
    """, unsafe_allow_html=True)

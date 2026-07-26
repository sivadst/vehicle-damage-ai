"""
Custom SaaS CSS Styling Module.

Injects custom CSS rules for glassmorphism layout, typography, animations,
risk badges, quality alert banners, and interactive component styling.
"""

import streamlit as st


def inject_custom_css():
    """Injects high-end commercial SaaS styles into the Streamlit app context."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Glassmorphism Application Canvas */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1250px;
        }

        /* Metric Value Styling */
        div[data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: #1a365d !important;
        }

        div[data-testid="stMetricLabel"] {
            font-weight: 600 !important;
            color: #4a5568 !important;
            font-size: 0.9rem !important;
        }

        /* Glassmorphism Feature Cards */
        .result-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(12px);
            border-radius: 14px;
            padding: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
            margin-bottom: 24px;
            border: 1px solid rgba(226, 232, 240, 0.8);
            border-left: 6px solid #2b6cb0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .result-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.12), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }

        /* Severity Badges & Status Indicators */
        .badge {
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.85rem;
            letter-spacing: 0.03em;
            color: white;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            margin-top: 10px;
        }

        .badge-minor {
            background: linear-gradient(135deg, #38a169 0%, #276749 100%);
            box-shadow: 0 4px 12px rgba(56, 161, 105, 0.25);
        }

        .badge-moderate {
            background: linear-gradient(135deg, #dd6b20 0%, #c05621 100%);
            box-shadow: 0 4px 12px rgba(221, 107, 32, 0.25);
        }

        .badge-severe {
            background: linear-gradient(135deg, #e53e3e 0%, #9b2c2c 100%);
            box-shadow: 0 4px 14px rgba(229, 62, 62, 0.35);
            animation: pulse-border 2s infinite;
        }

        @keyframes pulse-border {
            0% { box-shadow: 0 0 0 0 rgba(229, 62, 62, 0.6); }
            70% { box-shadow: 0 0 0 12px rgba(229, 62, 62, 0); }
            100% { box-shadow: 0 0 0 0 rgba(229, 62, 62, 0); }
        }

        /* Quality Alert Banner */
        .quality-banner {
            background: #fffaf0;
            border-left: 4px solid #dd6b20;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 16px;
            font-size: 0.9rem;
            color: #7b341e;
        }

        /* Human Review Escalation Banner */
        .escalation-banner {
            background: #fff5f5;
            border-left: 4px solid #e53e3e;
            padding: 14px 18px;
            border-radius: 8px;
            margin-top: 12px;
            color: #9b2c2c;
            font-weight: 600;
            font-size: 0.92rem;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }

        /* Custom Button Gradients */
        .stButton>button {
            border-radius: 10px;
            background: linear-gradient(135deg, #2b6cb0 0%, #1a365d 100%);
            color: white;
            font-weight: 600;
            padding: 0.6rem 1.2rem;
            border: none;
            box-shadow: 0 4px 12px rgba(43, 108, 176, 0.2);
            transition: all 0.25s ease;
        }

        .stButton>button:hover {
            background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%);
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(43, 108, 176, 0.3);
        }

        /* Hide Default Header / Footer Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

import streamlit as st

def setup_theme():
    # Check if theme is already in session state
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # CSS for light and dark themes
    light_theme = """
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E3A8A;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #2563EB;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: #F3F4F6;
            border-radius: 0.5rem;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #1E3A8A;
        }
        .metric-label {
            font-size: 1rem;
            color: #4B5563;
            margin-top: 0.5rem;
        }
        .insight-card {
            background-color: #EFF6FF;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #2563EB;
        }
        .alert-card {
            background-color: #FEF2F2;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #DC2626;
        }
        .success-card {
            background-color: #ECFDF5;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #059669;
        }
        .copy-btn {
            background-color: #2563EB;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            text-decoration: none;
            display: inline-block;
            margin-top: 0.5rem;
            cursor: pointer;
        }
        .copy-btn:hover {
            background-color: #1E40AF;
        }
    </style>
    """
    
    dark_theme = """
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #60A5FA;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #93C5FD;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: #1F2937;
            border-radius: 0.5rem;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #60A5FA;
        }
        .metric-label {
            font-size: 1rem;
            color: #D1D5DB;
            margin-top: 0.5rem;
        }
        .insight-card {
            background-color: #1E3A8A;
            color: #E5E7EB;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #60A5FA;
        }
        .alert-card {
            background-color: #7F1D1D;
            color: #E5E7EB;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #F87171;
        }
        .success-card {
            background-color: #064E3B;
            color: #E5E7EB;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #34D399;
        }
        .copy-btn {
            background-color: #3B82F6;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            text-decoration: none;
            display: inline-block;
            margin-top: 0.5rem;
            cursor: pointer;
        }
        .copy-btn:hover {
            background-color: #2563EB;
        }
    </style>
    """
    
    # Apply the selected theme
    if st.session_state.theme == 'light':
        st.markdown(light_theme, unsafe_allow_html=True)
        plt_style = 'default'
    else:
        st.markdown(dark_theme, unsafe_allow_html=True)
        plt_style = 'dark_background'
    
    return plt_style

def toggle_theme():
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'
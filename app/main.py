import streamlit as st
import plotly.graph_objects as go
from prediction_helper import predict

# -----------------------------------------------------------------------------
# 1. PAGE SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Credit Risk Dashboard",
    page_icon="🔰", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. STYLING (The "Mock Image" Look)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* 1. MAIN CONTAINER CONSTRAINT */
    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        padding-bottom: 0rem;
        margin: auto;
    }

    /* 2. BACKGROUND & TEXT COLORS */
    .stApp {
        background-color: #040813;
        color: #e2e8f0;
        font-family: 'Segoe UI', sans-serif;
    }

    /* 3. INPUT FIELDS (Dark & Compact) */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: #0e1321;
        color: white;
        border: 1px solid #1e293b;
        border-radius: 6px;
        height: 45px;
    }
    
    /* 4. LABELS */
    .stMarkdown label p {
        font-size: 13px !important;
        color: #94a3b8;
    }

    /* 5. BUTTON (Matches the "Calculate Risk" in mock) */
    .stButton > button {
        width: 100%;
        background-color: #1e3a8a; /* Dark Blue */
        color: white;
        border: 1px solid #3b82f6;
        padding: 12px;
        border-radius: 6px; 
        font-weight: bold;
        text-transform: uppercase;
        margin-top: 15px;
    }
    .stButton > button:hover {
        background-color: #2563eb;
    }
    
    /* 6. CUSTOM METRICS (For Score & Rating) */
    .custom-metric {
        background-color: #151b2b;
        border: 1px solid #2d3748;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def create_gauge_chart(probability):
    if probability < 0.3:
        bar_color = "#10b981" # Green
    elif probability < 0.7:
        bar_color = "#f59e0b" # Orange/Gold
    else:
        bar_color = "#ef4444" # Red

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = probability * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Default Probability", 'font': {'size': 18, 'color': '#cbd5e1'}},
        number = {'suffix': "%", 'font': {'size': 40, 'color': 'white'}},
        gauge = {
            'axis': {'range': [None, 100], 'visible': False},
            'bar': {'color': bar_color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [{'range': [0, 100], 'color': '#1e293b'}], # Dark track
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': probability * 100
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white"},
        height=220,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# -----------------------------------------------------------------------------
# 4. MAIN APP STRUCTURE
# -----------------------------------------------------------------------------

st.markdown("<h2 style='color: #fceea7; margin-bottom: 15px;'>Credit Risk Modelling Dashboard</h2>", unsafe_allow_html=True)

# Layout: Inputs (Left 70%) | Results (Right 30%)
col_input, col_result = st.columns([2.2, 1], gap="medium")

with col_input:
    st.markdown("##### APPLICANT DATA")
    
    # Grid Layout: 4 Rows x 3 Columns
    
    # --- ROW 1 ---
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1: age = st.number_input('Age', 18, 100, 28)
    with r1c2: income = st.number_input('Income', 0, value=1200000)
    with r1c3: loan_amount = st.number_input('Loan Amount', 0, value=2560000)

    # --- ROW 2 ---
    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1: 
        # Display Only (Calculated) - Styled to look like an Input Box
        lti = loan_amount / income if income > 0 else 0
        st.markdown(f"""
        <div style="padding: 0px;">
            <label style="font-size: 13px; color: #94a3b8; margin-bottom: 2px;">Loan to Income Ratio</label>
            <div style="
                background-color: #0e1321; 
                border: 1px solid #1e293b; 
                border-radius: 6px; 
                padding: 8px 10px; 
                color: white; 
                font-size: 14px; 
                height: 45px; 
                display: flex; 
                align-items: center;">
                {lti:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with r2c2: loan_tenure_months = st.number_input('Loan Tenure (Months)', 0, value=36)
    with r2c3: avg_dpd_per_delinquency = st.number_input('Avg DPD', 0, value=20)

    # --- ROW 3 ---
    r3c1, r3c2, r3c3 = st.columns(3)
    with r3c1: delinquency_ratio = st.number_input('Delinquency Ratio', 0, 100, 30)
    with r3c2: credit_utilization_ratio = st.number_input('Credit Utilization Ratio', 0, 100, 30)
    with r3c3: num_open_accounts = st.number_input('Open Loan Accounts', 1, 4, 2)

    # --- ROW 4 ---
    r4c1, r4c2, r4c3 = st.columns(3)
    with r4c1: residence_type = st.selectbox('Residence Type', ['Owned', 'Rented', 'Mortgage'])
    with r4c2: loan_purpose = st.selectbox('Loan Purpose', ['Education', 'Home', 'Auto', 'Personal'])
    with r4c3: loan_type = st.selectbox('Loan Type', ['Unsecured', 'Secured'])

    # --- ACTION BUTTON ---
    if st.button('CALCULATE RISK'):
        probability, credit_score, rating = predict(
            age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
            delinquency_ratio, credit_utilization_ratio, num_open_accounts,
            residence_type, loan_purpose, loan_type
        )
        st.session_state.probability = probability
        st.session_state.credit_score = credit_score
        st.session_state.rating = rating

with col_result:
    st.markdown("##### RISK ASSESSMENT")
    
    # Initialize Session State
    if 'probability' not in st.session_state:
        st.session_state.probability = 0.64 
        st.session_state.credit_score = 515
        st.session_state.rating = "Average"

    # Container for Results
    with st.container():
        # 1. Gauge Chart
        fig = create_gauge_chart(st.session_state.probability)
        st.plotly_chart(fig, use_container_width=True)

        # 2. Metrics (Side by Side)
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"""
            <div class="custom-metric">
                <div style="color: #60a5fa; font-size: 12px;">Credit Score</div>
                <div style="color: #fff; font-size: 24px; font-weight: bold;">{st.session_state.credit_score}</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="custom-metric">
                <div style="color: #f59e0b; font-size: 12px;">Rating</div>
                <div style="color: #fff; font-size: 22px; font-weight: bold;">{st.session_state.rating}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        # 3. Message
        st.caption("Requires careful review of applicant credit history.")
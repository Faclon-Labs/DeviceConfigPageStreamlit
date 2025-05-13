import os
import json
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import constants as c
import io_connect as io
import time

st.set_page_config(
    layout="wide",
    page_title="FaclonLabs-AI-Studio",
    page_icon="https://storage.googleapis.com/ai-workbench/Data%20Import.svg",
)

# Enhanced CSS for better visual appearance
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
    }
    .metric-icon {
        color: #00bcd4;
        font-size: 24px;
        margin-bottom: 12px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 600;
        color: #2c3e50;
        margin: 8px 0;
    }
    .metric-label {
        font-size: 16px;
        color: #64748b;
        margin-bottom: 8px;
    }
    .metric-timestamp {
        font-size: 12px;
        color: #94a3b8;
    }
    .gauge-container {
        margin-top: 2rem;
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.header("Dashboard")


# Add debug info below device card
# Add Device Info Card in sidebar
st.sidebar.markdown("## Device Info")
st.sidebar.markdown("""
    <div style="background-color: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); text-align: center; margin-bottom: 2rem;">
        <div style="background-color: #2c3e50; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 1rem auto; display: flex; justify-content: center; align-items: center;">
            <span style="font-size: 2rem;">📟</span>
        </div>
        <div style="color: #64748b; margin-bottom: 0.5rem;">
            <span style="background-color: #e2e8f0; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem;">
                ADIFM_B2
            </span>
        </div>
        <h3 style="color: #2c3e50; font-size: 1.25rem; margin: 0.75rem 0;">ADIFM_B2</h3>
        <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 0.5rem;">
            Device Type: FLOWMETER
        </div>
        <div style="color: #94a3b8; font-size: 0.75rem;">
            Added On: 19/04/2025 @ 11:57 am</div>
    </div>
""", 
unsafe_allow_html=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("### Debug Info")
USER_ID = "645a159222722a319ca5f5ad"
data_access = io.DataAccess(
    user_id=USER_ID,
    data_url=c.DATA_URL,
    ds_url=c.DS_URL,
    log_time=False,
)

# Create four metric cards in a row
col1, col2, col3= st.columns(3)

with st.spinner("Fetching current data..."):
    # Fetch latest data
    current_data = data_access.get_dp(
        device_id="ADIFM_B2",
        sensor_list=["FLOW", "TOTAL"],
        end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    
    # Yesterday's data
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_data = data_access.get_dp(
        device_id="ADIFM_B2",
        sensor_list=["FLOW", "TOTAL"],
        end_time=yesterday.strftime("%Y-%m-%d %H:%M:%S"),
    )

    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-icon">📊</div>
                <div class="metric-label">Yesterday's Consumption</div>
                <div class="metric-value">{:,.0f} m³</div>
            </div>
        """.format(yesterday_data["TOTAL"].iloc[0] if not yesterday_data.empty else 0), 
        unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-icon">📈</div>
                <div class="metric-label">Today's Consumption</div>
                <div class="metric-value">{:,.0f} m³</div>
            </div>
        """.format(current_data["TOTAL"].iloc[0] if not current_data.empty else 0),
        unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-icon">🔄</div>
                <div class="metric-label">Totalizer</div>
                <div class="metric-value">{:,.0f} m³</div>
                <div class="metric-timestamp">Last Data At: {}</div>
            </div>
        """.format(
            current_data["TOTAL"].iloc[0] if not current_data.empty else 0,
            datetime.now().strftime("%m/%d/%Y @ %I:%M:%S %p")
        ),
        unsafe_allow_html=True)

# Add gauge chart for flowrate and total consumption with improved styling
if not current_data.empty:
    # Create two columns for gauges
    gauge_col1, gauge_col2 = st.columns(2)
    
    with gauge_col1:
        # Flow Rate Gauge
        flow_value = current_data["FLOW"].iloc[0]
        max_range = 1000
        
        fig1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=flow_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Flow Rate (m³/hr)", 'font': {'size': 22, 'color': '#2c3e50'}},
            number={'font': {'size': 24, 'color': '#2c3e50'}},
            gauge={
                'axis': {
                    'range': [None, max_range],
                    'tickwidth': 1,
                    'tickcolor': '#2c3e50',
                    'ticktext': [f'{i}M' for i in range(0, max_range + 1, 200)],
                    'tickvals': list(range(0, max_range + 1, 200))
                },
                'bar': {'color': '#00bcd4', 'thickness': 0.6},
                'bgcolor': 'white',
                'borderwidth': 2,
                'bordercolor': '#e2e8f0',
                'steps': [
                    {'range': [0, max_range/3], 'color': '#e2e8f0'},
                    {'range': [max_range/3, max_range*2/3], 'color': '#f1f5f9'},
                    {'range': [max_range*2/3, max_range], 'color': '#f8fafc'}
                ],
                'threshold': {
                    'line': {'color': '#ef4444', 'width': 4},
                    'thickness': 0.8,
                    'value': max_range * 0.8
                }
            }
        ))
        
        fig1.update_layout(
            height=250,  # Reduced height
            margin=dict(l=20, r=20, t=40, b=20),  # Reduced margins
            paper_bgcolor="rgba(0,0,0,0)",
            font={'family': "Arial"}
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
# Add Flow Rate vs Network Strength Graph
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
    <div style="background-color: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
        <h3 style="color: #2c3e50; margin-bottom: 1rem;">Flowrate V/S Network Strength Variation With Time</h3>
    </div>
""", unsafe_allow_html=True)

# Get time series data for the graph
end_time = datetime.now()
start_time = end_time - timedelta(hours=24)  # Last 24 hours data

# Debug information
st.sidebar.write("Debug Info:")
st.sidebar.write("Start time:", start_time)
st.sidebar.write("End time:", end_time)

historical_data = data_access.data_query(
    device_id="ADIFM_B2",
    sensor_list=["FLOW", "RSSI"],  # Changed to RSSI for network strength
    start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
    end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
)

# Debug the data
if not historical_data.empty:
    st.sidebar.write("Available columns:", historical_data.columns.tolist())
    
    # Convert timestamp to datetime if it's not already
    if 'timestamp' in historical_data.columns:
        historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'])
        historical_data.set_index('timestamp', inplace=True)
    
    fig = go.Figure()
    
    # Add Flow Rate trace
    fig.add_trace(go.Scatter(
        x=historical_data.index,
        y=historical_data["FLOW"],
        name="Flowrate",
        line=dict(color="#00bcd4", width=2),
        yaxis="y"
    ))
    
    # Add Network Strength trace
    fig.add_trace(go.Scatter(
        x=historical_data.index,
        y=historical_data["RSSI"],  # Changed to RSSI
        name="Network Strength",
        line=dict(color="#4c1d95", width=2),
        yaxis="y2"
    ))
    
    # Update layout with two y-axes and improved time formatting
    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=30, b=30),
        paper_bgcolor="white",
        plot_bgcolor="#f8fafc",
        font=dict(family="Arial"),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            title=dict(
                text="Flowrate (m³/hr)",
                font=dict(color="#00bcd4")
            ),
            tickfont=dict(color="#00bcd4"),
            gridcolor="#e2e8f0"
        ),
        yaxis2=dict(
            title=dict(
                text="Network Strength",
                font=dict(color="#4c1d95")
            ),
            tickfont=dict(color="#4c1d95"),
            anchor="x",
            overlaying="y",
            side="right",
            gridcolor="#e2e8f0",
            range=[0, 100]  # Set fixed range for network strength
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#e2e8f0",
            title="Time",
            tickformat="%H:%M\n%Y-%m-%d",  # Improved time format
            tickangle=-45,
            dtick=3600000  # Show ticks every hour
        )
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No historical data available for the graph")

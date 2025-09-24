import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np
import time
from stock_screener import run_stock_screening  # We'll create this module

# Page configuration
st.set_page_config(
    page_title="📈 Stock Screener Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for dark mode
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Dynamic CSS based on dark mode
def get_custom_css():
    if st.session_state.dark_mode:
        return """
        <style>
            /* Dark Mode Styles */
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            
            .main-header {
                font-size: 3rem;
                font-weight: bold;
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-align: center;
                margin-bottom: 2rem;
            }
            
            .metric-card {
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
                padding: 1rem;
                border-radius: 10px;
                color: #e2e8f0;
                text-align: center;
                margin: 0.5rem 0;
                border: 1px solid #4a5568;
            }
            
            /* Ultra-strong dark mode metric selectors - covers all possible cases */
            div[data-testid="metric-container"],
            .stMetric > div,
            .metric-container {
                background-color: rgba(45, 55, 72, 0.95) !important;
                border: 2px solid #4facfe !important;
                border-radius: 12px !important;
                padding: 1.2rem !important;
                box-shadow: 0 4px 12px rgba(79, 172, 254, 0.15) !important;
            }
            
            /* All possible metric label selectors */
            div[data-testid="metric-container"] div[data-testid="metric-label"],
            div[data-testid="metric-container"] .metric-label,
            .stMetric .metric-label,
            .stMetric label,
            div[data-testid="metric-label"] {
                color: #e2e8f0 !important;
                font-size: 0.9rem !important;
                font-weight: 500 !important;
                opacity: 0.9 !important;
            }
            
            /* Comprehensive metric value selectors */
            div[data-testid="metric-container"] div[data-testid="metric-value"],
            div[data-testid="metric-container"] .metric-value,
            div[data-testid="metric-value"],
            .stMetric div[data-testid="metric-value"],
            .stMetric .metric-value,
            .metric div[data-testid="metric-value"],
            [data-testid="metric-value"],
            .js-plot-link-container + div div[data-testid="metric-value"],
            div[data-testid="metric-container"] > div > div:last-child,
            .stMetric > div > div:last-child {
                color: #4facfe !important;
                font-size: 2.2rem !important;
                font-weight: 800 !important;
                text-shadow: 0 0 10px rgba(79, 172, 254, 0.3) !important;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }
            
            /* Force all text inside metrics to be visible */
            div[data-testid="metric-container"] * {
                color: #4facfe !important;
                opacity: 1 !important;
                visibility: visible !important;
            }
            
            /* Specific override for metric labels */
            div[data-testid="metric-container"] div[data-testid="metric-label"] * {
                color: #e2e8f0 !important;
            }
            
            /* Debug and force visibility animation */
            @keyframes forceVisible {
                0% { opacity: 0; }
                100% { opacity: 1; }
            }
            
            div[data-testid="metric-value"],
            [data-testid="metric-value"] {
                animation: forceVisible 0.5s ease-in-out !important;
                color: #4facfe !important;
            }
            
            /* Nuclear option - force all metric text to be visible */
            .stMetric, .stMetric *, div[data-testid="metric-container"], div[data-testid="metric-container"] * {
                color: #4facfe !important;
                text-decoration: none !important;
                background: transparent !important;
            }
            
            /* Re-override labels to correct color */
            div[data-testid="metric-label"], div[data-testid="metric-label"] * {
                color: #e2e8f0 !important;
            }
            
            /* Progress bar styling for dark mode */
            .stProgress .stProgress-bar {
                background-color: #4facfe !important;
            }
            
            .filter-section {
                background-color: #1a202c;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 1rem 0;
                border: 1px solid #2d3748;
            }
            
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 0.5rem 2rem;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            /* Dark mode toggle button styling */
            .stButton > button[data-testid="baseButton-secondary"] {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
            }
            
            .sidebar .sidebar-content {
                background-color: #1a202c;
            }
            
            /* Dark mode specific elements */
            .stSelectbox > div > div {
                background-color: #2d3748;
                color: #e2e8f0;
            }
            
            .stSlider > div > div > div {
                background-color: #4a5568;
            }
            
            .stDataFrame {
                background-color: #1a202c;
            }
            
            .dark-mode-badge {
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
                color: #e2e8f0;
                padding: 0.3rem 0.8rem;
                border-radius: 20px;
                font-size: 0.8rem;
                border: 1px solid #4a5568;
            }
            
            .feature-card-dark {
                background-color: #1a202c;
                padding: 1.5rem;
                border-radius: 10px;
                border: 1px solid #2d3748;
                margin: 1rem 0;
            }
        </style>
        """
    else:
        return """
        <style>
            /* Light Mode Styles */
            .stApp {
                background-color: #ffffff;
                color: #262730;
            }
            
            .main-header {
                font-size: 3rem;
                font-weight: bold;
                color: #1E88E5;
                text-align: center;
                margin-bottom: 2rem;
            }
            
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin: 0.5rem 0;
            }
            
            /* Comprehensive light mode metrics */
            div[data-testid="metric-container"],
            .stMetric > div,
            .metric-container {
                background-color: rgba(248, 249, 250, 0.95) !important;
                border: 2px solid #1E88E5 !important;
                border-radius: 12px !important;
                padding: 1.2rem !important;
                box-shadow: 0 4px 12px rgba(30, 136, 229, 0.15) !important;
            }
            
            /* All possible light mode label selectors */
            div[data-testid="metric-container"] div[data-testid="metric-label"],
            div[data-testid="metric-container"] .metric-label,
            .stMetric .metric-label,
            .stMetric label,
            div[data-testid="metric-label"] {
                color: #495057 !important;
                font-size: 0.9rem !important;
                font-weight: 500 !important;
                opacity: 0.8 !important;
            }
            
            /* Comprehensive light mode value selectors */
            div[data-testid="metric-container"] div[data-testid="metric-value"],
            div[data-testid="metric-container"] .metric-value,
            div[data-testid="metric-value"],
            .stMetric div[data-testid="metric-value"],
            .stMetric .metric-value,
            .metric div[data-testid="metric-value"],
            [data-testid="metric-value"],
            .js-plot-link-container + div div[data-testid="metric-value"],
            div[data-testid="metric-container"] > div > div:last-child,
            .stMetric > div > div:last-child {
                color: #1E88E5 !important;
                font-size: 2.2rem !important;
                font-weight: 800 !important;
                text-shadow: 0 0 10px rgba(30, 136, 229, 0.2) !important;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }
            
            .filter-section {
                background-color: #f8f9fa;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 1rem 0;
            }
            
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 0.5rem 2rem;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            /* Light mode toggle button styling */
            .stButton > button[data-testid="baseButton-secondary"] {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .light-mode-badge {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 0.3rem 0.8rem;
                border-radius: 20px;
                font-size: 0.8rem;
            }
            
            .feature-card-light {
                background-color: #f8f9fa;
                padding: 1.5rem;
                border-radius: 10px;
                border: 1px solid #e9ecef;
                margin: 1rem 0;
            }
        </style>
        """

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Force metric visibility with JavaScript in dark mode
if st.session_state.dark_mode:
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            // Force metric values to be visible
            const metricValues = document.querySelectorAll('[data-testid="metric-value"]');
            metricValues.forEach(function(element) {
                element.style.color = '#4facfe !important';
                element.style.visibility = 'visible !important';
                element.style.opacity = '1 !important';
                element.style.display = 'block !important';
                element.style.fontSize = '2.2rem !important';
                element.style.fontWeight = '800 !important';
            });
            
            // Set metric labels
            const metricLabels = document.querySelectorAll('[data-testid="metric-label"]');
            metricLabels.forEach(function(element) {
                element.style.color = '#e2e8f0 !important';
                element.style.opacity = '0.9 !important';
            });
        }, 500);
    });
    </script>
    """, unsafe_allow_html=True)

# Header with dark mode indicator
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown('<h1 class="main-header">📈 Stock Screener Dashboard</h1>', unsafe_allow_html=True)
with header_col2:
    mode_badge = "🌙 Dark" if st.session_state.dark_mode else "☀️ Light"
    badge_class = "dark-mode-badge" if st.session_state.dark_mode else "light-mode-badge"
    st.markdown(f'<div class="{badge_class}">{mode_badge}</div>', unsafe_allow_html=True)

# Sidebar for filters
with st.sidebar:
    # Dark mode toggle at the top of sidebar
    st.markdown("### 🎨 Appearance")
    
    # Dark mode toggle button that works reliably
    current_mode = "🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode"
    if st.button(current_mode, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    
    # Show current mode status
    mode_status = "Currently: Dark Mode 🌙" if st.session_state.dark_mode else "Currently: Light Mode ☀️"
    st.caption(mode_status)
    
    st.markdown("---")
    st.header("🔧 Screening Criteria")
    
    st.subheader("📊 Fundamental Filters")
    max_pe = st.slider("Maximum Forward P/E", 5, 50, 15)
    min_price = st.slider("Minimum Price ($)", 1, 100, 15)
    min_market_cap = st.selectbox("Minimum Market Cap", 
                                 ["1B", "5B", "10B", "50B", "100B"], 
                                 index=2)
    min_beta = st.slider("Minimum Beta", 0.0, 2.0, 1.0, 0.1)
    
    st.subheader("📈 Technical Filters")
    min_return = st.slider("Minimum 5-day Return (%)", -10, 20, 5)
    rsi_min = st.slider("RSI Range Min", 10, 50, 30)
    rsi_max = st.slider("RSI Range Max", 50, 90, 70)
    
    st.subheader("💹 Volume & Momentum")
    min_volume = st.selectbox("Minimum Avg Volume", 
                             ["100K", "500K", "1M", "2M", "5M"], 
                             index=3)
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        enable_finviz = st.checkbox("Enable Finviz Scraping", True)
        consecutive_days = st.slider("Min Consecutive Up Days", 1, 5, 3)
        recommendation_filter = st.selectbox("Minimum Recommendation", 
                                           ["Any", "Buy", "Strong Buy"], 
                                           index=2)

# Convert market cap and volume to numbers
market_cap_values = {"1B": 1e9, "5B": 5e9, "10B": 1e10, "50B": 5e10, "100B": 1e11}
volume_values = {"100K": 1e5, "500K": 5e5, "1M": 1e6, "2M": 2e6, "5M": 5e6}

min_market_cap_value = market_cap_values[min_market_cap]
min_volume_value = volume_values[min_volume]

# Main content area
col1, col2, col3, col4 = st.columns(4)

# Initialize session state
if 'screening_results' not in st.session_state:
    st.session_state.screening_results = None
if 'last_run' not in st.session_state:
    st.session_state.last_run = None

# Run screening button
if st.button("🚀 Run Stock Screening", type="primary"):
    # Create a styled container for progress indicators based on theme
    progress_container = st.container()
    with progress_container:
        if st.session_state.dark_mode:
            st.markdown("""
            <div style="
                background: rgba(45, 55, 72, 0.9); 
                padding: 1.5rem; 
                border-radius: 10px; 
                border: 1px solid #4a5568; 
                margin: 1rem 0;
                text-align: center;
            ">
                <p style="color: #e2e8f0; font-size: 1.1rem; margin: 0;">
                    🔍 Analyzing stocks... This may take a few minutes...
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: rgba(248, 249, 250, 0.9); 
                padding: 1.5rem; 
                border-radius: 10px; 
                border: 1px solid #e9ecef; 
                margin: 1rem 0;
                text-align: center;
            ">
                <p style="color: #495057; font-size: 1.1rem; margin: 0;">
                    🔍 Analyzing stocks... This may take a few minutes...
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create screening parameters
        params = {
            'max_pe': max_pe,
            'min_price': min_price,
            'min_market_cap': min_market_cap_value,
            'min_beta': min_beta,
            'min_return': min_return / 100,  # Convert to decimal
            'rsi_min': rsi_min,
            'rsi_max': rsi_max,
            'min_volume': min_volume_value,
            'enable_finviz': enable_finviz,
            'consecutive_days': consecutive_days,
            'recommendation_filter': recommendation_filter.lower().replace(' ', '_')
        }
        
        try:
            # Run the screening (we'll implement this)
            results = run_stock_screening(params, progress_bar, status_text)
            st.session_state.screening_results = results
            st.session_state.last_run = datetime.now()
            st.success(f"✅ Screening completed! Found {len(results)} qualifying stocks.")
        except Exception as e:
            st.error(f"❌ Error during screening: {str(e)}")

# Display results if available
if st.session_state.screening_results is not None:
    results_df = pd.DataFrame(st.session_state.screening_results)
    
    if len(results_df) > 0:
        # Metrics row
        with col1:
            st.metric("📊 Stocks Found", len(results_df))
        with col2:
            avg_pe = results_df['Fwd P/E'].mean() if 'Fwd P/E' in results_df.columns else 0
            st.metric("📈 Avg P/E Ratio", f"{avg_pe:.1f}")
        with col3:
            avg_rsi = results_df['RSI'].mean() if 'RSI' in results_df.columns else 0
            st.metric("📊 Avg RSI", f"{avg_rsi:.1f}")
        with col4:
            if st.session_state.last_run:
                st.metric("🕒 Last Updated", st.session_state.last_run.strftime("%H:%M"))
        
        # Charts section
        st.subheader("📊 Analysis Charts")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            if len(results_df) > 0 and 'Sector' in results_df.columns:
                # Sector distribution
                sector_counts = results_df['Sector'].value_counts()
                
                # Dark mode color scheme
                if st.session_state.dark_mode:
                    colors = px.colors.qualitative.Dark24
                    paper_bgcolor = 'rgba(0,0,0,0)'
                    plot_bgcolor = 'rgba(0,0,0,0)'
                    font_color = '#e2e8f0'
                else:
                    colors = px.colors.qualitative.Set3
                    paper_bgcolor = 'rgba(0,0,0,0)'
                    plot_bgcolor = 'rgba(0,0,0,0)'
                    font_color = '#262730'
                
                fig_sector = px.pie(values=sector_counts.values, 
                                  names=sector_counts.index,
                                  title="📊 Sector Distribution",
                                  color_discrete_sequence=colors)
                fig_sector.update_traces(textposition='inside', textinfo='percent+label')
                fig_sector.update_layout(
                    paper_bgcolor=paper_bgcolor,
                    plot_bgcolor=plot_bgcolor,
                    font_color=font_color,
                    title_font_color=font_color
                )
                st.plotly_chart(fig_sector, use_container_width=True)
        
        with chart_col2:
            if len(results_df) > 0 and 'RSI' in results_df.columns:
                # RSI distribution
                # Enhanced RSI Distribution Chart
                if st.session_state.dark_mode:
                    bar_color = '#4facfe'
                    paper_bgcolor = 'rgba(0,0,0,0)'
                    plot_bgcolor = 'rgba(0,0,0,0)'
                    font_color = '#e2e8f0'
                    grid_color = '#4a5568'
                    line_colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']
                else:
                    bar_color = '#667eea'
                    paper_bgcolor = 'rgba(0,0,0,0)'
                    plot_bgcolor = 'rgba(0,0,0,0)'
                    font_color = '#262730'
                    grid_color = '#e9ecef'
                    line_colors = ['#e74c3c', '#2ecc71', '#3498db']
                
                fig_rsi = px.histogram(
                    results_df, 
                    x='RSI', 
                    title="� RSI Distribution Analysis",
                    nbins=15,
                    color_discrete_sequence=[bar_color],
                    labels={'RSI': 'RSI Value', 'count': 'Number of Stocks'},
                    opacity=0.8
                )
                
                # Add reference lines for RSI zones
                fig_rsi.add_vline(x=30, line_dash="dash", line_color=line_colors[0], 
                                annotation_text="Oversold (30)", annotation_position="top")
                fig_rsi.add_vline(x=70, line_dash="dash", line_color=line_colors[0], 
                                annotation_text="Overbought (70)", annotation_position="top")
                fig_rsi.add_vline(x=50, line_dash="dot", line_color=line_colors[1], 
                                annotation_text="Neutral (50)", annotation_position="bottom")
                
                # Enhanced layout
                fig_rsi.update_layout(
                    showlegend=False,
                    paper_bgcolor=paper_bgcolor,
                    plot_bgcolor=plot_bgcolor,
                    font_color=font_color,
                    title_font_color=font_color,
                    title_font_size=16,
                    xaxis=dict(
                        gridcolor=grid_color,
                        title_font_size=14,
                        tickfont_size=12,
                        range=[0, 100]
                    ),
                    yaxis=dict(
                        gridcolor=grid_color,
                        title_font_size=14,
                        tickfont_size=12
                    ),
                    margin=dict(l=40, r=40, t=60, b=40),
                    height=400
                )
                
                # Add hover template
                fig_rsi.update_traces(
                    hovertemplate='<b>RSI Range:</b> %{x}<br><b>Count:</b> %{y}<extra></extra>'
                )
                
                st.plotly_chart(fig_rsi, use_container_width=True)
        
        # Interactive data table
        st.subheader("📋 Screening Results")
        
        # Add sorting options
        sort_col1, sort_col2 = st.columns(2)
        with sort_col1:
            sort_by = st.selectbox("Sort by:", 
                                 ['Market Cap', 'Price', 'Fwd P/E', 'RSI', 'Beta'])
        with sort_col2:
            sort_order = st.selectbox("Order:", ['Descending', 'Ascending'])
        
        # Sort the dataframe
        ascending = sort_order == 'Ascending'
        if sort_by in results_df.columns:
            results_df = results_df.sort_values(by=sort_by, ascending=ascending)
        
        # Format the dataframe for display
        display_df = results_df.copy()
        if 'Market Cap' in display_df.columns:
            display_df['Market Cap'] = display_df['Market Cap'].apply(
                lambda x: f"${x/1e9:.1f}B" if pd.notnull(x) else "N/A"
            )
        if 'Price' in display_df.columns:
            display_df['Price'] = display_df['Price'].apply(
                lambda x: f"${x:.2f}" if pd.notnull(x) else "N/A"
            )
        
        # Display with styling
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"stock_screening_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
        
        # Individual stock details
        if len(results_df) > 0:
            st.subheader("🔍 Stock Details")
            selected_stock = st.selectbox("Select a stock for detailed analysis:", 
                                        results_df['Ticker'].tolist())
            
            if selected_stock:
                with st.spinner(f"Loading details for {selected_stock}..."):
                    try:
                        ticker = yf.Ticker(selected_stock)
                        hist = ticker.history(period="3mo")
                        
                        if not hist.empty:
                            # Dark mode styling for candlestick chart
                            if st.session_state.dark_mode:
                                paper_bgcolor = 'rgba(0,0,0,0)'
                                plot_bgcolor = 'rgba(0,0,0,0)'
                                font_color = '#e2e8f0'
                                grid_color = '#4a5568'
                            else:
                                paper_bgcolor = 'rgba(0,0,0,0)'
                                plot_bgcolor = 'rgba(0,0,0,0)'
                                font_color = '#262730'
                                grid_color = '#e9ecef'
                            
                            fig = go.Figure(data=go.Candlestick(x=hist.index,
                                                              open=hist['Open'],
                                                              high=hist['High'],
                                                              low=hist['Low'],
                                                              close=hist['Close']))
                            fig.update_layout(
                                title=f"{selected_stock} - 3 Month Price Chart",
                                xaxis_title="Date",
                                yaxis_title="Price ($)",
                                paper_bgcolor=paper_bgcolor,
                                plot_bgcolor=plot_bgcolor,
                                font_color=font_color,
                                title_font_color=font_color,
                                xaxis=dict(gridcolor=grid_color),
                                yaxis=dict(gridcolor=grid_color)
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not load chart for {selected_stock}: {str(e)}")
    
    else:
        st.warning("🔍 No stocks found matching the current criteria. Try adjusting the filters to see results.")
        
        # Suggestions for relaxing criteria
        st.subheader("💡 Suggestions to Get Results:")
        suggestions = [
            f"• Increase Forward P/E limit from {max_pe} to {max_pe + 10}",
            f"• Reduce minimum return from {min_return}% to {max(1, min_return-2)}%",
            f"• Lower minimum market cap from {min_market_cap} to a smaller value",
            "• Change recommendation filter from 'Strong Buy' to 'Buy' or 'Any'",
            f"• Reduce consecutive up days from {consecutive_days} to {max(1, consecutive_days-1)}"
        ]
        for suggestion in suggestions:
            st.write(suggestion)

else:
    # Welcome message
    st.info("👋 Welcome to the Stock Screener Dashboard! Use the sidebar to set your criteria and click 'Run Stock Screening' to begin.")
    
    # Feature highlights
    st.subheader("🌟 Features:")
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    card_class = "feature-card-dark" if st.session_state.dark_mode else "feature-card-light"
    
    with feature_col1:
        st.markdown(f"""
        <div class="{card_class}">
        <strong>📊 Advanced Filtering</strong><br>
        • Fundamental analysis<br>
        • Technical indicators<br>
        • Volume & momentum<br>
        • Custom criteria
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown(f"""
        <div class="{card_class}">
        <strong>📈 Interactive Charts</strong><br>
        • Sector distribution<br>
        • RSI analysis<br>
        • Price charts<br>
        • Real-time data
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col3:
        st.markdown(f"""
        <div class="{card_class}">
        <strong>💾 Export & Analysis</strong><br>
        • Download results<br>
        • Detailed stock view<br>
        • Historical charts<br>
        • Progress tracking
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("📈 **Stock Screener Dashboard** | Built with Streamlit | Data from Yahoo Finance & Finviz")
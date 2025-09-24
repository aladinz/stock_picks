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

# Custom CSS for modern styling
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📈 Stock Screener Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for filters
with st.sidebar:
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
    with st.spinner("🔍 Analyzing stocks... This may take a few minutes..."):
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
                fig_sector = px.pie(values=sector_counts.values, 
                                  names=sector_counts.index,
                                  title="📊 Sector Distribution",
                                  color_discrete_sequence=px.colors.qualitative.Set3)
                fig_sector.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_sector, use_container_width=True)
        
        with chart_col2:
            if len(results_df) > 0 and 'RSI' in results_df.columns:
                # RSI distribution
                fig_rsi = px.histogram(results_df, x='RSI', 
                                     title="📈 RSI Distribution",
                                     nbins=10,
                                     color_discrete_sequence=['#667eea'])
                fig_rsi.update_layout(showlegend=False)
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
                            fig = go.Figure(data=go.Candlestick(x=hist.index,
                                                              open=hist['Open'],
                                                              high=hist['High'],
                                                              low=hist['Low'],
                                                              close=hist['Close']))
                            fig.update_layout(title=f"{selected_stock} - 3 Month Price Chart",
                                            xaxis_title="Date",
                                            yaxis_title="Price ($)")
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
    
    with feature_col1:
        st.markdown("""
        **📊 Advanced Filtering**
        - Fundamental analysis
        - Technical indicators
        - Volume & momentum
        - Custom criteria
        """)
    
    with feature_col2:
        st.markdown("""
        **📈 Interactive Charts**
        - Sector distribution
        - RSI analysis
        - Price charts
        - Real-time data
        """)
    
    with feature_col3:
        st.markdown("""
        **💾 Export & Analysis**
        - Download results
        - Detailed stock view
        - Historical charts
        - Progress tracking
        """)

# Footer
st.markdown("---")
st.markdown("📈 **Stock Screener Dashboard** | Built with Streamlit | Data from Yahoo Finance & Finviz")
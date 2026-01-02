import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
from pathlib import Path

import database as db
from charts import (
    create_market_scoreboard,
    create_mom_comparison,
    create_top_movers,
    create_pareto_chart,
    create_variance_analysis,
    create_trends_chart,
    create_totals_trend,
    create_action_plan_table,
    format_currency
)

st.set_page_config(
    page_title="Financial Analytics Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_demo_data():
    """Load demo data for showcase purposes"""
    np.random.seed(42)
    
    markets = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East']
    ledgers = [
        'Revenue - Product Sales', 'Revenue - Services',
        'COGS - Materials', 'COGS - Labor', 'COGS - Overhead',
        'SG&A - Marketing', 'SG&A - Sales', 'SG&A - Admin',
        'R&D - Development', 'R&D - Research',
        'Depreciation', 'Interest Expense', 'Other Income', 'Tax Expense'
    ]
    months = ['2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12']
    
    base_values = {
        'Revenue - Product Sales': 1000000, 'Revenue - Services': 300000,
        'COGS - Materials': -400000, 'COGS - Labor': -200000, 'COGS - Overhead': -100000,
        'SG&A - Marketing': -80000, 'SG&A - Sales': -120000, 'SG&A - Admin': -60000,
        'R&D - Development': -50000, 'R&D - Research': -30000,
        'Depreciation': -25000, 'Interest Expense': -15000, 'Other Income': 10000, 'Tax Expense': -50000
    }
    market_multipliers = {'North America': 1.5, 'Europe': 1.2, 'Asia Pacific': 1.0, 'Latin America': 0.6, 'Middle East': 0.4}
    
    db.save_column_mapping('Market', 'Ledger Account', 'Actual', 'Plan', 'Forecast')
    
    ledger_mapping = pd.DataFrame([
        {'ledger': 'Revenue - Product Sales', 'bucket': 'Revenue', 'driver': 'Volume', 'controllable': True},
        {'ledger': 'Revenue - Services', 'bucket': 'Revenue', 'driver': 'Volume', 'controllable': True},
        {'ledger': 'COGS - Materials', 'bucket': 'COGS', 'driver': 'Volume', 'controllable': True},
        {'ledger': 'COGS - Labor', 'bucket': 'COGS', 'driver': 'Headcount', 'controllable': True},
        {'ledger': 'COGS - Overhead', 'bucket': 'COGS', 'driver': 'Fixed', 'controllable': False},
        {'ledger': 'SG&A - Marketing', 'bucket': 'SG&A', 'driver': 'Discretionary', 'controllable': True},
        {'ledger': 'SG&A - Sales', 'bucket': 'SG&A', 'driver': 'Headcount', 'controllable': True},
        {'ledger': 'SG&A - Admin', 'bucket': 'SG&A', 'driver': 'Fixed', 'controllable': False},
        {'ledger': 'R&D - Development', 'bucket': 'R&D', 'driver': 'Project', 'controllable': True},
        {'ledger': 'R&D - Research', 'bucket': 'R&D', 'driver': 'Project', 'controllable': True},
        {'ledger': 'Depreciation', 'bucket': 'Non-Cash', 'driver': 'Fixed', 'controllable': False},
        {'ledger': 'Interest Expense', 'bucket': 'Financing', 'driver': 'Fixed', 'controllable': False},
        {'ledger': 'Other Income', 'bucket': 'Other', 'driver': 'Variable', 'controllable': False},
        {'ledger': 'Tax Expense', 'bucket': 'Tax', 'driver': 'Calculated', 'controllable': False}
    ])
    db.save_ledger_mapping(ledger_mapping)
    
    mapping = {'market_col': 'Market', 'ledger_col': 'Ledger Account', 'actual_col': 'Actual', 'plan_col': 'Plan', 'forecast_col': 'Forecast'}
    
    for i, month in enumerate(months):
        data = []
        growth_factor = 1 + (i * 0.02)
        for market in markets:
            for ledger in ledgers:
                base = base_values[ledger] * market_multipliers[market] * growth_factor
                data.append({
                    'Market': market,
                    'Ledger Account': ledger,
                    'Actual': round(base * (1 + np.random.uniform(-0.1, 0.15)), 2),
                    'Plan': round(base * (1 + np.random.uniform(-0.05, 0.05)), 2),
                    'Forecast': round(base * (1 + np.random.uniform(-0.08, 0.08)), 2)
                })
        df = pd.DataFrame(data)
        db.save_financial_snapshot(df, month, mapping)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0066CC;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0066CC;
        color: white;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    .export-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

db.init_database()

if not db.get_available_months():
    load_demo_data()

def export_chart_to_png(fig, filename):
    img_bytes = fig.to_image(format="png", width=1200, height=600, scale=2)
    return img_bytes

def export_chart_to_pdf(fig, filename):
    pdf_bytes = fig.to_image(format="pdf", width=1200, height=600)
    return pdf_bytes

def main():
    st.markdown('<p class="main-header">📊 Financial Analytics Tool</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Local-only month-over-month financial analysis • Powered by DuckDB</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio(
            "Select Page",
            ["🏠 Home & Upload", "⚙️ Settings", "📈 Market Scoreboard", "📊 MoM Analysis", 
             "🎯 Pareto Chart", "📉 Trends", "📋 Action Plan"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### Data Status")
        months = db.get_available_months()
        if months:
            st.success(f"✅ {len(months)} months loaded")
            st.caption(f"Latest: {months[0]}")
        else:
            st.warning("⚠️ No data uploaded yet")
    
    if "🏠" in page:
        render_home_page()
    elif "⚙️" in page:
        render_settings_page()
    elif "📈" in page:
        render_scoreboard_page()
    elif "📊 MoM" in page:
        render_mom_page()
    elif "🎯" in page:
        render_pareto_page()
    elif "📉" in page:
        render_trends_page()
    elif "📋" in page:
        render_action_plan_page()

def render_home_page():
    st.header("Upload Financial Report")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Excel file (.xlsx)",
            type=['xlsx'],
            help="Upload your monthly financial report"
        )
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
                
                with st.expander("Preview Data", expanded=True):
                    st.dataframe(df.head(10), use_container_width=True)
                
                mapping = db.get_column_mapping()
                
                if mapping:
                    st.info("Using saved column mapping. Go to Settings to change.")
                    
                    month_tag = st.text_input(
                        "Month Tag (YYYY-MM)",
                        value=datetime.now().strftime("%Y-%m"),
                        help="Enter the month this report represents"
                    )
                    
                    if st.button("💾 Save Snapshot", type="primary"):
                        try:
                            db.save_financial_snapshot(df, month_tag, mapping)
                            st.success(f"✅ Snapshot saved for {month_tag}")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Error saving: {e}")
                else:
                    st.warning("⚠️ Please configure column mapping in Settings first")
                    
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    with col2:
        st.markdown("### Quick Stats")
        months = db.get_available_months()
        
        if months:
            all_data = db.get_all_snapshots()
            latest = all_data[all_data['month_tag'] == months[0]]
            
            total_actual = latest['actual'].sum()
            total_plan = latest['plan'].sum()
            variance = total_actual - total_plan
            var_pct = (variance / abs(total_plan) * 100) if total_plan != 0 else 0
            
            st.metric("Latest Month", months[0])
            st.metric("Net Position", format_currency(total_actual))
            st.metric("vs Plan", f"{var_pct:+.1f}%", delta=format_currency(variance))
            st.metric("Markets", len(latest['market'].unique()))
        else:
            st.info("Upload data to see stats")

def render_settings_page():
    st.header("⚙️ Settings & Configuration")
    
    tab1, tab2 = st.tabs(["Column Mapping", "Ledger Mapping"])
    
    with tab1:
        st.subheader("Column Mapping")
        st.caption("Map your Excel columns to the required fields (one-time setup)")
        
        uploaded_file = st.file_uploader(
            "Upload a sample Excel to detect columns",
            type=['xlsx'],
            key="mapping_file"
        )
        
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            columns = [''] + list(df.columns)
            
            col1, col2 = st.columns(2)
            
            with col1:
                market_col = st.selectbox("Market Column", columns, help="Column containing market/region names")
                ledger_col = st.selectbox("Ledger Column", columns, help="Column containing ledger account names")
                actual_col = st.selectbox("Actual Column", columns, help="Column containing actual values")
            
            with col2:
                plan_col = st.selectbox("Plan Column", columns, help="Column containing plan/budget values")
                forecast_col = st.selectbox("Forecast Column", columns, help="Column containing forecast values")
            
            if all([market_col, ledger_col, actual_col, plan_col, forecast_col]):
                if st.button("💾 Save Column Mapping", type="primary"):
                    db.save_column_mapping(market_col, ledger_col, actual_col, plan_col, forecast_col)
                    st.success("✅ Column mapping saved!")
        
        current_mapping = db.get_column_mapping()
        if current_mapping:
            st.markdown("---")
            st.markdown("**Current Mapping:**")
            st.json(current_mapping)
    
    with tab2:
        st.subheader("Ledger Mapping")
        st.caption("Map ledger accounts to buckets and drivers")
        
        ledger_file = st.file_uploader(
            "Upload ledger mapping Excel",
            type=['xlsx'],
            key="ledger_mapping_file",
            help="Excel with columns: ledger, bucket, driver, controllable"
        )
        
        if ledger_file:
            mapping_df = pd.read_excel(ledger_file)
            st.dataframe(mapping_df, use_container_width=True)
            
            if st.button("💾 Save Ledger Mapping", type="primary"):
                db.save_ledger_mapping(mapping_df)
                st.success("✅ Ledger mapping saved!")
        
        current_ledger = db.get_ledger_mapping()
        if not current_ledger.empty:
            st.markdown("---")
            st.markdown("**Current Ledger Mapping:**")
            st.dataframe(current_ledger, use_container_width=True)

def render_scoreboard_page():
    st.header("📈 Market Scoreboard")
    
    months = db.get_available_months()
    if not months:
        st.warning("No data available. Please upload financial reports first.")
        return
    
    selected_month = st.selectbox("Select Month", months)
    
    all_data = db.get_all_snapshots()
    
    fig = create_market_scoreboard(all_data, selected_month)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Export as PNG"):
            img = export_chart_to_png(fig, "scoreboard")
            st.download_button("Download PNG", img, "market_scoreboard.png", "image/png")
    with col2:
        if st.button("📥 Export as PDF"):
            pdf = export_chart_to_pdf(fig, "scoreboard")
            st.download_button("Download PDF", pdf, "market_scoreboard.pdf", "application/pdf")
    
    st.markdown("---")
    st.subheader("Variance Analysis")
    
    var_fig = create_variance_analysis(all_data, selected_month, by='bucket')
    st.plotly_chart(var_fig, use_container_width=True)

def render_mom_page():
    st.header("📊 Month-over-Month Analysis")
    
    months = db.get_available_months()
    if len(months) < 2:
        st.warning("Need at least 2 months of data for MoM analysis.")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        current_month = st.selectbox("Current Month", months, index=0)
    with col2:
        prev_options = [m for m in months if m < current_month]
        if prev_options:
            previous_month = st.selectbox("Previous Month", prev_options, index=0)
        else:
            st.warning("No previous month available")
            return
    with col3:
        markets = ['All Markets'] + db.get_markets()
        selected_market = st.selectbox("Market Filter", markets)
    
    all_data = db.get_all_snapshots()
    
    market_filter = None if selected_market == 'All Markets' else selected_market
    
    mom_fig = create_mom_comparison(all_data, current_month, previous_month, market_filter)
    st.plotly_chart(mom_fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Export MoM as PNG"):
            img = export_chart_to_png(mom_fig, "mom")
            st.download_button("Download PNG", img, "mom_analysis.png", "image/png")
    
    st.markdown("---")
    st.subheader("Top Movers")
    
    top_n = st.slider("Number of top movers", 5, 20, 10)
    movers_fig = create_top_movers(all_data, current_month, previous_month, top_n)
    st.plotly_chart(movers_fig, use_container_width=True)

def render_pareto_page():
    st.header("🎯 Pareto Analysis")
    
    months = db.get_available_months()
    if not months:
        st.warning("No data available.")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox("Select Month", months)
    with col2:
        metric = st.radio("Variance Type", ["vs Plan", "vs Forecast"], horizontal=True)
    
    all_data = db.get_all_snapshots()
    metric_key = 'variance_plan' if metric == "vs Plan" else 'variance_forecast'
    
    fig = create_pareto_chart(all_data, selected_month, metric_key)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Export Pareto as PNG"):
            img = export_chart_to_png(fig, "pareto")
            st.download_button("Download PNG", img, "pareto_chart.png", "image/png")
    with col2:
        if st.button("📥 Export Pareto as PDF"):
            pdf = export_chart_to_pdf(fig, "pareto")
            st.download_button("Download PDF", pdf, "pareto_chart.pdf", "application/pdf")
    
    st.markdown("---")
    st.caption("The Pareto chart shows which items contribute most to total variance. The 80% line helps identify the vital few.")

def render_trends_page():
    st.header("📉 Trend Analysis")
    
    months = db.get_available_months()
    if len(months) < 2:
        st.warning("Need at least 2 months of data for trend analysis.")
        return
    
    all_data = db.get_all_snapshots()
    
    totals_fig = create_totals_trend(all_data)
    st.plotly_chart(totals_fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Export Trend as PNG"):
            img = export_chart_to_png(totals_fig, "trend")
            st.download_button("Download PNG", img, "trend_chart.png", "image/png")
    
    st.markdown("---")
    st.subheader("Detailed Trends")
    
    col1, col2 = st.columns(2)
    with col1:
        markets = ['All Markets'] + db.get_markets()
        selected_market = st.selectbox("Market", markets)
    with col2:
        metric = st.selectbox("Metric", ['actual', 'plan', 'forecast'])
    
    market_filter = None if selected_market == 'All Markets' else selected_market
    detail_fig = create_trends_chart(all_data, market_filter, metric)
    st.plotly_chart(detail_fig, use_container_width=True)

def render_action_plan_page():
    st.header("📋 Action Plan")
    
    months = db.get_available_months()
    if not months:
        st.warning("No data available.")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox("Select Month", months)
    with col2:
        threshold = st.slider("Variance Threshold (%)", 1, 20, 5)
    
    all_data = db.get_all_snapshots()
    
    action_df = create_action_plan_table(all_data, selected_month, threshold)
    
    if action_df.empty:
        st.success(f"✅ No items exceed {threshold}% variance threshold!")
    else:
        st.markdown(f"### Items exceeding {threshold}% variance")
        
        high_priority = len(action_df[action_df['Priority'] == 'High'])
        medium_priority = len(action_df[action_df['Priority'] == 'Medium'])
        low_priority = len(action_df[action_df['Priority'] == 'Low'])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Items", len(action_df))
        col2.metric("🔴 High Priority", high_priority)
        col3.metric("🟡 Medium Priority", medium_priority)
        col4.metric("🟢 Low Priority", low_priority)
        
        st.markdown("---")
        
        action_df['Actual'] = action_df['Actual'].apply(format_currency)
        action_df['Plan'] = action_df['Plan'].apply(format_currency)
        action_df['Variance'] = action_df['Variance'].apply(format_currency)
        
        st.dataframe(
            action_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Var %": st.column_config.NumberColumn(format="%.1f%%"),
                "Priority": st.column_config.TextColumn(width="small"),
                "Status": st.column_config.TextColumn(width="medium"),
            }
        )
        
        csv = action_df.to_csv(index=False)
        st.download_button(
            "📥 Export Action Plan (CSV)",
            csv,
            f"action_plan_{selected_month}.csv",
            "text/csv"
        )

if __name__ == "__main__":
    main()


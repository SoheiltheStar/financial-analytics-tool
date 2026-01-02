import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

COLORS = {
    'primary': '#0066CC',
    'secondary': '#00A86B',
    'warning': '#FF6B35',
    'danger': '#DC3545',
    'neutral': '#6C757D',
    'positive': '#28A745',
    'negative': '#DC3545',
    'background': '#FAFBFC'
}

PALETTE = ['#0066CC', '#00A86B', '#FF6B35', '#9B59B6', '#F39C12', '#1ABC9C', '#E74C3C', '#3498DB']

def format_currency(value):
    if abs(value) >= 1e6:
        return f"${value/1e6:.1f}M"
    elif abs(value) >= 1e3:
        return f"${value/1e3:.1f}K"
    return f"${value:.0f}"

def create_market_scoreboard(df: pd.DataFrame, selected_month: str) -> go.Figure:
    month_data = df[df['month_tag'] == selected_month].copy()
    
    market_summary = month_data.groupby('market').agg({
        'actual': 'sum',
        'plan': 'sum',
        'forecast': 'sum'
    }).reset_index()
    
    market_summary['vs_plan'] = ((market_summary['actual'] - market_summary['plan']) / abs(market_summary['plan']) * 100).round(1)
    market_summary['vs_forecast'] = ((market_summary['actual'] - market_summary['forecast']) / abs(market_summary['forecast']) * 100).round(1)
    market_summary = market_summary.sort_values('actual', ascending=True)
    
    fig = make_subplots(
        rows=1, cols=3,
        column_widths=[0.5, 0.25, 0.25],
        subplot_titles=('Net Income by Market', 'vs Plan (%)', 'vs Forecast (%)'),
        horizontal_spacing=0.08
    )
    
    colors = [COLORS['positive'] if v >= 0 else COLORS['negative'] for v in market_summary['actual']]
    
    fig.add_trace(
        go.Bar(
            y=market_summary['market'],
            x=market_summary['actual'],
            orientation='h',
            marker_color=colors,
            text=[format_currency(v) for v in market_summary['actual']],
            textposition='outside',
            name='Actual'
        ),
        row=1, col=1
    )
    
    plan_colors = [COLORS['positive'] if v >= 0 else COLORS['negative'] for v in market_summary['vs_plan']]
    fig.add_trace(
        go.Bar(
            y=market_summary['market'],
            x=market_summary['vs_plan'],
            orientation='h',
            marker_color=plan_colors,
            text=[f"{v:+.1f}%" for v in market_summary['vs_plan']],
            textposition='outside',
            name='vs Plan'
        ),
        row=1, col=2
    )
    
    forecast_colors = [COLORS['positive'] if v >= 0 else COLORS['negative'] for v in market_summary['vs_forecast']]
    fig.add_trace(
        go.Bar(
            y=market_summary['market'],
            x=market_summary['vs_forecast'],
            orientation='h',
            marker_color=forecast_colors,
            text=[f"{v:+.1f}%" for v in market_summary['vs_forecast']],
            textposition='outside',
            name='vs Forecast'
        ),
        row=1, col=3
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        title_text=f"Market Scoreboard — {selected_month}",
        title_x=0.5,
        title_font_size=18,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial", size=11)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    fig.update_yaxes(showgrid=False)
    
    return fig

def create_mom_comparison(df: pd.DataFrame, current_month: str, previous_month: str, market: str = None) -> go.Figure:
    current = df[df['month_tag'] == current_month].copy()
    previous = df[df['month_tag'] == previous_month].copy()
    
    if market:
        current = current[current['market'] == market]
        previous = previous[previous['market'] == market]
    
    current_agg = current.groupby('ledger')['actual'].sum().reset_index()
    previous_agg = previous.groupby('ledger')['actual'].sum().reset_index()
    
    merged = current_agg.merge(previous_agg, on='ledger', suffixes=('_current', '_previous'))
    merged['change'] = merged['actual_current'] - merged['actual_previous']
    merged['pct_change'] = ((merged['change'] / abs(merged['actual_previous'])) * 100).round(1)
    merged = merged.sort_values('change', ascending=True)
    
    colors = [COLORS['positive'] if v >= 0 else COLORS['negative'] for v in merged['change']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=merged['ledger'],
        x=merged['change'],
        orientation='h',
        marker_color=colors,
        text=[f"{format_currency(v)} ({p:+.1f}%)" for v, p in zip(merged['change'], merged['pct_change'])],
        textposition='outside'
    ))
    
    market_label = f" — {market}" if market else " — All Markets"
    fig.update_layout(
        title_text=f"Month-over-Month Change: {previous_month} → {current_month}{market_label}",
        title_x=0.5,
        title_font_size=16,
        xaxis_title="Change (USD)",
        height=500,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial", size=11),
        margin=dict(l=200)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5', zeroline=True, zerolinewidth=2, zerolinecolor='#333')
    
    return fig

def create_top_movers(df: pd.DataFrame, current_month: str, previous_month: str, top_n: int = 10) -> go.Figure:
    current = df[df['month_tag'] == current_month].copy()
    previous = df[df['month_tag'] == previous_month].copy()
    
    current['key'] = current['market'] + ' | ' + current['ledger']
    previous['key'] = previous['market'] + ' | ' + previous['ledger']
    
    merged = current[['key', 'actual']].merge(
        previous[['key', 'actual']], 
        on='key', 
        suffixes=('_current', '_previous')
    )
    merged['change'] = merged['actual_current'] - merged['actual_previous']
    
    top_positive = merged.nlargest(top_n, 'change')
    top_negative = merged.nsmallest(top_n, 'change')
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=(f'Top {top_n} Gainers', f'Top {top_n} Decliners'))
    
    fig.add_trace(
        go.Bar(
            y=top_positive['key'],
            x=top_positive['change'],
            orientation='h',
            marker_color=COLORS['positive'],
            text=[format_currency(v) for v in top_positive['change']],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            y=top_negative['key'],
            x=top_negative['change'],
            orientation='h',
            marker_color=COLORS['negative'],
            text=[format_currency(v) for v in top_negative['change']],
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        title_text=f"Top Movers: {previous_month} → {current_month}",
        title_x=0.5,
        title_font_size=16,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial", size=10),
        margin=dict(l=250)
    )
    
    return fig

def create_pareto_chart(df: pd.DataFrame, month: str, metric: str = 'variance_plan') -> go.Figure:
    month_data = df[df['month_tag'] == month].copy()
    
    if metric == 'variance_plan':
        month_data['variance'] = month_data['actual'] - month_data['plan']
        title = "Pareto: Actual vs Plan Variance"
    else:
        month_data['variance'] = month_data['actual'] - month_data['forecast']
        title = "Pareto: Actual vs Forecast Variance"
    
    month_data['key'] = month_data['market'] + ' | ' + month_data['ledger']
    month_data['abs_variance'] = abs(month_data['variance'])
    month_data = month_data.sort_values('abs_variance', ascending=False)
    
    month_data['cumulative'] = month_data['abs_variance'].cumsum()
    total = month_data['abs_variance'].sum()
    month_data['cumulative_pct'] = (month_data['cumulative'] / total * 100)
    
    top_20 = month_data.head(20)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    colors = [COLORS['positive'] if v >= 0 else COLORS['negative'] for v in top_20['variance']]
    
    fig.add_trace(
        go.Bar(
            x=top_20['key'],
            y=top_20['variance'],
            marker_color=colors,
            name='Variance',
            text=[format_currency(v) for v in top_20['variance']],
            textposition='outside'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=top_20['key'],
            y=top_20['cumulative_pct'],
            mode='lines+markers',
            name='Cumulative %',
            line=dict(color=COLORS['primary'], width=2),
            marker=dict(size=6)
        ),
        secondary_y=True
    )
    
    fig.add_hline(y=80, line_dash="dash", line_color="gray", secondary_y=True)
    
    fig.update_layout(
        title_text=f"{title} — {month}",
        title_x=0.5,
        title_font_size=16,
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial", size=10),
        xaxis_tickangle=-45,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_yaxes(title_text="Variance (USD)", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative %", secondary_y=True, range=[0, 105])
    
    return fig

def create_variance_analysis(df: pd.DataFrame, month: str, by: str = 'bucket') -> go.Figure:
    month_data = df[df['month_tag'] == month].copy()
    
    if by == 'bucket' and 'bucket' in month_data.columns:
        group_col = 'bucket'
    else:
        group_col = 'market'
    
    summary = month_data.groupby(group_col).agg({
        'actual': 'sum',
        'plan': 'sum',
        'forecast': 'sum'
    }).reset_index()
    
    summary['var_plan'] = summary['actual'] - summary['plan']
    summary['var_forecast'] = summary['actual'] - summary['forecast']
    summary = summary.sort_values('actual', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=summary[group_col],
        x=summary['plan'],
        name='Plan',
        orientation='h',
        marker_color=COLORS['neutral'],
        opacity=0.6
    ))
    
    fig.add_trace(go.Bar(
        y=summary[group_col],
        x=summary['forecast'],
        name='Forecast',
        orientation='h',
        marker_color=COLORS['warning'],
        opacity=0.6
    ))
    
    fig.add_trace(go.Bar(
        y=summary[group_col],
        x=summary['actual'],
        name='Actual',
        orientation='h',
        marker_color=COLORS['primary']
    ))
    
    fig.update_layout(
        title_text=f"Actual vs Plan vs Forecast by {group_col.title()} — {month}",
        title_x=0.5,
        title_font_size=16,
        barmode='group',
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="Amount (USD)",
        margin=dict(l=150)
    )
    
    return fig

def create_trends_chart(df: pd.DataFrame, market: str = None, metric: str = 'actual') -> go.Figure:
    if market:
        data = df[df['market'] == market].copy()
        title_suffix = f" — {market}"
    else:
        data = df.copy()
        title_suffix = " — All Markets"
    
    if 'bucket' in data.columns and data['bucket'].notna().any():
        trend_data = data.groupby(['month_tag', 'bucket'])[metric].sum().reset_index()
        color_col = 'bucket'
    else:
        trend_data = data.groupby(['month_tag', 'ledger'])[metric].sum().reset_index()
        trend_data = trend_data[trend_data['ledger'].isin(trend_data.groupby('ledger')[metric].sum().nlargest(8).index)]
        color_col = 'ledger'
    
    fig = px.line(
        trend_data,
        x='month_tag',
        y=metric,
        color=color_col,
        markers=True,
        color_discrete_sequence=PALETTE
    )
    
    fig.update_layout(
        title_text=f"Trend Analysis: {metric.title()}{title_suffix}",
        title_x=0.5,
        title_font_size=16,
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial", size=11),
        xaxis_title="Month",
        yaxis_title=f"{metric.title()} (USD)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    
    return fig

def create_totals_trend(df: pd.DataFrame) -> go.Figure:
    trend = df.groupby('month_tag').agg({
        'actual': 'sum',
        'plan': 'sum',
        'forecast': 'sum'
    }).reset_index().sort_values('month_tag')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=trend['month_tag'],
        y=trend['plan'],
        name='Plan',
        mode='lines+markers',
        line=dict(color=COLORS['neutral'], width=2, dash='dash'),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=trend['month_tag'],
        y=trend['forecast'],
        name='Forecast',
        mode='lines+markers',
        line=dict(color=COLORS['warning'], width=2, dash='dot'),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=trend['month_tag'],
        y=trend['actual'],
        name='Actual',
        mode='lines+markers',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title_text="Total Performance Trend: Actual vs Plan vs Forecast",
        title_x=0.5,
        title_font_size=16,
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial", size=11),
        xaxis_title="Month",
        yaxis_title="Net Amount (USD)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    
    return fig

def create_action_plan_table(df: pd.DataFrame, month: str, threshold_pct: float = 5.0) -> pd.DataFrame:
    month_data = df[df['month_tag'] == month].copy()
    
    month_data['var_plan'] = month_data['actual'] - month_data['plan']
    month_data['var_plan_pct'] = ((month_data['var_plan'] / abs(month_data['plan'])) * 100).round(1)
    
    issues = month_data[abs(month_data['var_plan_pct']) > threshold_pct].copy()
    issues = issues.sort_values('var_plan', ascending=True)
    
    issues['Status'] = issues['var_plan'].apply(lambda x: '🔴 Unfavorable' if x < 0 else '🟢 Favorable')
    issues['Priority'] = issues['var_plan_pct'].apply(
        lambda x: 'High' if abs(x) > 15 else ('Medium' if abs(x) > 10 else 'Low')
    )
    issues['Suggested Action'] = issues.apply(
        lambda row: f"Investigate {row['ledger']} in {row['market']}" if row['var_plan'] < 0 
        else f"Document success in {row['ledger']} — {row['market']}", axis=1
    )
    
    result = issues[['market', 'ledger', 'actual', 'plan', 'var_plan', 'var_plan_pct', 'Status', 'Priority', 'Suggested Action']].copy()
    result.columns = ['Market', 'Ledger', 'Actual', 'Plan', 'Variance', 'Var %', 'Status', 'Priority', 'Action']
    
    return result.head(20)


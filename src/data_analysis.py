import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def create_data_visualizations():
    """Create comprehensive data visualizations for movie dataset"""

    # Color scheme matching the dark theme
    colors = {
        'primary': '#8b5cf6',      # Purple accent
        'secondary': '#a855f7',   # Lighter purple
        'success': '#27ae60',     # Green for success
        'danger': '#e74c3c',      # Red for failure
        'warning': '#e67e22',     # Orange
        'info': '#3498db',        # Blue
        'background': '#05050a', # Dark background
        'surface': 'rgba(18, 18, 28, 0.75)', # Surface color
        'text': '#f6f7fb',        # Light text
        'muted': '#c5c7d4'        # Muted text
    }

    # Load data
    data_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'Movies.csv')
    df = pd.read_csv(data_path)

    # Filter Vietnamese movies
    df = df[df['Production Countries'].str.contains('Vietnam', na=False, case=False)]

    # Clean data
    df = df.dropna(subset=['Revenue', 'Budget', 'Runtime', 'Vote Average'])
    df = df[df['Revenue'] > 0]
    df = df[df['Budget'] > 0]
    df = df[df['Vote Average'] > 0]

    # Create success label
    df['ROI'] = df['Revenue'] / df['Budget']
    df['Success'] = ((df['ROI'] >= 1) & (df['Vote Average'] >= 6.5)).astype(int)

    # Process genres
    df['Main_Genre'] = df['Genres'].str.strip('[]').str.split(',').str[0].str.strip(" '")

    # Process release date
    df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
    df['Year'] = df['Release Date'].dt.year

    # Create visualizations with modern styling
    visualizations = {}

    # 1. Budget Distribution - Modern histogram
    fig_budget = px.histogram(
        df, x='Budget', nbins=20,
        title='Phân bố ngân sách sản xuất phim',
        labels={'Budget': 'Ngân sách (USD)', 'count': 'Số lượng phim'},
        color_discrete_sequence=[colors['primary']],
        template='plotly_dark'
    )
    fig_budget.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=colors['text'],
        title_font_color=colors['primary'],
        title_font_size=20,
        showlegend=False,
        bargap=0.1,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    fig_budget.update_traces(
        marker_line_color=colors['secondary'],
        marker_line_width=1,
        opacity=0.8
    )
    visualizations['budget_dist'] = fig_budget.to_html(full_html=False, config={'displayModeBar': False})

    # 2. Vote Average Distribution - Modern histogram
    fig_vote = px.histogram(
        df, x='Vote Average', nbins=15,
        title='Phân bố điểm đánh giá trung bình',
        labels={'Vote Average': 'Điểm đánh giá', 'count': 'Số lượng phim'},
        color_discrete_sequence=[colors['warning']],
        template='plotly_dark'
    )
    fig_vote.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=colors['text'],
        title_font_color=colors['warning'],
        title_font_size=20,
        showlegend=False,
        bargap=0.1,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    fig_vote.update_traces(
        marker_line_color=colors['warning'],
        marker_line_width=1,
        opacity=0.8
    )
    visualizations['vote_dist'] = fig_vote.to_html(full_html=False, config={'displayModeBar': False})

    # 3. Budget vs Revenue Scatter Plot - Enhanced
    fig_scatter = px.scatter(
        df, x='Budget', y='Revenue',
        title='Mối quan hệ giữa Ngân sách và Doanh thu',
        labels={'Budget': 'Ngân sách (USD)', 'Revenue': 'Doanh thu (USD)'},
        color='Success',
        color_discrete_map={0: colors['danger'], 1: colors['success']},
        template='plotly_dark',
        hover_data=['Title']
    )
    fig_scatter.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=colors['text'],
        title_font_color=colors['primary'],
        title_font_size=20,
        legend_title_text='Kết quả',
        legend=dict(
            bgcolor='rgba(18, 18, 28, 0.8)',
            bordercolor=colors['primary'],
            borderwidth=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    fig_scatter.update_traces(
        marker=dict(size=10, line=dict(width=1, color='white')),
        opacity=0.8
    )
    visualizations['budget_revenue'] = fig_scatter.to_html(full_html=False, config={'displayModeBar': False})

    # 4. Genre Distribution - Modern bar chart
    genre_counts = df['Main_Genre'].value_counts().head(10)
    fig_genre = px.bar(
        genre_counts,
        title='Top 10 thể loại phim phổ biến',
        labels={'value': 'Số lượng phim', 'index': 'Thể loại'},
        color_discrete_sequence=[colors['info']],
        template='plotly_dark'
    )
    fig_genre.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=colors['text'],
        title_font_color=colors['info'],
        title_font_size=20,
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    fig_genre.update_traces(
        marker_line_color=colors['secondary'],
        marker_line_width=1,
        opacity=0.8
    )
    visualizations['genre_dist'] = fig_genre.to_html(full_html=False, config={'displayModeBar': False})

    # 5. Yearly Trends - Enhanced dual axis
    yearly_success = df.groupby('Year')['Success'].agg(['count', 'mean']).reset_index()
    yearly_success = yearly_success[yearly_success['count'] >= 2]  # At least 2 movies per year

    fig_yearly = make_subplots(specs=[[{"secondary_y": True}]])

    fig_yearly.add_trace(
        go.Bar(
            x=yearly_success['Year'],
            y=yearly_success['count'],
            name="Số lượng phim",
            marker_color=colors['primary'],
            opacity=0.8
        ),
        secondary_y=False,
    )

    fig_yearly.add_trace(
        go.Scatter(
            x=yearly_success['Year'],
            y=yearly_success['mean']*100,
            name="Tỷ lệ thành công (%)",
            mode='lines+markers',
            marker_color=colors['success'],
            line=dict(width=3, color=colors['success']),
            marker=dict(size=8, line=dict(width=2, color='white'))
        ),
        secondary_y=True,
    )

    fig_yearly.update_layout(
        title_text="Xu hướng sản xuất phim và tỷ lệ thành công theo năm",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=colors['text'],
        title_font_color=colors['primary'],
        title_font_size=20,
        legend=dict(
            bgcolor='rgba(18, 18, 28, 0.8)',
            bordercolor=colors['primary'],
            borderwidth=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    fig_yearly.update_xaxes(title_text="Năm phát hành", gridcolor='rgba(255,255,255,0.1)')
    fig_yearly.update_yaxes(title_text="Số lượng phim", secondary_y=False, gridcolor='rgba(255,255,255,0.1)')
    fig_yearly.update_yaxes(title_text="Tỷ lệ thành công (%)", secondary_y=True, gridcolor='rgba(255,255,255,0.1)')

    visualizations['yearly_trend'] = fig_yearly.to_html(full_html=False, config={'displayModeBar': False})

    # 6. Runtime Distribution - Modern histogram
    fig_runtime = px.histogram(
        df, x='Runtime', nbins=20,
        title='Phân bố thời lượng phim',
        labels={'Runtime': 'Thời lượng (phút)', 'count': 'Số lượng phim'},
        color_discrete_sequence=[colors['secondary']],
        template='plotly_dark'
    )
    fig_runtime.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=colors['text'],
        title_font_color=colors['secondary'],
        title_font_size=20,
        showlegend=False,
        bargap=0.1,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    fig_runtime.update_traces(
        marker_line_color=colors['primary'],
        marker_line_width=1,
        opacity=0.8
    )
    visualizations['runtime_dist'] = fig_runtime.to_html(full_html=False, config={'displayModeBar': False})

    # 7. Vote Analysis - Enhanced scatter
    fig_vote_scatter = px.scatter(
        df, x='Vote Count', y='Vote Average',
        title='Mối quan hệ giữa Số lượng đánh giá và Điểm trung bình',
        labels={'Vote Count': 'Số lượng đánh giá', 'Vote Average': 'Điểm trung bình'},
        color='Success',
        color_discrete_map={0: colors['danger'], 1: colors['success']},
        template='plotly_dark',
        hover_data=['Title']
    )
    fig_vote_scatter.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=colors['text'],
        title_font_color=colors['warning'],
        title_font_size=20,
        legend_title_text='Kết quả',
        legend=dict(
            bgcolor='rgba(18, 18, 28, 0.8)',
            bordercolor=colors['warning'],
            borderwidth=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    fig_vote_scatter.update_traces(
        marker=dict(size=10, line=dict(width=1, color='white')),
        opacity=0.8
    )
    visualizations['vote_analysis'] = fig_vote_scatter.to_html(full_html=False, config={'displayModeBar': False})

    # 8. ROI Distribution - Enhanced histogram
    df['ROI_Percent'] = (df['ROI'] - 1) * 100
    fig_roi = px.histogram(
        df, x='ROI_Percent', nbins=30,
        title='Phân bố tỷ suất lợi nhuận (ROI)',
        labels={'ROI_Percent': 'ROI (%)', 'count': 'Số lượng phim'},
        color='Success',
        color_discrete_map={0: colors['danger'], 1: colors['success']},
        template='plotly_dark'
    )
    fig_roi.add_vline(
        x=0,
        line_dash="dash",
        line_color=colors['warning'],
        annotation_text="Break-even",
        annotation_position="top right",
        annotation_font_color=colors['warning']
    )
    fig_roi.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=colors['text'],
        title_font_color=colors['primary'],
        title_font_size=20,
        legend_title_text='Kết quả',
        legend=dict(
            bgcolor='rgba(18, 18, 28, 0.8)',
            bordercolor=colors['primary'],
            borderwidth=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    fig_roi.update_traces(opacity=0.8)
    visualizations['roi_dist'] = fig_roi.to_html(full_html=False, config={'displayModeBar': False})

    # Dataset statistics
    stats = {
        'total_movies': len(df),
        'success_rate': df['Success'].mean() * 100,
        'avg_budget': df['Budget'].mean(),
        'avg_revenue': df['Revenue'].mean(),
        'avg_vote': df['Vote Average'].mean(),
        'avg_runtime': df['Runtime'].mean(),
        'genres_count': df['Main_Genre'].nunique(),
        'year_range': f"{df['Year'].min()} - {df['Year'].max()}"
    }

    return visualizations, stats
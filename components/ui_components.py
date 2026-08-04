"""
UI Components Module

Provides reusable UI components including cards, charts, filters,
and styling elements for the Blinkit AI Discovery Engine dashboard.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional
from config.constants import BLINKIT_COLORS, BLINKIT_THEME


class BlinkitCard:
    """Blinkit-styled card component for displaying content."""
    
    @staticmethod
    def render(title: str, content: str, icon: str = "📊", color: str = None):
        """
        Render a Blinkit-styled card.
        
        Args:
            title: Card title
            content: Card content
            icon: Card icon
            color: Card color (default: Blinkit primary)
        """
        if color is None:
            color = BLINKIT_COLORS["primary"]
        
        st.markdown(f"""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border-left: 4px solid {color};
        ">
            <h3 style="color: {BLINKIT_COLORS['dark']}; margin-top: 0;">
                {icon} {title}
            </h3>
            <p style="color: {BLINKIT_COLORS['dark']}; line-height: 1.6;">
                {content}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_metric(label: str, value: str, delta: str = None, icon: str = None):
        """
        Render a metric card.
        
        Args:
            label: Metric label
            value: Metric value
            delta: Change indicator
            icon: Metric icon
        """
        icon_display = f"{icon} " if icon else ""
        st.markdown(f"""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        ">
            <div style="font-size: 0.9rem; color: {BLINKIT_COLORS['gray']}; margin-bottom: 0.5rem;">
                {icon_display}{label}
            </div>
            <div style="font-size: 2rem; font-weight: bold; color: {BLINKIT_COLORS['dark']};">
                {value}
            </div>
            {f'<div style="color: {BLINKIT_COLORS["success"]}; font-size: 0.9rem;">{delta}</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)


class BlinkitChart:
    """Blinkit-styled chart components."""
    
    @staticmethod
    def get_color_palette(n: int = 5) -> List[str]:
        """
        Get Blinkit color palette for charts.
        
        Args:
            n: Number of colors needed
            
        Returns:
            List[str]: Color palette
        """
        base_colors = BLINKIT_THEME["chart_colors"]
        return base_colors[:n] + base_colors * (n // len(base_colors) + 1)
    
    @staticmethod
    def create_pie_chart(values: List[int], names: List[str], title: str = ""):
        """
        Create a Blinkit-styled pie chart.
        
        Args:
            values: Data values
            names: Category names
            title: Chart title
        """
        colors = BlinkitChart.get_color_palette(len(names))
        
        fig = go.Figure(data=[go.Pie(
            labels=names,
            values=values,
            marker=dict(colors=colors),
            textinfo='label+percent',
            hole=0.3
        )])
        
        fig.update_layout(
            title=title,
            font=dict(color=BLINKIT_COLORS["dark"]),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def create_bar_chart(x: List[str], y: List[int], title: str = "", color: str = None):
        """
        Create a Blinkit-styled bar chart.
        
        Args:
            x: X-axis values
            y: Y-axis values
            title: Chart title
            color: Bar color
        """
        if color is None:
            color = BLINKIT_COLORS["primary"]
        
        fig = go.Figure(data=[go.Bar(
            x=x,
            y=y,
            marker_color=color,
            text=y,
            textposition='auto',
        )])
        
        fig.update_layout(
            title=title,
            font=dict(color=BLINKIT_COLORS["dark"]),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def create_line_chart(x: List[str], y: List[int], title: str = ""):
        """
        Create a Blinkit-styled line chart.
        
        Args:
            x: X-axis values
            y: Y-axis values
            title: Chart title
        """
        fig = go.Figure(data=[go.Scatter(
            x=x,
            y=y,
            mode='lines+markers',
            line=dict(color=BLINKIT_COLORS["primary"], width=3),
            marker=dict(size=8, color=BLINKIT_COLORS["secondary"])
        )])
        
        fig.update_layout(
            title=title,
            font=dict(color=BLINKIT_COLORS["dark"]),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
        )
        
        st.plotly_chart(fig, use_container_width=True)


class BlinkitFilter:
    """Filter components for dashboard."""
    
    @staticmethod
    def render_date_filter(label: str = "Date Range"):
        """
        Render date range filter.
        
        Args:
            label: Filter label
        """
        st.markdown(f"**{label}**")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        return start_date, end_date
    
    @staticmethod
    def render_source_filter(sources: List[str], label: str = "Data Sources"):
        """
        Render source selection filter.
        
        Args:
            sources: Available sources
            label: Filter label
        """
        st.markdown(f"**{label}**")
        selected_sources = st.multiselect(
            "Select sources",
            sources,
            default=sources
        )
        return selected_sources
    
    @staticmethod
    def render_relevance_filter(label: str = "Relevance Level"):
        """
        Render relevance level filter.
        
        Args:
            label: Filter label
        """
        st.markdown(f"**{label}**")
        relevance_levels = ["HIGH", "MEDIUM", "LOW"]
        selected_relevance = st.multiselect(
            "Select relevance levels",
            relevance_levels,
            default=relevance_levels
        )
        return selected_relevance


class BlinkitProgress:
    """Progress indicators for long-running operations."""
    
    @staticmethod
    def render_stage_progress(current_stage: int, total_stages: int = 9):
        """
        Render pipeline stage progress.
        
        Args:
            current_stage: Current stage number
            total_stages: Total number of stages
        """
        progress = current_stage / total_stages
        st.progress(progress)
        st.markdown(f"**Stage {current_stage}/{total_stages}**")
    
    @staticmethod
    def render_loading_spinner(message: str = "Processing..."):
        """
        Render loading spinner with message.
        
        Args:
            message: Loading message
        """
        with st.spinner(message):
            st.empty()


def render_header(title: str, subtitle: str = ""):
    """
    Render Blinkit-styled page header.
    
    Args:
        title: Page title
        subtitle: Page subtitle
    """
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {BLINKIT_COLORS['primary']} 0%, {BLINKIT_COLORS['secondary']} 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    ">
        <h1 style="margin: 0; font-size: 2rem;">{title}</h1>
        {f'<p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(message: str, icon: str = "📭"):
    """
    Render empty state placeholder.
    
    Args:
        message: Empty state message
        icon: Empty state icon
    """
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 3rem;
        color: {BLINKIT_COLORS['gray']};
    ">
        <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
        <p style="font-size: 1.2rem;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

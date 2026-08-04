"""
Blinkit AI Discovery Engine - Main Application

Production-quality Streamlit application for customer intelligence
and product insights discovery from Blinkit customer feedback.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[0]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from loguru import logger

# Import application modules
from config.settings import get_settings
from config.constants import DASHBOARD_TABS, BLINKIT_THEME, BLINKIT_COLORS
from scrapers.manager import ScraperManager
from database.models import ReviewModel, SourceType
from utils.cleaner import DataCleaner
from ai.relevance_classifier import RelevanceClassifier
from ai.pipeline import AIPipelineManager
from components.page_components import (
    OverviewPage, ThemesPage, SegmentsPage,
    PainPointsPage, RootCausesPage, UnmetNeedsPage, ChatPage
)
from components.ui_components import render_header, BlinkitProgress

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO")


def setup_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Blinkit AI Discovery Engine",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def apply_custom_css():
    """Apply Blinkit-inspired custom CSS styling."""
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {BLINKIT_THEME['background']};
        }}
        
        .stSidebar {{
            background-color: white;
        }}
        
        .stButton>button {{
            background-color: {BLINKIT_COLORS['primary']};
            color: {BLINKIT_COLORS['dark']};
            border: none;
            border-radius: 8px;
            font-weight: bold;
        }}
        
        .stButton>button:hover {{
            background-color: {BLINKIT_COLORS['secondary']};
        }}
        
        .stTextInput>div>div>input,
        .stSelectbox>div>div>select {{
            border-color: {BLINKIT_COLORS['primary']};
        }}
        
        .metric-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "reviews" not in st.session_state:
        st.session_state.reviews = []
    
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = {}
    
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "overview"
    
    if "use_live_data" not in st.session_state:
        st.session_state.use_live_data = False
    
    if "review_count" not in st.session_state:
        st.session_state.review_count = 500


def render_sidebar():
    """Render sidebar with configuration and controls."""
    
    # Analysis Mode
    st.sidebar.subheader("📥 Data Source")
    data_source = st.sidebar.radio(
        "Select Data Source",
        ["📁 Preloaded Dataset", "🌐 Live Data Collection"],
        index=1,
        help="On Streamlit Cloud, choose Live Data Collection. Preloaded files are not committed to the repo."
    )
    
    st.session_state.use_live_data = (data_source == "🌐 Live Data Collection")
    
    # Review Count
    if st.session_state.use_live_data:
        st.sidebar.subheader("🎚 Review Count")
        st.session_state.review_count = st.sidebar.slider(
            "Number of Reviews",
            min_value=50,
            max_value=2000,
            value=500,
            step=50
        )
    else:
        st.sidebar.subheader("📥 Preloaded Dataset")
        st.sidebar.markdown("**1,000 raw reviews** from Google Play")
        st.sidebar.markdown("Preloaded data is stored in the repo")
    
    # Data Sources
    if st.session_state.use_live_data:
        st.sidebar.subheader("🌐 Data Sources")
        enabled_sources = st.sidebar.multiselect(
            "Select Sources",
            ["Google Play", "Reddit", "YouTube", "News", "Apify"],
            default=["Google Play"]
        )
        st.session_state.enabled_sources = enabled_sources
    
    # Analysis Trigger
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Run Full Analysis", type="primary"):
        run_full_analysis()
    
    if st.sidebar.button("Clear Data"):
        st.session_state.reviews = []
        st.session_state.analysis_results = {}
        st.session_state.analysis_complete = False
        st.rerun()


def load_preloaded_data() -> List[ReviewModel]:
    """
    Load 1,760 preloaded reviews balanced across Google Play, Reddit and App Store.
    
    Returns:
        List[ReviewModel]: Loaded reviews
    """
    try:
        logger.info("Loading preloaded data from raw files")
        
        TARGET_PRELOADED = 1760
        PRELOADED_SOURCES = [
            SourceType.GOOGLE_PLAY,
            SourceType.REDDIT,
            SourceType.APP_STORE
        ]
        
        scraper_manager = ScraperManager()
        
        # Collect from the three preloaded sources
        reviews_by_source = scraper_manager.collect_from_all_sources(
            use_live=False,
            enabled_sources=PRELOADED_SOURCES
        )
        
        # Balance across sources: try equal share, fill any shortfall from the largest source
        per_source = TARGET_PRELOADED // len(PRELOADED_SOURCES)
        selected = []
        for source in PRELOADED_SOURCES:
            reviews = reviews_by_source.get(source, [])
            take = min(len(reviews), per_source)
            selected.extend(reviews[:take])
        
        shortfall = TARGET_PRELOADED - len(selected)
        if shortfall > 0:
            for source in sorted(PRELOADED_SOURCES, key=lambda s: len(reviews_by_source.get(s, [])), reverse=True):
                if shortfall <= 0:
                    break
                reviews = reviews_by_source.get(source, [])
                already_taken = min(len(reviews), per_source)
                remaining = reviews[already_taken:]
                take_extra = min(len(remaining), shortfall)
                selected.extend(remaining[:take_extra])
                shortfall -= take_extra
        
        logger.info(f"Loaded {len(selected)} preloaded reviews from {len(PRELOADED_SOURCES)} sources")
        return selected
        
    except Exception as e:
        logger.error(f"Error loading preloaded data: {e}")
        st.error(f"Error loading preloaded data: {e}")
        return []


def collect_live_data() -> List[ReviewModel]:
    """
    Collect live data from APIs.
    
    Returns:
        List[ReviewModel]: Collected reviews
    """
    try:
        logger.info("Collecting live data from APIs")
        
        scraper_manager = ScraperManager()
        
        # Convert source names to SourceType enums
        source_mapping = {
            "Google Play": SourceType.GOOGLE_PLAY,
            "Reddit": SourceType.REDDIT,
            "YouTube": SourceType.YOUTUBE,
            "News": SourceType.NEWS,
            "Apify": SourceType.APIFY
        }
        
        enabled_source_types = [
            source_mapping.get(source) 
            for source in st.session_state.enabled_sources 
            if source in source_mapping
        ]
        
        # Collect live data
        reviews_by_source = scraper_manager.collect_from_all_sources(
            use_live=True,
            count_per_source=st.session_state.review_count // len(enabled_source_types),
            enabled_sources=enabled_source_types
        )
        
        # Combine all reviews and cap to user-selected count
        all_reviews = []
        for source, reviews in reviews_by_source.items():
            all_reviews.extend(reviews)
        
        all_reviews = all_reviews[:st.session_state.review_count]
        
        logger.info(f"Collected {len(all_reviews)} live reviews")
        return all_reviews
        
    except Exception as e:
        logger.error(f"Error collecting live data: {e}")
        st.error(f"Error collecting live data: {e}")
        return []


def run_full_analysis():
    """
    Run the complete analysis pipeline including data collection,
    cleaning, relevance classification, and AI pipeline.
    """
    try:
        logger.info("Starting full analysis pipeline")
        
        # Step 1: Data Collection
        with st.spinner("Collecting data..."):
            if st.session_state.use_live_data:
                reviews = collect_live_data()
            else:
                reviews = load_preloaded_data()
            
            if not reviews:
                st.error("No reviews collected. Select Live Data Collection and check your API tokens are set in Secrets.")
                return
            
            st.session_state.reviews = reviews
        
        # Step 2: Data Cleaning
        with st.spinner("Cleaning data..."):
            cleaner = DataCleaner()
            cleaned_reviews = cleaner.clean_reviews(reviews)
            st.session_state.reviews = cleaned_reviews
        
        # Step 3: Relevance Classification
        with st.spinner("Classifying relevance with AI models..."):
            classifier = RelevanceClassifier()
            classified_reviews = classifier.classify_batch(
                cleaned_reviews,
                use_ai=False  # Keyword-based for speed; AI is used in the 9-stage pipeline
            )
            st.session_state.reviews = classified_reviews
        
        # Step 4: Filter by Relevance
        with st.spinner("Filtering by relevance..."):
            from database.models import RelevanceLevel
            relevant_reviews = classifier.filter_by_relevance(
                classified_reviews,
                RelevanceLevel.LOW  # Keep all preloaded reviews for full analysis
            )
            st.session_state.reviews = relevant_reviews
        
        # Step 5: AI Pipeline (9 stages)
        with st.spinner("Running AI pipeline..."):
            pipeline_manager = AIPipelineManager()
            
            # Show progress
            progress_bar = st.progress(0)
            stage_text = st.empty()
            
            stages = [
                "Theme Extraction",
                "Behavior Analysis",
                "Jobs To Be Done",
                "Customer Segmentation",
                "Pain Point Clustering",
                "Root Cause Analysis",
                "Unmet Needs",
                "Opportunity Discovery",
                "Business Recommendations"
            ]
            
            for i, stage in enumerate(stages):
                stage_text.text(f"Stage {i+1}/9: {stage}")
                progress_bar.progress((i + 1) / len(stages))
            
            # Run full pipeline
            analysis_results = pipeline_manager.run_full_pipeline(relevant_reviews)
            st.session_state.analysis_results = analysis_results
            
            stage_text.text("Pipeline Complete!")
            progress_bar.progress(1.0)
        
        # Mark analysis as complete
        st.session_state.analysis_complete = True
        
        st.success("✅ Analysis Complete!")
        st.rerun()
        
    except Exception as e:
        logger.error(f"Error in analysis pipeline: {e}")
        st.error(f"Error in analysis pipeline: {e}")
        import traceback
        st.error(traceback.format_exc())


def render_main_content():
    """Render main content area with tab navigation."""
    
    # Create tabs
    tabs = [tab["label"] for tab in DASHBOARD_TABS]
    tab_objects = st.tabs(tabs)
    
    # Get current tab index
    current_tab_index = tabs.index(st.session_state.current_tab) if st.session_state.current_tab in tabs else 0
    
    # Render appropriate tab content
    if not st.session_state.analysis_complete:
        # Show empty state if analysis not complete
        with tab_objects[current_tab_index]:
            render_header("🛒 Blinkit AI Discovery Engine", "Customer Intelligence Platform")
            st.markdown("""
            ### Welcome to the Blinkit AI Discovery Engine!
            
            This platform analyzes customer feedback from multiple sources to generate 
            actionable product insights for Product Managers.
            
            **To get started:**
            1. Configure your data source preferences in the sidebar
            2. Click "Run Full Analysis" to collect and analyze customer feedback
            3. Explore insights across 7 different dashboard tabs
            
            **Features:**
            - 📊 Multi-source data collection (Google Play, Reddit, YouTube, News)
            - 🤖 9-stage AI pipeline for comprehensive analysis
            - 🎯 Theme extraction and customer behavior analysis
            - 👤 Customer segmentation and pain point clustering
            - 🚀 Opportunity discovery with business impact assessment
            - 💬 AI-powered chat for natural language queries
            """)
            
            st.info("👈 Configure analysis settings in the sidebar and click 'Run Full Analysis' to begin.")
    
    else:
        # Render tab content based on analysis results
        reviews = st.session_state.reviews
        analysis_results = st.session_state.analysis_results
        
        # Overview Tab
        with tab_objects[0]:
            OverviewPage.render(reviews, analysis_results)
        
        # Themes Tab
        with tab_objects[1]:
            ThemesPage.render(analysis_results.get("themes", []))
        
        # Segments Tab
        with tab_objects[2]:
            SegmentsPage.render(analysis_results.get("segments", []))
        
        # Pain Points Tab
        with tab_objects[3]:
            PainPointsPage.render(analysis_results.get("pain_points", []))
        
        # Root Causes Tab
        with tab_objects[4]:
            RootCausesPage.render(analysis_results.get("root_causes", {}))
        
        # Unmet Needs Tab
        with tab_objects[5]:
            UnmetNeedsPage.render(analysis_results.get("unmet_needs", []))
        
        # Chat Tab
        with tab_objects[6]:
            ChatPage.render()


def main():
    """Main application entry point."""
    
    # Setup
    setup_page_config()
    apply_custom_css()
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main content
    render_main_content()
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: {BLINKIT_COLORS['gray']}; padding: 2rem;">
        <p>Blinkit AI Discovery Engine • Powered by Gemini & Groq</p>
        <p>Customer insights for shopping behavior, category discovery, and product opportunities</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

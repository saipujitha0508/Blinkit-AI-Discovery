"""
Application Constants Module

Contains application-wide constants, Blinkit-specific configurations,
and UI theme settings for the Discovery Engine.
"""

from typing import List, Dict, Any


# ============================================
# BLINKIT APP CONFIGURATION
# ============================================

BLINKIT_PACKAGE_ID = "com.grofers.customerapp"
BLINKIT_APP_NAME = "Blinkit"
BLINKIT_COMPANY = "Grofers"


# ============================================
# DATA SOURCES
# ============================================

DATA_SOURCES = {
    "google_play": {
        "name": "Google Play Store",
        "package_id": BLINKIT_PACKAGE_ID,
        "enabled": True,
        "priority": 1
    },
    "reddit": {
        "name": "Reddit",
        "search_queries": [
            "Blinkit",
            "Blinkit review",
            "Blinkit recommendations",
            "Blinkit customer service",
            "Blinkit delivery",
            "Blinkit grocery",
            "Blinkit search",
            "Blinkit refund",
            "Blinkit vs Zepto",
            "Quick commerce"
        ],
        "enabled": True,
        "priority": 2
    },
    "youtube": {
        "name": "YouTube",
        "search_queries": [
            "Blinkit review",
            "Blinkit vs Zepto",
            "Blinkit grocery",
            "Blinkit delivery"
        ],
        "enabled": True,
        "priority": 3
    },
    "news": {
        "name": "News RSS",
        "sources": [
            "Moneycontrol",
            "Economic Times",
            "Inc42",
            "YourStory",
            "Mint"
        ],
        "enabled": True,
        "priority": 4
    }
}


# ============================================
# RELEVANCE FILTERING
# ============================================

# Topics to ignore (technical issues, not product insights)
IGNORE_TOPICS = [
    "OTP",
    "Login",
    "Payment Failure",
    "App Crash",
    "Network Error",
    "Technical Bugs",
    "Server Down",
    "404 Error",
    "500 Error",
    "Connection Timeout"
]

# Topics to keep (product insights, customer behavior)
KEEP_TOPICS = [
    "Discovery",
    "Recommendations",
    "Shopping Behaviour",
    "Search",
    "Category Exploration",
    "Product Experience",
    "Customer Journey",
    "Cross Sell",
    "Upsell",
    "Product Quality",
    "Freshness",
    "Availability",
    "Pricing",
    "Delivery Experience",
    "Customer Service",
    "App Experience"
]

RELEVANCE_LEVELS = {
    "HIGH": 0.8,
    "MEDIUM": 0.5,
    "LOW": 0.2
}


# ============================================
# CUSTOMER SEGMENTS
# ============================================

CUSTOMER_SEGMENTS = {
    "Routine Grocery Buyer": {
        "description": "Regular shoppers who buy groceries on a fixed schedule",
        "goals": ["Stock up essentials", "Save time", "Get best prices"],
        "pain_points": ["Out of stock items", "Delivery delays", "Price fluctuations"]
    },
    "Impulse Shopper": {
        "description": "Spontaneous buyers who make quick purchases",
        "goals": ["Instant gratification", "Try new products", "Convenience"],
        "pain_points": ["Limited selection", "Slow delivery", "High minimum order"]
    },
    "Health Conscious": {
        "description": "Health-focused shoppers seeking quality products",
        "goals": ["Fresh produce", "Organic options", "Nutritional information"],
        "pain_points": ["Quality inconsistency", "Limited organic range", "Missing nutritional data"]
    },
    "Busy Professional": {
        "description": "Time-constrained professionals valuing efficiency",
        "goals": ["Speed", "Reliability", "Wide selection"],
        "pain_points": ["Delivery delays", "Wrong items", "App complexity"]
    },
    "Student": {
        "description": "Budget-conscious students seeking value",
        "goals": ["Low prices", "Small quantities", "Student discounts"],
        "pain_points": ["High minimum orders", "Limited budget options", "Delivery fees"]
    },
    "Family Shopper": {
        "description": "Parents shopping for family needs",
        "goals": ["Bulk purchases", "Family-friendly products", "Reliable delivery"],
        "pain_points": ["Stock availability", "Delivery windows", "Product variety"]
    },
    "Monthly Stock-up": {
        "description": "Shoppers who buy in bulk monthly",
        "goals": ["Bulk discounts", "Storage-friendly items", "One-time delivery"],
        "pain_points": ["Bulk packaging", "Limited bulk options", "Storage constraints"]
    }
}


# ============================================
# PAIN POINT CATEGORIES
# ============================================

PAIN_POINT_CATEGORIES = {
    "Search": ["Search functionality", "Product discovery", "Filters", "Search results"],
    "Recommendations": ["Personalized suggestions", "Related products", "Cross-sell"],
    "Delivery": ["Delivery time", "Delivery quality", "Delivery slots", "Delivery fees"],
    "Pricing": ["Product prices", "Delivery charges", "Discounts", "Value for money"],
    "Quality": ["Product freshness", "Product quality", "Packaging", "Damaged items"],
    "Freshness": ["Fresh produce quality", "Expiry dates", "Storage conditions"],
    "Availability": ["Out of stock", "Limited selection", "Regional availability"],
    "App Experience": ["App performance", "User interface", "Navigation", "Checkout process"]
}


# ============================================
# BLINKIT UI THEME
# ============================================

BLINKIT_COLORS = {
    "primary": "#FFD700",      # Yellow/Gold
    "secondary": "#FF6B35",    # Orange
    "dark": "#1A1A1A",         # Dark gray
    "light": "#F8F9FA",        # Light gray
    "success": "#2ECC71",      # Green
    "danger": "#E74C3C",       # Red
    "warning": "#F39C12",      # Orange
    "info": "#3498DB",         # Blue
    "white": "#FFFFFF",        # White
    "gray": "#95A5A6"          # Gray
}

BLINKIT_THEME = {
    "background": BLINKIT_COLORS["light"],
    "primary": BLINKIT_COLORS["primary"],
    "secondary": BLINKIT_COLORS["secondary"],
    "text": BLINKIT_COLORS["dark"],
    "border": "#E0E0E0",
    "card_background": "#FFFFFF",
    "chart_colors": [
        BLINKIT_COLORS["primary"],
        BLINKIT_COLORS["secondary"],
        BLINKIT_COLORS["success"],
        BLINKIT_COLORS["info"],
        BLINKIT_COLORS["warning"]
    ]
}


# ============================================
# DASHBOARD TABS
# ============================================

DASHBOARD_TABS = [
    {"id": "overview", "label": "📊 Overview", "icon": "📊"},
    {"id": "themes", "label": "🎯 Themes", "icon": "🎯"},
    {"id": "segments", "label": "👤 Customer Segments", "icon": "👤"},
    {"id": "pain_points", "label": "😣 Pain Points", "icon": "😣"},
    {"id": "root_causes", "label": "🔍 Root Causes", "icon": "🔍"},
    {"id": "unmet_needs", "label": "💡 Unmet Needs", "icon": "💡"},
    {"id": "chat", "label": "🤖 AI Chat", "icon": "🤖"}
]


# ============================================
# AI PIPELINE STAGES
# ============================================

AI_PIPELINE_STAGES = [
    "theme_extraction",
    "behavior_analysis", 
    "jobs_to_be_done",
    "customer_segmentation",
    "pain_point_clustering",
    "root_cause_analysis",
    "unmet_needs",
    "opportunity_discovery",
    "business_recommendations"
]


# ============================================
# BUSINESS METRICS
# ============================================

BUSINESS_METRICS = {
    "category_exploration": {
        "name": "Category Exploration",
        "description": "Percentage of users exploring new categories",
        "target": 0.25  # 25% target
    },
    "basket_size": {
        "name": "Basket Size",
        "description": "Average number of items per order",
        "target": 8.0
    },
    "retention": {
        "name": "Customer Retention",
        "description": "Monthly active customer retention rate",
        "target": 0.80  # 80% target
    },
    "conversion": {
        "name": "Conversion Rate",
        "description": "Browse to purchase conversion rate",
        "target": 0.15  # 15% target
    },
    "monthly_active_users": {
        "name": "Monthly Active Users",
        "description": "Number of active users per month",
        "target": 1000000  # 1M target
    }
}


# ============================================
# EXPORT FORMATS
# ============================================

EXPORT_FORMATS = ["markdown", "csv", "excel", "pdf"]

EXPORT_CONFIG = {
    "markdown": {"extension": ".md", "mime_type": "text/markdown"},
    "csv": {"extension": ".csv", "mime_type": "text/csv"},
    "excel": {"extension": ".xlsx", "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    "pdf": {"extension": ".pdf", "mime_type": "application/pdf"}
}

"""
Page Components Module

Provides page-specific components for each of the 10 dashboard tabs
including Overview, Themes, Customer Behaviour, JTBD, Segments, Pain Points,
Root Causes, Unmet Needs, Opportunities, Business Insights, and AI Chat.
"""

import re
import streamlit as st
from typing import List, Dict, Any, Optional
from database.models import ReviewModel, ThemeModel, CustomerSegmentModel, PainPointModel, OpportunityModel
from components.ui_components import BlinkitCard, BlinkitChart, render_header, render_empty_state


class OverviewPage:
    """Overview page component with key metrics and visualizations."""
    
    @staticmethod
    def render(reviews: List[ReviewModel], analysis_results: Dict[str, Any]):
        """
        Render overview page with key metrics.
        
        Args:
            reviews: List of review models
            analysis_results: Analysis results from pipeline
        """
        render_header("📊 Overview", "Key metrics and insights from customer feedback")
        
        if not reviews:
            render_empty_state("No data available. Run analysis to see overview.")
            return
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            BlinkitCard.render_metric("Total Reviews", str(len(reviews)), icon="📝")
        
        with col2:
            rated = [r.rating for r in reviews if r.rating]
            avg_rating = sum(rated) / len(rated) if rated else 0
            BlinkitCard.render_metric("Average Rating", f"{avg_rating:.1f}/5", icon="⭐")
        
        with col3:
            positive_count = sum(1 for r in reviews if r.rating and r.rating >= 4)
            BlinkitCard.render_metric("Positive Reviews", str(positive_count), icon="😊")
        
        with col4:
            sources = len(set(r.source for r in reviews))
            BlinkitCard.render_metric("Data Sources", str(sources), icon="🌐")
        
        st.markdown("---")
        
        # Sentiment distribution
        st.subheader("Sentiment Distribution")
        sentiments = ["Positive" if r.rating and r.rating >= 4 else "Negative" if r.rating and r.rating <= 2 else "Neutral" for r in reviews]
        sentiment_counts = {s: sentiments.count(s) for s in set(sentiments)}
        BlinkitChart.create_pie_chart(
            list(sentiment_counts.values()),
            list(sentiment_counts.keys()),
            "Sentiment Distribution"
        )
        
        st.markdown("---")
        
        # Source distribution
        st.subheader("Source Distribution")
        source_counts = {}
        for r in reviews:
            raw = r.source.value if hasattr(r.source, "value") else str(r.source)
            source_counts[raw] = source_counts.get(raw, 0) + 1
        source_table = [
            {"Source": k.replace("_", " ").title(), "Review Count": count}
            for k, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        st.table(source_table)
        
        st.markdown("---")
        
        # Rating distribution
        st.subheader("Rating Distribution")
        rating_counts = {
            i: sum(1 for review in reviews if review.rating and int(review.rating) == i)
            for i in range(1, 6)
        }
        BlinkitChart.create_bar_chart(
            [str(r) for r in rating_counts.keys()],
            list(rating_counts.values()),
            title="Rating Distribution"
        )


class ThemesPage:
    """Themes page component with behavioral customer themes."""
    
    @staticmethod
    def render(themes: List[ThemeModel]):
        """
        Render themes page with behavioral theme details.
        
        Args:
            themes: List of theme models
        """
        render_header("🎯 Behavioral Themes", "Customer behaviors that drive or block category exploration")
        
        if not themes:
            render_empty_state("No themes available. Run analysis to see themes.")
            return
        
        # Sort by priority: High > Medium > Low
        priority_order = {"High": 3, "Medium": 2, "Low": 1}
        sorted_themes = sorted(themes, key=lambda t: priority_order.get((t.priority or t.frequency), 0), reverse=True)
        
        for theme in sorted_themes:
            priority = theme.priority or theme.frequency
            
            st.markdown(f"### {theme.theme} ({priority})")
            
            if theme.behavior or theme.summary:
                st.markdown(f"**Behavior:**\n\n{theme.behavior or theme.summary}")
            
            if theme.root_cause:
                st.markdown(f"**Root Cause:**\n\n{theme.root_cause}")
            
            if theme.business_impact:
                st.markdown(f"**Impact on Business Goal:**\n\n{theme.business_impact}")
            
            # Show exactly one highly relevant customer quote at the bottom
            raw_quote = (theme.customer_quotes or theme.representative_quote or "").split("|")[0].split("\n")[0].strip().strip("'\"")
            if raw_quote:
                st.markdown(f'*"{raw_quote}"*')
            
            st.markdown("---")


class BehaviourPage:
    """Customer Behaviour page component with shopping behavior insights."""
    
    @staticmethod
    def render(behavior_analysis: Dict[str, Any]):
        """
        Render customer behaviour page.
        
        Args:
            behavior_analysis: Behavior analysis results
        """
        render_header("🛍 Customer Behaviour", "Shopping patterns and customer journey insights")
        
        if not behavior_analysis or "error" in behavior_analysis:
            render_empty_state("No behavior analysis available. Run analysis to see insights.")
            return
        
        # Display behavior analysis
        BlinkitCard.render(
            "Customer Behavior Analysis",
            behavior_analysis.get("analysis", "No analysis available"),
            icon="🛍"
        )
        
        st.markdown("---")
        st.subheader("Key Questions Answered")
        
        questions = [
            "Why do users repeatedly purchase from the same categories?",
            "What prevents customers from exploring new categories?",
            "Which shopping journeys fail most often?",
            "What categories remain undiscovered?",
            "How do customers currently discover products?"
        ]
        
        for i, question in enumerate(questions, 1):
            st.markdown(f"**{i}. {question}**")


class JTBDPage:
    """Jobs To Be Done page component with JTBD statements."""
    
    @staticmethod
    def render(jtbd_statements: List[str]):
        """
        Render JTBD page with statements.
        
        Args:
            jtbd_statements: List of JTBD statements
        """
        render_header("💼 Jobs To Be Done", "Customer motivations and desired outcomes")
        
        if not jtbd_statements:
            render_empty_state("No JTBD statements available. Run analysis to see insights.")
            return
        
        st.subheader("Customer Jobs To Be Done")
        
        for i, statement in enumerate(jtbd_statements, 1):
            BlinkitCard.render(
                f"Job {i}",
                statement,
                icon="💼"
            )


class SegmentsPage:
    """Customer Segments page component with behavioral segments."""
    
    @staticmethod
    def render(segments: List[CustomerSegmentModel]):
        """
        Render customer segments page.
        
        Args:
            segments: List of customer segment models
        """
        render_header("👤 Customer Segments", "Behavior-based customer segmentation")
        
        if not segments:
            render_empty_state("No segments available. Run analysis to see insights.")
            return
        
        # Show top 5 segments by share of customers
        sorted_segments = sorted(segments, key=lambda s: s.size_percentage if s.size_percentage else 0, reverse=True)[:5]
        
        # Segment details in non-collapsible format
        for segment in sorted_segments:
            pct = segment.size_percentage if segment.size_percentage else 0
            st.markdown(f"### 👤 {segment.segment_name} ({pct}%)")
            st.markdown(f"**Description:** {segment.description}")
            st.markdown(f"**Goals:** {', '.join(segment.goals)}")
            st.markdown(f"**Pain Points:** {', '.join(segment.pain_points)}")
            st.markdown(f"**Shopping Behavior:** {segment.shopping_behavior}")
            st.markdown(f"**Business Opportunity:** {segment.opportunity}")
            st.markdown("---")


class PainPointsPage:
    """Pain Points page component with clustered complaints."""
    
    @staticmethod
    def render(pain_points: List[PainPointModel]):
        """
        Render pain points page.
        
        Args:
            pain_points: List of pain point models
        """
        render_header("😣 Pain Points", "Clustered customer complaints and issues")
        
        if not pain_points:
            render_empty_state("No pain points available. Run analysis to see insights.")
            return
        
        # Show top 3 pain points only
        top_pain_points = sorted(pain_points, key=lambda p: p.frequency, reverse=True)[:3]
        
        st.subheader("Top 3 Pain Points")
        
        for pain_point in top_pain_points:
            st.markdown(f"### {pain_point.category} ({pain_point.severity})")
            st.markdown(f"{pain_point.description}")
            st.markdown(f"**Frequency:** {pain_point.frequency} mentions")
            
            if pain_point.examples:
                st.markdown("**Example complaints:**")
                for example in pain_point.examples:
                    st.markdown(f"- {example}")
            
            st.markdown("---")


class RootCausesPage:
    """Root Causes page component with systemic analysis."""
    
    @staticmethod
    def render(root_causes: Dict[str, Any]):
        """
        Render root causes page.
        
        Args:
            root_causes: Root cause analysis results
        """
        render_header("🔍 Root Causes", "Systemic reasons behind customer problems")
        
        if not root_causes or "error" in root_causes:
            render_empty_state("No root cause analysis available. Run analysis to see insights.")
            return
        
        st.subheader("Root Cause Analysis")
        
        causes = root_causes.get("root_causes", [])
        if isinstance(causes, list):
            for i, item in enumerate(causes, 1):
                st.markdown(f"### {i}. {item.get('pain_point', 'Pain point')}")
                st.markdown(f"{item.get('cause', 'No root cause available')}")
                st.markdown("---")
        elif isinstance(causes, str):
            st.markdown(causes)
        
        st.markdown(f"**Analysis Depth:** {root_causes.get('analysis_depth', 'N/A')}")
        st.markdown(f"**Sample Size:** {root_causes.get('sample_size', 'N/A')} reviews")


class UnmetNeedsPage:
    """Unmet Needs page component with customer needs statements."""
    
    @staticmethod
    def render(unmet_needs: List[Any]):
        """
        Render unmet needs page.
        
        Args:
            unmet_needs: List of unmet needs statements or dictionaries
        """
        render_header("💡 Unmet Needs", "Customer needs not currently met")
        
        # Curated unmet needs from the Blinkit dataset
        if not unmet_needs:
            unmet_needs = [
                {
                    "need": "Users need better cross-category product discovery",
                    "segment": "General",
                    "description": "Customers repeatedly buy the same staples and rarely see relevant new categories. Search-first design only works when they already know what to buy."
                },
                {
                    "need": "Users need reliable product quality and expiry information",
                    "segment": "Quality-Trust Buyers",
                    "description": "Shoppers avoid trying new categories because they fear damaged, expired or wrong items and expect difficult returns."
                },
                {
                    "need": "Users need transparent delivery charges and bundle deals",
                    "segment": "Deal-Seeking Explorers",
                    "description": "High delivery fees and lack of cross-category discounts stop users from adding incremental items from new categories."
                },
                {
                    "need": "Users need a more curated browsing experience",
                    "segment": "Routine Reorderers",
                    "description": "Habitual shoppers have no reason to browse beyond their usual list because the app does not surface timely, relevant alternatives."
                }
            ]
        
        for item in unmet_needs:
            if isinstance(item, dict):
                st.markdown(f"### 💡 {item.get('need', 'Unmet Need')}")
                st.markdown(f"**Segment:** {item.get('segment', 'General')}")
                st.markdown(f"{item.get('description', '')}")
            else:
                st.markdown(f"### 💡 Unmet Need")
                st.markdown(str(item))
            st.markdown("---")


class OpportunitiesPage:
    """Product Opportunities page component with business opportunities."""
    
    @staticmethod
    def render(opportunities: List[OpportunityModel]):
        """
        Render opportunities page.
        
        Args:
            opportunities: List of opportunity models
        """
        render_header("🚀 Product Opportunities", "AI-generated business opportunities")
        
        if not opportunities:
            render_empty_state("No opportunities available. Run analysis to see insights.")
            return
        
        # Opportunity priority chart
        priorities = [o.priority for o in opportunities]
        priority_counts = {p: priorities.count(p) for p in set(priorities)}
        
        BlinkitChart.create_pie_chart(
            list(priority_counts.values()),
            list(priority_counts.keys()),
            "Opportunity Priority Distribution"
        )
        
        st.markdown("---")
        
        # Opportunity cards
        st.subheader("Opportunity Details")
        
        for opportunity in opportunities:
            priority_color = {
                "High": "#E74C3C",
                "Medium": "#F39C12",
                "Low": "#2ECC71"
            }.get(opportunity.priority, "#95A5A6")
            
            with st.expander(f"🚀 {opportunity.problem[:50]}... ({opportunity.priority})"):
                st.markdown(f"**Problem:** {opportunity.problem}")
                st.markdown(f"**Evidence:** {opportunity.evidence}")
                st.markdown(f"**Customer Need:** {opportunity.need}")
                st.markdown(f"**AI Solution:** {opportunity.ai_solution}")
                st.markdown(f"**Business Impact:** {opportunity.business_impact}")
                st.markdown(f"**Confidence:** {opportunity.confidence_score:.1%}")
                
                st.progress(opportunity.confidence_score)


class InsightsPage:
    """Business Insights page component with strategic recommendations."""
    
    @staticmethod
    def render(recommendations: Dict[str, Any]):
        """
        Render business insights page.
        
        Args:
            recommendations: Business recommendations results
        """
        render_header("📈 Business Insights", "Strategic recommendations and impact estimates")
        
        if not recommendations or "error" in recommendations:
            render_empty_state("No business insights available. Run analysis to see insights.")
            return
        
        BlinkitCard.render(
            "Business Recommendations",
            recommendations.get("recommendations", "No recommendations available"),
            icon="📈"
        )
        
        st.markdown("---")
        st.subheader("Impact Framework")
        st.markdown(f"**Impact Estimates:** {recommendations.get('impact_estimates', 'N/A')}")
        st.markdown(f"**Priority Framework:** {recommendations.get('priority_framework', 'N/A')}")


class ChatPage:
    """AI Chat page component for PM questions."""
    
    @staticmethod
    def render():
        """Render AI chat page for PM questions."""
        render_header("🤖 AI Chat", "Ask questions about customer feedback and get data-backed insights")
        
        st.markdown("### 💬 Ask a question")
        
        if not st.session_state.get("analysis_complete"):
            render_empty_state("Run Full Analysis first to enable chat.")
            return
        
        example_questions = [
            "Why don't customers explore new categories?",
            "What are the top customer pain points?",
            "Which customer segment is the largest?",
            "What stops users from trying new products?",
            "How can we increase cross-category purchases?"
        ]
        
        if "chat_input" not in st.session_state:
            st.session_state.chat_input = ""
        
        def set_chat_input():
            selected = st.session_state.get("suggested_question", "")
            if selected:
                st.session_state.chat_input = selected
        
        st.selectbox(
            "Suggested questions",
            [""] + example_questions,
            key="suggested_question",
            on_change=set_chat_input
        )
        
        user_question = st.text_input(
            "Ask a question about customer feedback...",
            key="chat_input"
        )
        
        if st.button("Ask", type="primary") and user_question:
            with st.spinner("Analyzing..."):
                answer = ChatPage._answer_question(
                    user_question,
                    st.session_state.get("reviews", []),
                    st.session_state.get("analysis_results", {})
                )
                
                st.markdown(f"**You:** {user_question}")
                st.markdown(f"**AI:** {answer}")
    
    # Common words to ignore during keyword matching
    _STOPWORDS = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "to", "of", "in", "on", "at", "by", "for", "with", "from", "and",
        "but", "or", "so", "if", "it", "its", "they", "them", "their", "this",
        "that", "these", "those", "i", "you", "we", "he", "she", "us", "me",
        "my", "our", "your", "his", "her", "what", "why", "how", "when", "where",
        "which", "who", "whom", "do", "does", "did", "don", "doesn", "didn",
        "not", "no", "yes", "can", "could", "would", "should", "will", "shall",
        "may", "might", "must", "have", "has", "had", "having", "get", "got"
    }
    
    @staticmethod
    def _extract_words(text: str) -> set:
        """Extract meaningful words from text."""
        words = set(re.findall(r"\w+", text.lower()))
        return words - ChatPage._STOPWORDS
    
    @staticmethod
    def _score(query: str, text: str) -> int:
        """Count overlapping meaningful words."""
        query_words = ChatPage._extract_words(query)
        text_words = ChatPage._extract_words(text)
        if not query_words:
            return 0
        # Score is number of matching words weighted by how much of the question is covered
        matches = query_words & text_words
        return len(matches)
    
    @staticmethod
    def _answer_question(question: str, reviews: List[ReviewModel], analysis_results: Dict[str, Any]) -> str:
        """Return a combined, data-backed answer from the cached analysis."""
        q = question.lower()
        
        # Direct data queries for common PM questions
        segments = analysis_results.get("segments", [])
        pain_points = analysis_results.get("pain_points", [])
        
        if "largest" in q and ("segment" in q or "group" in q):
            if segments:
                largest = max(segments, key=lambda s: s.size_percentage)
                return (
                    f"The largest customer segment is **{largest.segment_name}** "
                    f"({largest.size_percentage}% of users).\n\n"
                    f"{largest.description} {largest.shopping_behavior}"
                )
        
        if ("top" in q or "biggest" in q or "most" in q) and ("pain point" in q or "pain points" in q or "pain" in q):
            if pain_points:
                sorted_pains = sorted(pain_points, key=lambda p: p.frequency, reverse=True)
                lines = ["Top pain points by number of mentions:"]
                for i, p in enumerate(sorted_pains, 1):
                    lines.append(f"{i}. **{p.category}** — {p.frequency} mentions\n   {p.description}")
                return "\n\n".join(lines)
        
        if "top" in q and "theme" in q:
            themes = analysis_results.get("themes", [])
            if themes:
                top = themes[0]
                return (
                    f"The top priority theme is **{top.theme}** ({top.priority}).\n\n"
                    f"{top.behavior or top.summary}"
                )
        
        candidates = []
        
        for theme in analysis_results.get("themes", []):
            text = " ".join(filter(None, [
                theme.theme,
                theme.summary or "",
                theme.behavior or "",
                theme.root_cause or ""
            ]))
            score = ChatPage._score(q, text)
            candidates.append((score, "theme", theme))
        
        for segment in analysis_results.get("segments", []):
            text = " ".join(filter(None, [
                segment.segment_name,
                segment.description,
                segment.shopping_behavior,
                " ".join(segment.pain_points)
            ]))
            score = ChatPage._score(q, text)
            candidates.append((score, "segment", segment))
        
        for pain_point in analysis_results.get("pain_points", []):
            text = " ".join(filter(None, [
                pain_point.category,
                pain_point.description,
                " ".join(pain_point.examples)
            ]))
            score = ChatPage._score(q, text)
            candidates.append((score, "pain point", pain_point))
        
        root_causes_data = analysis_results.get("root_causes", {}).get("root_causes", [])
        if isinstance(root_causes_data, str):
            score = ChatPage._score(q, root_causes_data)
            candidates.append((score, "root cause", {"pain_point": "Root cause", "cause": root_causes_data}))
        elif isinstance(root_causes_data, list):
            for root_cause in root_causes_data:
                if isinstance(root_cause, dict):
                    text = " ".join(filter(None, [
                        root_cause.get("pain_point", ""),
                        root_cause.get("cause", "")
                    ]))
                    score = ChatPage._score(q, text)
                    candidates.append((score, "root cause", root_cause))
                elif isinstance(root_cause, str):
                    score = ChatPage._score(q, root_cause)
                    candidates.append((score, "root cause", {"pain_point": "Root cause", "cause": root_cause}))
        
        # Add direct review snippets as candidates too, so the chat can answer from raw data
        for review in reviews[:200]:  # limit to keep it fast
            score = ChatPage._score(q, review.text)
            if score > 0:
                candidates.append((score, "review", review))
        
        if not candidates or max(c[0] for c in candidates) < 1:
            return (
                "I don't have a direct answer for that in the current analysis. "
                "Try asking about themes, customer segments, pain points, root causes, or specific products/categories."
            )
        
        candidates.sort(key=lambda x: x[0], reverse=True)
        top = candidates[:5]
        
        # Combine the top matching insights into a coherent answer
        parts = ["Based on the data analysis:"]
        seen = set()
        for _, kind, item in top:
            summary = ChatPage._summarize_item(kind, item)
            if summary and summary not in seen:
                parts.append(summary)
                seen.add(summary)
        
        return "\n\n".join(parts)
    
    @staticmethod
    def _summarize_item(kind: str, item: Any) -> str:
        """Generate a concise markdown summary for a matched item."""
        if kind == "theme":
            return (
                f"- **Theme: {item.theme}** — {item.behavior or item.summary} "
                f"{item.business_impact or ''}"
            )
        elif kind == "segment":
            return (
                f"- **Segment: {item.segment_name}** ({item.size_percentage}% of users) — "
                f"{item.description} {item.shopping_behavior}"
            )
        elif kind == "pain point":
            examples = " | ".join(item.examples[:2]) if item.examples else ""
            return (
                f"- **Pain point: {item.category}** ({item.frequency} mentions) — "
                f"{item.description} *Example: {examples}*" if examples
                else f"- **Pain point: {item.category}** ({item.frequency} mentions) — {item.description}"
            )
        elif kind == "root cause":
            return f"- **Root cause for {item.get('pain_point')}** — {item.get('cause')}"
        elif kind == "review":
            return f'- **Customer quote:** "{item.text[:160]}"'
        return ""
    
    @staticmethod
    def _get_relevant_reviews(question: str, reviews: List[ReviewModel]) -> List[str]:
        """Return the top 3 reviews that share the most words with the question."""
        scored = []
        q_words = set(re.findall(r"\w+", question.lower()))
        for review in reviews:
            r_words = set(re.findall(r"\w+", review.text.lower()))
            overlap = len(q_words & r_words)
            if overlap > 0:
                scored.append((overlap, review.text))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in scored[:3]]

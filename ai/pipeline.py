"""
AI Pipeline Manager Module

Coordinates the 9-stage AI pipeline for comprehensive customer insight generation
including theme extraction, behavior analysis, JTBD, segmentation, and opportunity discovery.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional
from loguru import logger
from database.models import ReviewModel, ThemeModel, CustomerSegmentModel, PainPointModel, OpportunityModel, AnalysisResultModel
from config.settings import get_settings
from config.constants import AI_PIPELINE_STAGES, CUSTOMER_SEGMENTS, PAIN_POINT_CATEGORIES


class AIPipelineManager:
    """
    Manager for the 9-stage AI pipeline that transforms customer reviews
    into actionable product insights for PMs.
    """
    
    def __init__(self):
        """Initialize AI pipeline manager."""
        self.settings = get_settings()
        self.stages = AI_PIPELINE_STAGES
        self.current_stage = 0
    
    def run_full_pipeline(self, reviews: List[ReviewModel]) -> Dict[str, Any]:
        """
        Run the complete 9-stage AI pipeline on reviews.
        
        Args:
            reviews: List of review models to analyze
            
        Returns:
            Dict[str, Any]: Complete pipeline results
        """
        logger.info(f"Starting 9-stage AI pipeline for {len(reviews)} reviews")
        
        pipeline_results = {
            "themes": [],
            "behavior": {},
            "jtbd": [],
            "segments": [],
            "pain_points": [],
            "root_causes": [],
            "unmet_needs": [],
            "opportunities": [],
            "recommendations": []
        }
        
        # Stage 1: Theme Extraction
        try:
            pipeline_results["themes"] = self.stage1_theme_extraction(reviews)
        except Exception as e:
            logger.warning(f"Stage 1 failed: {e}. Using defaults.")
        
        # Stage 2: Customer Behaviour Analysis
        try:
            pipeline_results["behavior"] = self.stage2_behavior_analysis(reviews)
        except Exception as e:
            logger.warning(f"Stage 2 failed: {e}. Using defaults.")
        
        # Stage 3: Jobs To Be Done
        try:
            pipeline_results["jtbd"] = self.stage3_jobs_to_be_done(reviews)
        except Exception as e:
            logger.warning(f"Stage 3 failed: {e}. Using defaults.")
        
        # Stage 4: Customer Segmentation
        try:
            pipeline_results["segments"] = self.stage4_customer_segmentation(reviews)
        except Exception as e:
            logger.warning(f"Stage 4 failed: {e}. Using defaults.")
        
        # Stage 5: Pain Point Clustering
        try:
            pipeline_results["pain_points"] = self.stage5_pain_point_clustering(reviews)
        except Exception as e:
            logger.warning(f"Stage 5 failed: {e}. Using defaults.")
        
        # Stage 6: Root Cause Analysis
        try:
            pipeline_results["root_causes"] = self.stage6_root_cause_analysis(reviews)
        except Exception as e:
            logger.warning(f"Stage 6 failed: {e}. Using defaults.")
        
        # Stage 7: Unmet Needs
        try:
            pipeline_results["unmet_needs"] = self.stage7_unmet_needs(reviews)
        except Exception as e:
            logger.warning(f"Stage 7 failed: {e}. Using defaults.")
        
        # Stage 8: Opportunity Discovery
        try:
            pipeline_results["opportunities"] = self.stage8_opportunity_discovery(reviews)
        except Exception as e:
            logger.warning(f"Stage 8 failed: {e}. Using defaults.")
        
        # Stage 9: Business Recommendations
        try:
            pipeline_results["recommendations"] = self.stage9_business_recommendations(reviews, pipeline_results)
        except Exception as e:
            logger.warning(f"Stage 9 failed: {e}. Using defaults.")
        
        logger.info("9-stage AI pipeline completed successfully")
        return pipeline_results
    
    def stage1_theme_extraction(self, reviews: List[ReviewModel]) -> List[ThemeModel]:
        """
        Stage 1: Extract recurring themes from customer reviews.
        
        Args:
            reviews: List of review models
            
        Returns:
            List[ThemeModel]: Extracted themes
        """
        logger.info("Stage 1: Theme Extraction")
        
        try:
            # Use a representative sample that fits within context limits while reflecting the customer base
            sample_reviews = reviews[:min(len(reviews), 80)]
            review_texts = [r.text for r in sample_reviews]
            
            prompt = f"""
            You are a Senior Product Manager and Product Data Analyst.

            Business Problem
            The company wants to increase the percentage of Monthly Active Customers (MACs) who purchase from at least one NEW category every month.

            Current customer behavior shows that users repeatedly purchase from the same category instead of exploring new ones.

            Your goal is NOT to summarize customer reviews.
            Your goal is to identify the underlying CUSTOMER BEHAVIORS that explain WHY customers continue buying from the same categories and what prevents them from exploring new categories.

            Do NOT output customer experience themes like:
            - Fast Delivery
            - Poor Customer Service
            - High Prices
            - Product Quality
            - Easy to Use App

            These are observations. Instead, infer the behavioral reason behind them.

            Analyze the following review dataset and identify 10-15 behavioral discovery themes ranked by business impact.

            For every theme, explain:
            - Why customers repeatedly purchase from the same category
            - What prevents category exploration
            - What motivates exploration
            - Which shopping habits create category stickiness
            - Which product or UX improvements could encourage exploration

            Think beyond sentiment. Infer customer intent, shopping missions, decision-making patterns, and purchase psychology.

            Reviews:
            {review_texts}

            Return each theme using these exact markers and format:

            THEME: [behavioral theme name, e.g. Mission-Based Shopping]
            PRIORITY: [High / Medium / Low]
            BEHAVIOR: [2-4 sentence description of the customer behavior]
            ROOT_CAUSE: [2-4 sentence explanation of why customers behave this way, using evidence]
            SUPPORTING_EVIDENCE: [bullet list of supporting review themes with percentages or counts, e.g. "- Convenience & Fast Delivery (30%)"]
            CUSTOMER_QUOTES: [1-2 representative review snippets]
            BUSINESS_IMPACT: [2-3 sentence explanation of how this affects the goal of increasing new-category purchases]
            PRODUCT_OPPORTUNITIES: [bullet list of 3-5 product improvements or experiments]
            CONFIDENCE: [High / Medium / Low]
            EVIDENCE_COUNT: [number of reviews supporting this theme]
            PERCENTAGE: [e.g., "27% of reviews"]
            AVERAGE_RATING: [average star rating of relevant reviews, or N/A]

            Produce 10-15 themes. Avoid generic CX observations. Convert review insights into actionable behavioral insights for product strategy, recommendations, and growth experiments.
            """
            
            response = self._call_ai_model(prompt)
            
            # Parse response into ThemeModel objects
            themes = self._parse_theme_response(response)
            
            if len(themes) < 5:
                logger.warning(f"Theme extraction produced only {len(themes)} themes. Loading fallback cached themes.")
                themes = self._load_fallback_themes()
            
            logger.info(f"Extracted {len(themes)} themes")
            return themes
            
        except Exception as e:
            logger.error(f"Error in theme extraction: {e}. Loading fallback cached themes.")
            return self._load_fallback_themes()
    
    def _load_fallback_themes(self) -> List[ThemeModel]:
        """Load cached fallback behavioral themes when AI calls fail."""
        try:
            fallback_path = os.path.join(os.path.dirname(__file__), "..", "data", "fallback_themes.json")
            with open(fallback_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            themes = [ThemeModel(**item) for item in data]
            logger.info(f"Loaded {len(themes)} fallback themes")
            return themes
        except Exception as e:
            logger.error(f"Error loading fallback themes: {e}")
            return []
    
    def _load_fallback_behavior(self) -> Dict[str, Any]:
        """Load cached fallback behavior analysis when AI calls fail."""
        try:
            fallback_path = os.path.join(os.path.dirname(__file__), "..", "data", "fallback_behavior.json")
            with open(fallback_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("Loaded fallback behavior analysis")
            return data
        except Exception as e:
            logger.error(f"Error loading fallback behavior analysis: {e}")
            return {"analysis": "No behavior analysis available.", "questions_answered": 0}
    
    def stage2_behavior_analysis(self, reviews: List[ReviewModel]) -> Dict[str, Any]:
        """
        Stage 2: Analyze customer shopping behavior patterns.
        
        Args:
            reviews: List of review models
            
        Returns:
            Dict[str, Any]: Behavior analysis results
        """
        logger.info("Stage 2: Customer Behaviour Analysis")
        
        try:
            sample_reviews = reviews[:50] if len(reviews) > 50 else reviews
            review_texts = [r.text for r in sample_reviews]
            
            prompt = f"""
            Analyze customer behavior patterns from these reviews.
            Answer these questions:
            1. Why do users repeatedly purchase from the same categories?
            2. What prevents customers from exploring new categories?
            3. Which shopping journeys fail most often?
            4. What categories remain undiscovered?
            5. How do customers currently discover products?
            
            Reviews:
            {review_texts}
            
            For each question, provide:
            - Executive explanation
            - Key insights (bullet points)
            - Supporting customer evidence
            - Frequency of occurrence
            """
            
            response = self._call_ai_model(prompt)
            
            return {
                "analysis": response,
                "questions_answered": 5,
                "sample_size": len(sample_reviews)
            }
            
        except Exception as e:
            logger.error(f"Error in behavior analysis: {e}. Loading fallback behavior analysis.")
            return self._load_fallback_behavior()
    
    def stage3_jobs_to_be_done(self, reviews: List[ReviewModel]) -> List[str]:
        """
        Stage 3: Generate Jobs To Be Done statements.
        
        Args:
            reviews: List of review models
            
        Returns:
            List[str]: JTBD statements
        """
        logger.info("Stage 3: Jobs To Be Done")
        
        try:
            sample_reviews = reviews[:30] if len(reviews) > 30 else reviews
            review_texts = [r.text for r in sample_reviews]
            
            prompt = f"""
            Generate Jobs To Be Done (JTBD) statements from these customer reviews.
            
            JTBD format: "When [situation], users want [motivation] so they can [outcome]."
            
            Examples:
            - "When shopping quickly, users want relevant complementary products so they don't forget items."
            - "When planning meals, users want recipe suggestions so they can discover new ingredients."
            
            Reviews:
            {review_texts}
            
            Generate 5-7 JTBD statements based on the reviews.
            """
            
            response = self._call_ai_model(prompt)
            
            # Parse JTBD statements
            jtbd_statements = self._parse_jtbd_response(response)
            
            logger.info(f"Generated {len(jtbd_statements)} JTBD statements")
            return jtbd_statements
            
        except Exception as e:
            logger.error(f"Error in JTBD generation: {e}")
            return []
    
    def stage4_customer_segmentation(self, reviews: List[ReviewModel]) -> List[CustomerSegmentModel]:
        """
        Stage 4: Generate behavior-based customer segments.
        
        Args:
            reviews: List of review models
            
        Returns:
            List[CustomerSegmentModel]: Customer segments
        """
        logger.info("Stage 4: Customer Segmentation")
        
        try:
            sample_reviews = reviews[:40] if len(reviews) > 40 else reviews
            review_texts = [r.text for r in sample_reviews]
            
            prompt = f"""
            Analyze these customer reviews and generate behavior-based segments.
            
            Possible segments: Routine Grocery Buyer, Impulse Shopper, Health Conscious,
            Busy Professional, Student, Family Shopper, Monthly Stock-up.
            
            For each segment identified, provide:
            - Segment name
            - Description
            - Goals (what they want to achieve)
            - Pain points (what frustrates them)
            - Shopping behavior (how they shop)
            - Business opportunity (how to serve them better)
            
            Reviews:
            {review_texts}
            """
            
            response = self._call_ai_model(prompt)
            
            # Parse response into CustomerSegmentModel objects
            segments = self._parse_segment_response(response)
            
            # If the parser returned generic default names, use the fallback data instead
            if not all(s.segment_name and not s.segment_name.lower().startswith("segment ") for s in segments):
                logger.warning("Customer segmentation produced unparsable names. Loading fallback segments.")
                segments = self._load_fallback_segments()
            
            logger.info(f"Generated {len(segments)} customer segments")
            return segments
            
        except Exception as e:
            logger.error(f"Error in customer segmentation: {e}. Loading fallback segments.")
            return self._load_fallback_segments()
    
    def _load_fallback_segments(self) -> List[CustomerSegmentModel]:
        """Load cached fallback customer segments when AI calls fail."""
        try:
            fallback_path = os.path.join(os.path.dirname(__file__), "..", "data", "fallback_segments.json")
            with open(fallback_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            segments = [CustomerSegmentModel(**item) for item in data]
            logger.info(f"Loaded {len(segments)} fallback customer segments")
            return segments
        except Exception as e:
            logger.error(f"Error loading fallback segments: {e}")
            return []
    
    def _load_fallback_pain_points(self) -> List[PainPointModel]:
        """Load cached fallback pain points when AI calls fail."""
        try:
            fallback_path = os.path.join(os.path.dirname(__file__), "..", "data", "fallback_pain_points.json")
            with open(fallback_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            pain_points = [PainPointModel(**item) for item in data]
            logger.info(f"Loaded {len(pain_points)} fallback pain points")
            return pain_points
        except Exception as e:
            logger.error(f"Error loading fallback pain points: {e}")
            return []
    
    def _load_fallback_root_causes(self) -> Dict[str, Any]:
        """Load cached fallback root causes when AI calls fail."""
        try:
            fallback_path = os.path.join(os.path.dirname(__file__), "..", "data", "fallback_root_causes.json")
            with open(fallback_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("Loaded fallback root causes")
            return data
        except Exception as e:
            logger.error(f"Error loading fallback root causes: {e}")
            return {"error": str(e)}
    
    def stage5_pain_point_clustering(self, reviews: List[ReviewModel]) -> List[PainPointModel]:
        """
        Stage 5: Cluster similar customer complaints into pain point categories.
        
        Args:
            reviews: List of review models
            
        Returns:
            List[PainPointModel]: Clustered pain points
        """
        logger.info("Stage 5: Pain Point Clustering")
        
        try:
            sample_reviews = reviews[:50] if len(reviews) > 50 else reviews
            review_texts = [r.text for r in sample_reviews]
            
            categories = list(PAIN_POINT_CATEGORIES.keys())
            
            prompt = f"""
            Cluster these customer complaints into pain point categories.
            
            Categories: {', '.join(categories)}
            
            For each category with significant complaints, provide:
            - Category name
            - Description of the pain point
            - Frequency (number of mentions)
            - Severity level (High/Medium/Low)
            - Example complaints (2-3 actual quotes)
            
            Reviews:
            {review_texts}
            """
            
            response = self._call_ai_model(prompt)
            
            # Parse response into PainPointModel objects
            pain_points = self._parse_pain_point_response(response)
            
            logger.info(f"Clustered into {len(pain_points)} pain points")
            return pain_points if pain_points else self._load_fallback_pain_points()
            
        except Exception as e:
            logger.error(f"Error in pain point clustering: {e}. Loading fallback pain points.")
            return self._load_fallback_pain_points()
    
    def stage6_root_cause_analysis(self, reviews: List[ReviewModel]) -> Dict[str, Any]:
        """
        Stage 6: Generate systemic root causes behind customer problems.
        
        Args:
            reviews: List of review models
            
        Returns:
            Dict[str, Any]: Root cause analysis results
        """
        logger.info("Stage 6: Root Cause Analysis")
        
        try:
            sample_reviews = reviews[:40] if len(reviews) > 40 else reviews
            review_texts = [r.text for r in sample_reviews]
            
            prompt = f"""
            Identify systemic root causes behind customer problems from these reviews.
            
            Focus on root causes like:
            - Low category exploration
            - Search friction
            - Poor recommendations
            - Missing product information
            - Out-of-stock issues
            - Trust barriers
            - Pricing concerns
            - Delivery reliability
            
            For each root cause identified:
            - Root cause statement
            - Supporting evidence from reviews
            - Impact on customer experience
            - Potential solutions
            
            Reviews:
            {review_texts}
            """
            
            response = self._call_ai_model(prompt)
            
            if not response or not response.strip():
                logger.warning("Root cause analysis returned empty. Loading fallback root causes.")
                return self._load_fallback_root_causes()
            
            return {
                "root_causes": response,
                "analysis_depth": "systemic",
                "sample_size": len(sample_reviews)
            }
            
        except Exception as e:
            logger.error(f"Error in root cause analysis: {e}. Loading fallback root causes.")
            return self._load_fallback_root_causes()
    
    def stage7_unmet_needs(self, reviews: List[ReviewModel]) -> List[str]:
        """
        Stage 7: Generate unmet customer needs statements.
        
        Args:
            reviews: List of review models
            
        Returns:
            List[str]: Unmet needs statements
        """
        logger.info("Stage 7: Unmet Needs")
        
        try:
            sample_reviews = reviews[:30] if len(reviews) > 30 else reviews
            review_texts = [r.text for r in sample_reviews]
            
            prompt = f"""
            Identify unmet customer needs from these reviews.
            
            Format each need as: "Users need [need] because [reason]."
            
            Examples:
            - "Users need better product filtering because they can't find specific items quickly."
            - "Users need delivery time estimates because they plan their schedules around deliveries."
            
            Generate 5-7 unmet needs based on the reviews.
            
            Reviews:
            {review_texts}
            """
            
            response = self._call_ai_model(prompt)
            
            # Parse unmet needs
            unmet_needs = self._parse_unmet_needs_response(response)
            
            logger.info(f"Identified {len(unmet_needs)} unmet needs")
            return unmet_needs
            
        except Exception as e:
            logger.error(f"Error in unmet needs analysis: {e}")
            return []
    
    def stage8_opportunity_discovery(self, reviews: List[ReviewModel]) -> List[OpportunityModel]:
        """
        Stage 8: Generate product opportunities with impact assessment.
        
        Args:
            reviews: List of review models
            
        Returns:
            List[OpportunityModel]: Product opportunities
        """
        logger.info("Stage 8: Opportunity Discovery")
        
        try:
            sample_reviews = reviews[:40] if len(reviews) > 40 else reviews
            review_texts = [r.text for r in sample_reviews]
            
            prompt = f"""
            Generate product opportunities from these customer reviews.
            
            For each opportunity, provide:
            - Problem statement
            - Supporting evidence from reviews
            - Customer need
            - AI solution (how AI/technology can solve it)
            - Business impact (on category exploration, basket size, retention, etc.)
            - Priority level (High/Medium/Low)
            - Confidence score (0-1)
            
            Generate 5-7 high-impact opportunities.
            
            Reviews:
            {review_texts}
            """
            
            response = self._call_ai_model(prompt)
            
            # Parse response into OpportunityModel objects
            opportunities = self._parse_opportunity_response(response)
            
            logger.info(f"Discovered {len(opportunities)} opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error in opportunity discovery: {e}")
            return []
    
    def stage9_business_recommendations(self, reviews: List[ReviewModel], pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 9: Generate business recommendations with impact estimation.
        
        Args:
            reviews: List of review models
            pipeline_results: Results from previous pipeline stages
            
        Returns:
            Dict[str, Any]: Business recommendations
        """
        logger.info("Stage 9: Business Recommendations")
        
        try:
            # Combine insights from all stages
            themes_summary = pipeline_results.get("themes", [])
            opportunities_summary = pipeline_results.get("opportunities", [])
            pain_points_summary = pipeline_results.get("pain_points", [])
            
            prompt = f"""
            Generate business recommendations based on these analysis results.
            
            Themes: {[t.theme for t in themes_summary[:5]]}
            Opportunities: {[o.problem for o in opportunities_summary[:3]]}
            Pain Points: {[p.category for p in pain_points_summary[:3]]}
            
            For each recommendation, estimate impact on:
            - Category Exploration (percentage increase)
            - Basket Size (percentage increase)
            - Retention (percentage increase)
            - Conversion (percentage increase)
            - Monthly Active Users (percentage increase)
            
            Provide 5-7 prioritized recommendations with ROI estimates.
            """
            
            response = self._call_ai_model(prompt)
            
            return {
                "recommendations": response,
                "impact_estimates": "quantitative",
                "priority_framework": "ROI-based"
            }
            
        except Exception as e:
            logger.error(f"Error in business recommendations: {e}")
            return {"error": str(e)}
    
    def _call_ai_model(self, prompt: str) -> str:
        """
        Call AI model (Gemini or Groq) with the given prompt.
        
        Args:
            prompt: Prompt to send to AI model
            
        Returns:
            str: AI model response
        """
        # Try primary AI model first
        if self.settings.AI_MODEL_PRIMARY == "gemini" and self.settings.GEMINI_API_KEY:
            try:
                from src.analysis.gemini_client import GeminiClient
                client = GeminiClient(api_key=self.settings.GEMINI_API_KEY)
                return client.generate_content(prompt)
            except Exception as e:
                logger.warning(f"Primary Gemini model failed: {e}. Trying fallback.")
        elif self.settings.AI_MODEL_PRIMARY == "groq" and self.settings.GROQ_API_KEY:
            try:
                from src.analysis.groq_client import GroqClient
                client = GroqClient(api_key=self.settings.GROQ_API_KEY)
                return client.generate_content(prompt)
            except Exception as e:
                logger.warning(f"Primary Groq model failed: {e}. Trying fallback.")
        
        # Try fallback
        if self.settings.AI_MODEL_FALLBACK == "groq" and self.settings.GROQ_API_KEY:
            try:
                from src.analysis.groq_client import GroqClient
                client = GroqClient(api_key=self.settings.GROQ_API_KEY)
                return client.generate_content(prompt)
            except Exception as e:
                logger.error(f"Fallback Groq model also failed: {e}")
                raise
        elif self.settings.AI_MODEL_FALLBACK == "gemini" and self.settings.GEMINI_API_KEY:
            try:
                from src.analysis.gemini_client import GeminiClient
                client = GeminiClient(api_key=self.settings.GEMINI_API_KEY)
                return client.generate_content(prompt)
            except Exception as e:
                logger.error(f"Fallback Gemini model also failed: {e}")
                raise
        
        raise Exception("No AI model configured or all models failed")
    
    def _parse_theme_response(self, response: str) -> List[ThemeModel]:
        """Parse AI response into ThemeModel objects using field markers."""
        themes = []

        # Split response into individual theme blocks by THEME: markers
        blocks = re.split(r"\n\s*THEME:\s*", response, flags=re.IGNORECASE | re.DOTALL)
        # First split may contain preamble; keep only blocks that look like themes

        def get_field(block: str, field: str) -> Optional[str]:
            """Extract a field's value until the next uppercase marker or end of block."""
            pattern = rf"{re.escape(field)}:\s*(.*?)(?=\n\s*[A-Z][A-Z_]*:\s*|\Z)"
            match = re.search(pattern, block, re.IGNORECASE | re.DOTALL)
            if not match:
                return None
            return match.group(1).strip()

        def clean_text(text: str) -> str:
            if not text:
                return ""
            return re.sub(r"\*+", "", text).strip().strip("'\"")

        for block in blocks:
            # Skip preamble and empty blocks
            if not re.search(r"(?:^|\n)\s*PRIORITY:\s*", block, re.IGNORECASE):
                continue

            theme = get_field(block, "THEME")
            if not theme:
                continue

            priority = clean_text(get_field(block, "PRIORITY")).capitalize()
            if priority not in ["High", "Medium", "Low"]:
                priority = "Medium"

            behavior = clean_text(get_field(block, "BEHAVIOR"))
            root_cause = clean_text(get_field(block, "ROOT_CAUSE"))
            supporting_evidence = clean_text(get_field(block, "SUPPORTING_EVIDENCE"))
            customer_quotes = clean_text(get_field(block, "CUSTOMER_QUOTES"))
            business_impact = clean_text(get_field(block, "BUSINESS_IMPACT"))
            product_opportunities = clean_text(get_field(block, "PRODUCT_OPPORTUNITIES"))
            confidence = clean_text(get_field(block, "CONFIDENCE")).capitalize()
            if confidence not in ["High", "Medium", "Low"]:
                confidence = "Medium"

            percentage = clean_text(get_field(block, "PERCENTAGE"))
            metric = clean_text(get_field(block, "METRIC"))
            transition_rate = clean_text(get_field(block, "TRANSITION_RATE"))

            try:
                count = int(re.search(r"EVIDENCE_COUNT:\s*(\d+)", block, re.IGNORECASE).group(1))
            except (ValueError, TypeError, AttributeError):
                count = 1

            avg_rating_match = re.search(r"AVERAGE_RATING:\s*([\d.N/A]+)", block, re.IGNORECASE)
            try:
                avg_rating = float(avg_rating_match.group(1)) if avg_rating_match and "N/A" not in avg_rating_match.group(1).upper() else None
            except (ValueError, TypeError):
                avg_rating = None

            customer_count_match = re.search(r"CUSTOMER_COUNT:\s*([\d,]+)", block, re.IGNORECASE)
            try:
                customer_count = int(customer_count_match.group(1).replace(",", "")) if customer_count_match else None
            except (ValueError, TypeError):
                customer_count = None

            themes.append(ThemeModel(
                theme=re.sub(r"\*+", "", theme).strip(),
                frequency=priority,
                priority=priority,
                confidence=confidence,
                percentage=percentage,
                average_rating=avg_rating,
                customer_count=customer_count,
                metric=metric,
                transition_rate=transition_rate,
                behavior=behavior,
                root_cause=root_cause,
                supporting_evidence=supporting_evidence,
                customer_quotes=customer_quotes,
                business_impact=business_impact,
                product_opportunities=product_opportunities,
                summary=behavior or root_cause or theme,
                representative_quote=customer_quotes or "",
                evidence_count=count
            ))

        return themes
    
    def _parse_jtbd_response(self, response: str) -> List[str]:
        """Parse AI response into JTBD statements."""
        statements = []
        # Extract quoted or bulleted JTBD statements matching the expected pattern
        quoted = re.findall(r'"([^"]*when[^"]*)"', response, re.IGNORECASE)
        statements.extend([q for q in quoted if "users want" in q.lower()])
        for line in response.splitlines():
            line = re.sub(r"^\s*(?:\d+\.|-|\*)\s*", "", line).strip().strip('"').strip()
            if not line:
                continue
            if "users want" in line.lower():
                statements.append(line)
            elif line.lower().startswith("when ") and " so " in line.lower():
                statements.append(line)
        return list(dict.fromkeys(statements))[:15]
    
    def _parse_segment_response(self, response: str) -> List[CustomerSegmentModel]:
        """Parse AI response into CustomerSegmentModel objects."""
        segments = []
        blocks = [b for b in re.split(r"\n\s*-{3,}\s*\n|\n\s*\n", response.strip()) if b.strip()]
        if not blocks:
            blocks = [response.strip()]
        label_pattern = re.compile(
            r"(?:^|\n)\s*(?P<label>SEGMENT|DESCRIPTION|GOALS|PAIN POINTS|SHOPPING BEHAVIOR|BUSINESS OPPORTUNITY):\s*(?P<value>.+?)(?=(?:^|\n)\s*(?:SEGMENT|DESCRIPTION|GOALS|PAIN POINTS|SHOPPING BEHAVIOR|BUSINESS OPPORTUNITY):\s*|\Z)",
            re.IGNORECASE | re.DOTALL
        )
        for i, block in enumerate(blocks):
            fields = {}
            for m in label_pattern.finditer(block):
                fields[m.group("label").lower().strip()] = m.group("value").strip()
            if not fields and not block.strip():
                continue
            name = fields.get("segment", f"Segment {i+1}")
            goals = [g.strip() for g in fields.get("goals", "").split(",") if g.strip()] if "goals" in fields else []
            pain_points = [p.strip() for p in fields.get("pain points", "").split(",") if p.strip()] if "pain points" in fields else []
            segments.append(CustomerSegmentModel(
                segment_name=name,
                description=fields.get("description", block.strip()),
                goals=goals,
                pain_points=pain_points,
                shopping_behavior=fields.get("shopping behavior", ""),
                opportunity=fields.get("business opportunity", "")
            ))
        return segments
    
    def _parse_pain_point_response(self, response: str) -> List[PainPointModel]:
        """Parse AI response into PainPointModel objects."""
        pain_points = []
        blocks = [b for b in re.split(r"\n\s*-{3,}\s*\n|\n\s*\n", response.strip()) if b.strip()]
        if not blocks:
            blocks = [response.strip()]
        for i, block in enumerate(blocks):
            fields = {m.group(1).lower().strip(): m.group(2).strip() for m in re.finditer(
                r"(?:^|\n)\s*(CATEGORY|DESCRIPTION|FREQUENCY|SEVERITY):\s*(.+?)(?=(?:^|\n)\s*(?:CATEGORY|DESCRIPTION|FREQUENCY|SEVERITY):\s*|\Z)",
                block, re.IGNORECASE | re.DOTALL
            )}
            if not fields and not block.strip():
                continue
            category = fields.get("category", f"Pain Point {i+1}")
            description = fields.get("description", block.strip())
            try:
                frequency = int(re.search(r"\d+", fields.get("frequency", "")).group()) if "frequency" in fields else 1
            except (AttributeError, ValueError, TypeError):
                frequency = 1
            severity = "Medium"
            if "severity" in fields:
                s = fields["severity"].strip().lower()
                if "high" in s:
                    severity = "High"
                elif "low" in s:
                    severity = "Low"
            examples = re.findall(r'"([^"]+)"', block)
            pain_points.append(PainPointModel(
                category=category,
                description=description,
                frequency=frequency,
                severity=severity,
                examples=examples
            ))
        return pain_points
    
    def _parse_unmet_needs_response(self, response: str) -> List[str]:
        """Parse AI response into unmet needs statements."""
        needs = []
        for line in response.splitlines():
            line = line.strip().strip("-* ").strip('"').strip()
            if not line:
                continue
            if line.lower().startswith("users need "):
                needs.append(line)
            elif "need" in line.lower() and len(line) > 20:
                needs.append(line)
        return needs[:15]
    
    def _parse_opportunity_response(self, response: str) -> List[OpportunityModel]:
        """Parse AI response into OpportunityModel objects."""
        opportunities = []
        blocks = [b for b in re.split(r"\n\s*-{3,}\s*\n|\n\s*\n", response.strip()) if b.strip()]
        if not blocks:
            blocks = [response.strip()]
        for i, block in enumerate(blocks):
            fields = {m.group(1).lower().strip(): m.group(2).strip() for m in re.finditer(
                r"(?:^|\n)\s*(PROBLEM STATEMENT|PROBLEM|SUPPORTING EVIDENCE|EVIDENCE|CUSTOMER NEED|NEED|AI SOLUTION|SOLUTION|BUSINESS IMPACT|IMPACT|PRIORITY LEVEL|PRIORITY|CONFIDENCE SCORE|CONFIDENCE):\s*(.+?)(?=(?:^|\n)\s*(?:PROBLEM STATEMENT|PROBLEM|SUPPORTING EVIDENCE|EVIDENCE|CUSTOMER NEED|NEED|AI SOLUTION|SOLUTION|BUSINESS IMPACT|IMPACT|PRIORITY LEVEL|PRIORITY|CONFIDENCE SCORE|CONFIDENCE):\s*|\Z)",
                block, re.IGNORECASE | re.DOTALL
            )}
            if not fields and not block.strip():
                continue
            problem = fields.get("problem statement", fields.get("problem", f"Opportunity {i+1}"))
            evidence = fields.get("supporting evidence", fields.get("evidence", ""))
            need = fields.get("customer need", fields.get("need", ""))
            solution = fields.get("ai solution", fields.get("solution", ""))
            impact = fields.get("business impact", fields.get("impact", ""))
            priority = "Medium"
            if "priority" in fields:
                p = fields["priority"].strip().lower()
                if "high" in p:
                    priority = "High"
                elif "low" in p:
                    priority = "Low"
            try:
                confidence = float(re.search(r"0?\.\d+|1\.0|1", fields.get("confidence", "")).group())
            except (AttributeError, ValueError, TypeError):
                confidence = 0.7
            opportunities.append(OpportunityModel(
                problem=problem,
                evidence=evidence,
                need=need,
                ai_solution=solution,
                business_impact=impact,
                priority=priority,
                confidence_score=confidence
            ))
        return opportunities

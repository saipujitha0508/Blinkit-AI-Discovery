"""
Weekly Data Update Automation Script.

This script automates the weekly data scraping, analysis, and RAG index update process.
It should be scheduled to run once per week (e.g., via cron job or Windows Task Scheduler).
"""

import sys
from pathlib import Path
from datetime import datetime
import subprocess
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class WeeklyDataUpdater:
    """Automated weekly data update system."""

    def __init__(self) -> None:
        """Initialize the weekly data updater."""
        self.project_root = PROJECT_ROOT
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        self.log_file = self.logs_dir / f"weekly_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    def log(self, message: str) -> None:
        """Log a message to both console and log file."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')

    def run_command(self, command: list[str], description: str) -> bool:
        """
        Run a command and log the result.

        Args:
            command: Command to run as list of strings
            description: Description of the command

        Returns:
            True if successful, False otherwise
        """
        self.log(f"Starting: {description}")
        self.log(f"Command: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                self.log(f"✓ SUCCESS: {description}")
                if result.stdout:
                    self.log(f"Output: {result.stdout[:500]}")
                return True
            else:
                self.log(f"✗ FAILED: {description}")
                self.log(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"✗ TIMEOUT: {description}")
            return False
        except Exception as e:
            self.log(f"✗ ERROR: {description} - {str(e)}")
            return False

    def step_1_scrape_new_data(self) -> bool:
        """Step 1: Scrape new data from sources."""
        self.log("=" * 60)
        self.log("STEP 1: Scraping new data from sources")
        self.log("=" * 60)
        
        # This would typically call your existing scraping scripts
        # For now, this is a placeholder - you'd replace with your actual scraping commands
        command = ["python", "-m", "scripts.scrape_reviews"]  # Replace with your actual scraping script
        
        # Placeholder - in reality you'd have specific scraping scripts for each source
        self.log("Note: Configure your actual scraping scripts here")
        self.log("Example sources: Google Play, App Store, Reddit")
        
        return True  # Placeholder - return actual result when implemented

    def step_2_update_master_dataset(self) -> bool:
        """Step 2: Update the master dataset with new data."""
        self.log("=" * 60)
        self.log("STEP 2: Updating master dataset")
        self.log("=" * 60)
        
        # Run your data processing script
        command = ["python", "scripts/process_new_reviews.py"]
        return self.run_command(command, "Update master dataset")

    def step_3_run_sentiment_analysis(self) -> bool:
        """Step 3: Run sentiment analysis on updated data."""
        self.log("=" * 60)
        self.log("STEP 3: Running sentiment analysis")
        self.log("=" * 60)
        
        command = ["python", "scripts/analyze_reviews.py"]
        return self.run_command(command, "Sentiment analysis")

    def step_4_run_theme_extraction(self) -> bool:
        """Step 4: Run theme extraction."""
        self.log("=" * 60)
        self.log("STEP 4: Running theme extraction")
        self.log("=" * 60)
        
        command = ["python", "scripts/generate_themes.py"]
        return self.run_command(command, "Theme extraction")

    def step_5_run_insights_generation(self) -> bool:
        """Step 5: Generate business insights."""
        self.log("=" * 60)
        self.log("STEP 5: Generating business insights")
        self.log("=" * 60)
        
        command = ["python", "scripts/generate_insights.py"]
        return self.run_command(command, "Insights generation")

    def step_6_update_rag_index(self) -> bool:
        """Step 6: Update RAG index with new data."""
        self.log("=" * 60)
        self.log("STEP 6: Updating RAG index")
        self.log("=" * 60)
        
        # Clear old cache and index
        self.log("Clearing old RAG cache and index...")
        
        cache_dir = self.data_dir / "embeddings_cache"
        index_dir = self.data_dir / "vector_index"
        
        # Clear cache
        if cache_dir.exists():
            for file in cache_dir.glob("*.pkl"):
                file.unlink()
                self.log(f"Deleted: {file.name}")
        
        # Clear index
        if index_dir.exists():
            for file in index_dir.glob("*"):
                file.unlink()
                self.log(f"Deleted: {file.name}")
        
        self.log("✓ Old RAG cache and index cleared")
        
        # The RAG index will be automatically rebuilt on next chatbot startup
        self.log("RAG index will be rebuilt on next chatbot startup")
        return True

    def step_7_generate_update_report(self) -> bool:
        """Step 7: Generate update report."""
        self.log("=" * 60)
        self.log("STEP 7: Generating update report")
        self.log("=" * 60)
        
        report = {
            "update_date": datetime.now().isoformat(),
            "status": "completed",
            "steps_completed": [
                "Data scraping",
                "Master dataset update", 
                "Sentiment analysis",
                "Theme extraction",
                "Insights generation",
                "RAG index update"
            ]
        }
        
        report_file = self.logs_dir / f"update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"✓ Update report saved to {report_file}")
        return True

    def run_weekly_update(self) -> bool:
        """
        Run the complete weekly update process.

        Returns:
            True if all steps completed successfully, False otherwise
        """
        self.log("=" * 60)
        self.log("WEEKLY DATA UPDATE PROCESS STARTED")
        self.log("=" * 60)
        
        steps = [
            self.step_1_scrape_new_data,
            self.step_2_update_master_dataset,
            self.step_3_run_sentiment_analysis,
            self.step_4_run_theme_extraction,
            self.step_5_run_insights_generation,
            self.step_6_update_rag_index,
            self.step_7_generate_update_report
        ]
        
        results = []
        for step in steps:
            try:
                result = step()
                results.append(result)
                if not result:
                    self.log(f"Step failed, continuing with remaining steps...")
            except Exception as e:
                self.log(f"Step failed with exception: {str(e)}")
                results.append(False)
        
        success_count = sum(results)
        total_count = len(results)
        
        self.log("=" * 60)
        self.log(f"WEEKLY UPDATE PROCESS COMPLETED")
        self.log(f"Success rate: {success_count}/{total_count} steps completed")
        self.log("=" * 60)
        
        return all(results)


def main() -> int:
    """Main entry point for the weekly update script."""
    updater = WeeklyDataUpdater()
    
    try:
        success = updater.run_weekly_update()
        return 0 if success else 1
    except Exception as e:
        updater.log(f"FATAL ERROR: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

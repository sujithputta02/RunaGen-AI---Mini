"""
Automated Pipeline Scheduler
Runs ELT pipeline on schedule to keep data fresh
"""
import schedule
import time
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from etl.run_pipeline import run_bronze_layer, run_silver_layer, run_gold_layer, show_pipeline_stats
from ml.train_models_production import main as train_models
from utils.logger import setup_logger

logger = setup_logger('scheduler')

class PipelineScheduler:
    def __init__(self):
        self.is_running = False
    
    def run_full_pipeline(self, mode='priority'):
        """Run complete ELT pipeline"""
        if self.is_running:
            logger.warning("Pipeline already running, skipping this execution")
            return
        
        try:
            self.is_running = True
            logger.info(f"🚀 Starting scheduled pipeline run at {datetime.now()}")
            logger.info(f"Mode: {mode}")
            
            # Run Bronze layer (Extract new data)
            logger.info("Step 1/4: Extracting data (Bronze layer)")
            run_bronze_layer(target_count=2000, mode=mode)
            
            # Run Silver layer (Transform)
            logger.info("Step 2/4: Transforming data (Silver layer)")
            run_silver_layer()
            
            # Run Gold layer (Load features)
            logger.info("Step 3/4: Creating features (Gold layer)")
            run_gold_layer()
            
            # Step 4/4: Retrain Models with fresh data
            logger.info("Step 4/4: Retraining ML models with fresh data")
            training_success = train_models()
            if training_success:
                logger.info("✅ Models retrained successfully")
            else:
                logger.error("❌ Model retraining failed")
            
            # Show stats
            show_pipeline_stats()
            
            logger.info(f"✅ Pipeline completed successfully at {datetime.now()}")
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
        
        finally:
            self.is_running = False
    
    def run_incremental_update(self, mode='priority'):
        """Run incremental update (only new data)"""
        if self.is_running:
            logger.warning("Pipeline already running, skipping incremental update")
            return
        
        try:
            self.is_running = True
            logger.info(f"🔄 Starting incremental update at {datetime.now()}")
            
            # Only fetch new data and transform (smaller batch)
            run_bronze_layer(target_count=500, mode=mode)
            run_silver_layer()
            run_gold_layer()
            
            # Retrain models even on incremental updates to keep them fresh
            logger.info("Retraining models after incremental update...")
            train_models()
            
            logger.info(f"✅ Incremental update completed at {datetime.now()}")
            
        except Exception as e:
            logger.error(f"❌ Incremental update failed: {e}", exc_info=True)
        
        finally:
            self.is_running = False
    
    def start_scheduler(self, mode='production', collection_mode='priority'):
        """
        Start the scheduler
        """
        logger.info(f"Starting scheduler in {mode} mode")
        logger.info(f"Collection mode: {collection_mode}")
        
        if mode == 'production':
            schedule.every().day.at("02:00").do(lambda: self.run_full_pipeline(mode=collection_mode))
            schedule.every(6).hours.do(lambda: self.run_incremental_update(mode=collection_mode))
            logger.info("Schedule: Full pipeline daily at 2 AM, incremental every 6 hours")
        
        elif mode == 'development':
            schedule.every(12).hours.do(lambda: self.run_full_pipeline(mode=collection_mode))
            logger.info("Schedule: Full pipeline every 12 hours")
        
        elif mode == 'testing':
            schedule.every(1).hours.do(lambda: self.run_full_pipeline(mode=collection_mode))
            logger.info("Schedule: Full pipeline every hour (testing mode)")
        
        # Run immediately on startup
        logger.info("Running initial pipeline execution...")
        self.run_full_pipeline(mode=collection_mode)
        
        # Keep running
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Automated ELT Pipeline Scheduler')
    parser.add_argument('--mode', choices=['production', 'development', 'testing'],
                       default='production', help='Scheduler mode')
    parser.add_argument('--collection', choices=['priority', 'full', 'category'],
                       default='priority', help='Collection mode')
    parser.add_argument('--run-once', action='store_true', help='Run pipeline once and exit')
    
    args = parser.parse_args()
    scheduler = PipelineScheduler()
    
    if args.run_once:
        logger.info("Running pipeline once...")
        scheduler.run_full_pipeline(mode=args.collection)
    else:
        scheduler.start_scheduler(mode=args.mode, collection_mode=args.collection)

if __name__ == "__main__":
    main()

"""
Automated Pipeline Scheduler
"""
import schedule
import time
from datetime import datetime
import sys
import os

# Set Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from etl.run_pipeline import run_bronze_layer, run_silver_layer, run_gold_layer, show_pipeline_stats
from ml.train_models_production import main as train_models
from utils.logger import setup_logger

logger = setup_logger('scheduler')

class PipelineScheduler:
    def __init__(self):
        self.is_running = False
    
    def run_full_pipeline(self, mode='priority'):
        if self.is_running:
            logger.warning("Already running, skipping")
            return
        try:
            self.is_running = True
            logger.info(f"Starting pipeline at {datetime.now()}")
            run_bronze_layer(total_target=2000, mode=mode)
            run_silver_layer()
            run_gold_layer()
            logger.info("Retraining models...")
            train_models()
            show_pipeline_stats()
            logger.info(f"Success at {datetime.now()}")
        except Exception as e:
            logger.error(f"Failed: {e}")
        finally:
            self.is_running = False
    
    def run_incremental_update(self, mode='priority'):
        if self.is_running:
            logger.warning("Already running, skipping")
            return
        try:
            self.is_running = True
            logger.info(f"Starting incremental at {datetime.now()}")
            run_bronze_layer(total_target=500, mode=mode)
            run_silver_layer()
            run_gold_layer()
            train_models()
            logger.info(f"Success at {datetime.now()}")
        except Exception as e:
            logger.error(f"Failed: {e}")
        finally:
            self.is_running = False
    
    def start_scheduler(self, mode='production', collection_mode='priority'):
        logger.info(f"Starting: mode={mode}, collection={collection_mode}")
        if mode == 'production':
            schedule.every().day.at("02:00").do(lambda: self.run_full_pipeline(mode=collection_mode))
            schedule.every(6).hours.do(lambda: self.run_incremental_update(mode=collection_mode))
        elif mode == 'development':
            schedule.every(12).hours.do(lambda: self.run_full_pipeline(mode=collection_mode))
        elif mode == 'testing':
            schedule.every(1).hours.do(lambda: self.run_full_pipeline(mode=collection_mode))
        
        # Run once immediately
        self.run_full_pipeline(mode=collection_mode)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Stopped by user")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Scheduler')
    parser.add_argument('--mode', choices=['production', 'development', 'testing'], default='production')
    parser.add_argument('--collection', choices=['priority', 'full', 'category'], default='priority')
    parser.add_argument('--run-once', action='store_true')
    args = parser.parse_args()
    scheduler = PipelineScheduler()
    if args.run_once:
        scheduler.run_full_pipeline(mode=args.collection)
    else:
        scheduler.start_scheduler(mode=args.mode, collection_mode=args.collection)

if __name__ == "__main__":
    main()

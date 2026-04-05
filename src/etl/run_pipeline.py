"""
Main ELT Pipeline Orchestrator
Runs Bronze → Silver → Gold transformations using MongoDB
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from etl.adzuna_collector import AdzunaCollector
from etl.esco_collector import ESCOCollector
from etl.transformers import BronzeToSilverTransformer, SilverToGoldTransformer
from utils.logger import setup_logger
from utils.mongodb_client import MongoDBClient

logger = setup_logger('elt_pipeline')

def run_bronze_layer(total_target=2000, mode='priority'):
    """
    Extract: Collect raw data from all sources into MongoDB Bronze layer
    
    Args:
        total_target: Total number of jobs to collect across ALL roles (default: 2000)
        mode: 'priority' (30 roles), 'full' (all 150+ roles), or 'category' (by category)
    """
    logger.info("=== EXTRACT: Bronze Layer Collection ===")
    logger.info(f"Mode: {mode} | Total target: {total_target} records across all roles")
    
    # Import role taxonomy
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from config.job_roles_taxonomy import (
        get_priority_roles, get_all_roles, 
        get_all_categories, get_roles_by_category,
        TOTAL_ROLES
    )
    
    # Select roles based on mode
    if mode == 'priority':
        queries = get_priority_roles()
        logger.info(f"Collecting {len(queries)} priority roles")
    elif mode == 'full':
        queries = get_all_roles()
        logger.info(f"Collecting ALL {TOTAL_ROLES} roles across all categories")
    elif mode == 'category':
        # Collect by category for better organization
        queries = []
        categories = get_all_categories()
        logger.info(f"Collecting by category: {len(categories)} categories")
    else:
        queries = get_priority_roles()
    
    # Calculate jobs per role (distribute evenly)
    num_roles = len(queries)
    jobs_per_role = max(1, total_target // num_roles)
    logger.info(f"Collecting ~{jobs_per_role} jobs per role ({num_roles} roles)")
    
    # Collect job postings
    logger.info("Collecting job postings from Adzuna...")
    adzuna = AdzunaCollector()
    try:
        if mode == 'category':
            # Collect by category
            for category in categories:
                category_roles = get_roles_by_category(category)
                logger.info(f"\n📁 Category: {category} ({len(category_roles)} roles)")
                for role in category_roles:
                    jobs = adzuna.fetch_jobs(query=role, target_count=jobs_per_role)
                    adzuna.save_to_bronze(jobs, role, category=category)
        else:
            # Collect all roles in list
            total_queries = len(queries)
            for idx, query in enumerate(queries, 1):
                logger.info(f"[{idx}/{total_queries}] Collecting: {query}")
                jobs = adzuna.fetch_jobs(query=query, target_count=jobs_per_role)
                adzuna.save_to_bronze(jobs, query)
    finally:
        adzuna.close()
    
    # Collect skills taxonomy (2000 skills)
    logger.info("\nCollecting skills taxonomy from ESCO...")
    esco = ESCOCollector()
    try:
        skills = esco.fetch_skills(target_count=2000)
        esco.save_to_bronze(skills)
    finally:
        esco.close()
    
    logger.info("✓ Bronze layer collection completed")

def run_silver_layer():
    """Transform: Clean and standardize data (Bronze → Silver)"""
    logger.info("=== TRANSFORM: Silver Layer Processing ===")
    
    transformer = BronzeToSilverTransformer()
    try:
        # Transform jobs
        jobs_count = transformer.transform_jobs()
        logger.info(f"✓ Transformed {jobs_count} jobs")
        
        # Transform skills
        skills_count = transformer.transform_skills()
        logger.info(f"✓ Transformed {skills_count} skills")
        
    finally:
        transformer.close()
    
    logger.info("✓ Silver layer transformations completed")

def run_gold_layer():
    """Load: Create feature store (Silver → Gold)"""
    logger.info("=== LOAD: Gold Layer Feature Engineering ===")
    
    transformer = SilverToGoldTransformer()
    try:
        # Create skill frequency features
        skill_features = transformer.create_skill_frequency_features()
        logger.info(f"✓ Created {skill_features} skill frequency features")
        
        # Create role-skill matrix
        matrix_features = transformer.create_role_skill_matrix()
        logger.info(f"✓ Created {matrix_features} role-skill relationships")
        
    finally:
        transformer.close()
    
    logger.info("✓ Gold layer feature engineering completed")

def show_pipeline_stats():
    """Display pipeline statistics"""
    logger.info("=== Pipeline Statistics ===")
    
    mongo_client = MongoDBClient()
    mongo_client.connect()
    
    try:
        stats = mongo_client.get_collection_stats()
        
        print("\n📊 MongoDB Collections:")
        for layer in ['bronze', 'silver', 'gold']:
            print(f"\n{layer.upper()} Layer:")
            layer_stats = {k: v for k, v in stats.items() if k.startswith(f"{layer}_")}
            for collection, count in layer_stats.items():
                print(f"  • {collection}: {count:,} documents")
        
        if not stats:
            print("  No data found. Run the pipeline first!")
    
    finally:
        mongo_client.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='RunaGen AI ELT Pipeline')
    parser.add_argument('--layer', choices=['bronze', 'silver', 'gold', 'all', 'stats'], 
                       default='all', help='Which layer to run')
    parser.add_argument('--mode', choices=['priority', 'full', 'category'],
                       default='priority', 
                       help='Collection mode: priority (30 roles), full (150+ roles), category (by category)')
    parser.add_argument('--target', type=int, default=2000,
                       help='Target number of jobs per role (default: 2000)')
    
    args = parser.parse_args()
    
    try:
        if args.layer == 'stats':
            show_pipeline_stats()
        elif args.layer == 'bronze':
            run_bronze_layer(total_target=args.target, mode=args.mode)
        elif args.layer == 'silver':
            run_silver_layer()
        elif args.layer == 'gold':
            run_gold_layer()
        else:  # all
            run_bronze_layer(total_target=args.target, mode=args.mode)
            run_silver_layer()
            run_gold_layer()
            show_pipeline_stats()
        
        logger.info("🎉 Pipeline execution completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
        raise


#!/usr/bin/env python3
"""
Celery worker startup script for ContentForge AI.

Usage:
    python celery_worker.py worker          # Start worker
    python celery_worker.py beat            # Start beat scheduler
    python celery_worker.py flower          # Start flower monitoring
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.celery_app import celery_app


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Celery worker management")
    parser.add_argument(
        "command",
        choices=["worker", "beat", "flower"],
        help="Command to run"
    )
    parser.add_argument(
        "--loglevel",
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level"
    )
    parser.add_argument(
        "--queues",
        default="email,analytics,webhooks,celery",
        help="Comma-separated queue names"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Number of worker processes"
    )
    
    args = parser.parse_args()
    
    if args.command == "worker":
        # Start worker with specified queues
        queues = args.queues.split(",")
        celery_app.worker_main([
            "worker",
            "-Q", ",".join(queues),
            "--loglevel=" + args.loglevel,
            "--concurrency=" + str(args.concurrency),
            "-n", "contentforge@%h",
            "--max-tasks-per-child", "1000",
            "--prefetch-multiplier", "1",
        ])
    
    elif args.command == "beat":
        # Start beat scheduler
        celery_app.start([
            "beat",
            "--loglevel=" + args.loglevel,
            "--scheduler", "celery.beat.PersistentScheduler",
            "-s", "/tmp/celerybeat-schedule",
        ])
    
    elif args.command == "flower":
        # Start flower (requires flower package)
        # pip install flower
        try:
            import flower
            celery_app.start([
                "flower",
                "--loglevel=" + args.loglevel,
            ])
        except ImportError:
            print("Flower not installed. Run: pip install flower")
            sys.exit(1)

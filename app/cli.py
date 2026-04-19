import argparse
import time

from app.crawler import Crawler
from app.search import SearchEngine
from app.storage import Storage


def print_status(storage, crawler=None):
    db = storage.status()

    print("\nSystem Status")
    print("-" * 40)
    print(f"Active jobs   : {db['active_jobs']}")
    print(f"Pages indexed : {db['pages']}")
    print(f"Pending       : {db['pending']}")
    print(f"In progress   : {db['in_progress']}")
    print(f"Done          : {db['done']}")
    print(f"Failed        : {db['failed']}")

    if crawler:
        rt = crawler.runtime_status()
        print(f"Queue         : {rt['queue_size']}/{rt['max_queue_size']}")
        print(f"Workers       : {rt['active_workers']}/{rt['workers']}")
        print(f"Back pressure : {rt['back_pressure']}")

    print("-" * 40)


def handle_index(args):
    storage = Storage()
    crawler = Crawler(storage, workers=args.workers, max_queue_size=args.queue_size)

    job_id = crawler.start_job(args.origin, args.depth)
    print(f"Started job {job_id} for {args.origin} with depth {args.depth}")

    if args.watch:
        try:
            while True:
                print_status(storage, crawler)

                rt = crawler.runtime_status()
                if crawler.task_queue.unfinished_tasks == 0 and rt["active_workers"] == 0:
                    break

                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopped watching.")

    crawler.wait_until_done(job_id)
    print_status(storage, crawler)
    print("Indexing complete.")


def handle_search(args):
    storage = Storage()
    engine = SearchEngine(storage)

    results = engine.search(args.query)

    print(f"\nSearch results for: {args.query}")
    print("-" * 50)

    if not results:
        print("No results found.")
        return

    for i, (url, origin, depth) in enumerate(results, start=1):
        print(f"{i}. relevant_url: {url}")
        print(f"   origin_url  : {origin}")
        print(f"   depth       : {depth}")
        print()


def handle_status(args):
    storage = Storage()
    print_status(storage)


def build_parser():
    parser = argparse.ArgumentParser(description="Multi-agent web crawler CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="Start indexing")
    p_index.add_argument("origin", type=str)
    p_index.add_argument("depth", type=int)
    p_index.add_argument("--workers", type=int, default=4)
    p_index.add_argument("--queue-size", type=int, default=100)
    p_index.add_argument("--watch", action="store_true")
    p_index.set_defaults(func=handle_index)

    p_search = sub.add_parser("search", help="Search indexed pages")
    p_search.add_argument("query", type=str)
    p_search.set_defaults(func=handle_search)

    p_status = sub.add_parser("status", help="Show system status")
    p_status.set_defaults(func=handle_status)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
import queue
import threading

from app.fetcher import fetch_url
from app.parser import parse_html
from app.storage import Storage
from app.utils import normalize_url, term_frequencies


class Crawler:
    def __init__(self, storage, workers=4, max_queue_size=100):
        self.storage = storage
        self.workers = workers
        self.max_queue_size = max_queue_size

        self.task_queue = queue.Queue(maxsize=max_queue_size)
        self.visited = {}
        self.visited_lock = threading.Lock()

        self.active_workers = 0
        self.active_workers_lock = threading.Lock()

        self.threads = []
        self.stop_event = threading.Event()

    def start_job(self, origin_url, max_depth):
        origin = normalize_url(origin_url, origin_url)
        if not origin:
            raise ValueError("Invalid origin URL")

        job_id = self.storage.create_job(origin, max_depth)
        self.storage.add_frontier(job_id, origin, 0)
        self.storage.add_discovery(job_id, origin, origin, 0)

        self.visited[job_id] = {origin}

        pending = self.storage.get_pending(job_id)
        if pending:
            row = pending[0]
            self.storage.mark_in_progress(row["id"])
            self.task_queue.put((row["id"], job_id, origin, origin, 0))

        self._start_workers()
        return job_id

    def _start_workers(self):
        self.threads = []
        for _ in range(self.workers):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()
            self.threads.append(t)

    def _worker_loop(self):
        while not self.stop_event.is_set():
            try:
                frontier_id, job_id, url, origin_url, depth = self.task_queue.get(timeout=1)
            except queue.Empty:
                continue

            with self.active_workers_lock:
                self.active_workers += 1

            try:
                self._process_url(frontier_id, job_id, url, origin_url, depth)
            finally:
                with self.active_workers_lock:
                    self.active_workers -= 1
                self.task_queue.task_done()

    def _process_url(self, frontier_id, job_id, url, origin_url, depth):
        result = fetch_url(url)

        if not result["success"]:
            self.storage.mark_failed(frontier_id)
            return

        parsed = parse_html(url, result["html"])
        title = parsed["title"]
        body = parsed["body"]
        links = parsed["links"]

        self.storage.save_page(url, title, body)
        self.storage.save_terms(url, term_frequencies(f"{title} {body}"))

        next_depth = depth + 1

        conn = self.storage._get_conn()
        job = conn.execute(
            "SELECT * FROM crawl_jobs WHERE job_id=?",
            (job_id,)
        ).fetchone()

        if next_depth <= job["max_depth"]:
            for link in links:
                normalized = normalize_url(url, link)
                if not normalized:
                    continue

                with self.visited_lock:
                    if normalized in self.visited[job_id]:
                        continue
                    self.visited[job_id].add(normalized)

                inserted = self.storage.add_frontier(job_id, normalized, next_depth)
                self.storage.add_discovery(job_id, normalized, origin_url, next_depth)

                if inserted:
                    pending = self.storage.get_pending(job_id)
                    match = None
                    for row in pending:
                        if row["url"] == normalized and row["depth"] == next_depth:
                            match = row
                            break

                    if match:
                        self.storage.mark_in_progress(match["id"])
                        self.task_queue.put(
                            (match["id"], job_id, normalized, origin_url, next_depth)
                        )

        self.storage.mark_done(frontier_id)

    def resume_jobs(self):
        jobs = self.storage.get_active_jobs()

        for job in jobs:
            job_id = job["job_id"]

            if job_id not in self.visited:
                self.visited[job_id] = set()

            pending = self.storage.get_pending(job_id)

            for row in pending:
                url = row["url"]
                depth = row["depth"]

                self.visited[job_id].add(url)
                self.storage.mark_in_progress(row["id"])

                self.task_queue.put(
                    (row["id"], job_id, url, job["origin_url"], depth)
                )

        if jobs:
            self._start_workers()

    def wait_until_done(self, job_id=None):
        self.task_queue.join()
        if job_id is not None:
            self.storage.complete_job(job_id)

    def runtime_status(self):
        with self.active_workers_lock:
            active = self.active_workers

        return {
            "queue_size": self.task_queue.qsize(),
            "max_queue_size": self.max_queue_size,
            "active_workers": active,
            "workers": self.workers,
            "back_pressure": self.task_queue.qsize() >= self.max_queue_size,
        }

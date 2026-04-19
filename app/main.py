from app.crawler import Crawler
from app.storage import Storage


def main():
    storage = Storage()
    crawler = Crawler(storage, workers=4, max_queue_size=100)

    job_id = crawler.start_job("https://example.com", 1)
    print("started job:", job_id)

    crawler.wait_until_done(job_id)

    print("db status:", storage.status())
    print("runtime status:", crawler.runtime_status())


if __name__ == "__main__":
    main()
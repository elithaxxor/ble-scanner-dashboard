#!/usr/bin/env python
import argparse
import asyncio
import logging
import signal
import sys

from core.scanner import run_scanner
from core.utils import setup_logging

stop_event = asyncio.Event()


def _handle_stop(signame: str) -> None:
    logging.getLogger(__name__).info("Received %s, stopping", signame)
    stop_event.set()


async def main(
    interval: int, workers: int, threads: int, processes: int, threaded_scan: bool
) -> None:
    scanner_task = asyncio.create_task(
        run_scanner(
            interval,
            workers,
            threads,
            processes,
            stop_event=stop_event,
            threaded_scan=threaded_scan,
        )
    )
    await stop_event.wait()
    scanner_task.cancel()
    await asyncio.gather(scanner_task, return_exceptions=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=5)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--processes", type=int, default=0)
    parser.add_argument("--threaded-scan", action="store_true")
    args = parser.parse_args()

    setup_logging()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: _handle_stop(sig.name))
    loop.add_reader(
        sys.stdin,
        lambda: _handle_stop("keyboard") if sys.stdin.read(1).lower() == "q" else None,
    )

    loop.run_until_complete(
        main(
            args.interval,
            args.workers,
            args.threads,
            args.processes,
            args.threaded_scan,
        )
    )

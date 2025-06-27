#!/usr/bin/env python
import argparse
import asyncio
import logging
import signal
from core.scanner import run_scanner
from core.utils import setup_logging

stop_event = asyncio.Event()


def _handle_stop(signame: str) -> None:
    logging.getLogger(__name__).info("Received %s, stopping", signame)
    stop_event.set()


async def main(interval: int, workers: int) -> None:
    tasks = [asyncio.create_task(run_scanner(interval)) for _ in range(workers)]
    await stop_event.wait()
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=5)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()

    setup_logging()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: _handle_stop(sig.name))

    loop.run_until_complete(main(args.interval, args.workers))

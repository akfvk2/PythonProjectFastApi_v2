import asyncio
import logging
from src.students.consumer import run_student_events_consumer, run_student_events_retry_consumer

async def _run() -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(run_student_events_consumer())
        tg.create_task(run_student_events_retry_consumer())


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(_run())

if __name__ == "__main__":
    main()
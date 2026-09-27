import uvicorn
import asyncio
import argparse
import logging
from src.students.consumer import run_student_events_consumer, run_student_events_retry_consumer

def _run_web() -> None:
    uvicorn.run(
        "src.application:get_app",
        host="localhost",
        port=8001,
        reload=True,
        factory=True,)

async def _run_consumers() -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(run_student_events_consumer())
        tg.create_task(run_student_events_retry_consumer())

def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["web", "consumer"])
    args = parser.parse_args()

    if args.mode == "web":
        _run_web()
    else:
        asyncio.run(_run_consumers())



if __name__ == "__main__":
    main()
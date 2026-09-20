import asyncio
import logging
from src.students.consumer import run_student_events_consumer

def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_student_events_consumer())

if __name__ == "__main__":
    main()
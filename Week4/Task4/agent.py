import json
import os
import time
from datetime import datetime
from database import execute_query
from validator import validate_sql
from sql_generator import extract_decomposition, generate_sql, fix_sql, summarize_result

os.makedirs("logs", exist_ok=True)


def log_agent(entry: dict):
    log_file = f"logs/agent_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")


async def run_agent(question: str) -> dict:
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "decomposition": None,
        "attempts": [],
        "final_sql": None,
        "status": None,
        "error": None,
        "latency_ms": None,
    }

    start = time.time()
    MAX_RETRIES = 3

    try:
        # Step 1: Understand the query
        decomposition = extract_decomposition(question)
        log_entry["decomposition"] = decomposition

        # Step 2: Generate initial SQL
        sql = generate_sql(question, decomposition)
        last_error = None

        # Step 3 + 4: Execute with up to 3 retries
        for attempt in range(1, MAX_RETRIES + 1):
            attempt_log = {
                "attempt": attempt,
                "sql": sql,
                "status": None,
                "error": None,
                "execution_ms": None,
            }

            # Validate first
            is_valid, validation_error = validate_sql(sql)
            if not is_valid:
                attempt_log["status"] = "blocked"
                attempt_log["error"] = validation_error
                log_entry["attempts"].append(attempt_log)
                log_entry["status"] = "blocked"
                log_entry["error"] = validation_error
                log_entry["latency_ms"] = round((time.time() - start) * 1000)
                log_agent(log_entry)
                return {
                    "question": question,
                    "sql": sql,
                    "result": None,
                    "summary": "Query was blocked for safety reasons.",
                    "status": "blocked",
                    "error": validation_error,
                    "attempts": attempt,
                }

            # Execute
            exec_start = time.time()
            try:
                result = await execute_query(sql)
                attempt_log["execution_ms"] = round((time.time() - exec_start) * 1000)
                attempt_log["status"] = "success"
                log_entry["attempts"].append(attempt_log)
                log_entry["final_sql"] = sql
                log_entry["status"] = "success" if attempt == 1 else f"success_after_{attempt}_attempts"
                log_entry["latency_ms"] = round((time.time() - start) * 1000)

                # Step 5: Summarize result
                summary = summarize_result(question, sql, result)

                log_agent(log_entry)
                return {
                    "question": question,
                    "sql": sql,
                    "result": result[:100],
                    "result_count": len(result),
                    "summary": summary,
                    "status": log_entry["status"],
                    "attempts": attempt,
                    "latency_ms": log_entry["latency_ms"],
                }

            except Exception as exec_error:
                last_error = str(exec_error)
                attempt_log["execution_ms"] = round((time.time() - exec_start) * 1000)
                attempt_log["status"] = "failed"
                attempt_log["error"] = last_error
                log_entry["attempts"].append(attempt_log)

                if attempt < MAX_RETRIES:
                    # Ask LLM to fix and retry
                    sql = fix_sql(sql, last_error)
                else:
                    # All retries exhausted
                    log_entry["status"] = "failed"
                    log_entry["error"] = last_error
                    log_entry["latency_ms"] = round((time.time() - start) * 1000)
                    log_agent(log_entry)
                    return {
                        "question": question,
                        "sql": sql,
                        "result": None,
                        "summary": f"Sorry, I could not answer this question after {MAX_RETRIES} attempts. Last error: {last_error}",
                        "status": "failed",
                        "error": last_error,
                        "attempts": MAX_RETRIES,
                        "latency_ms": log_entry["latency_ms"],
                    }

    except Exception as e:
        log_entry["status"] = "error"
        log_entry["error"] = str(e)
        log_entry["latency_ms"] = round((time.time() - start) * 1000)
        log_agent(log_entry)
        return {
            "question": question,
            "sql": None,
            "result": None,
            "summary": "An unexpected error occurred.",
            "status": "error",
            "error": str(e),
            "attempts": 0,
        }
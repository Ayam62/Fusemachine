import json
import os
import time
from datetime import datetime
from database import execute_query
from validator import validate_sql
from sql_generator import generate_sql, extract_decomposition, fix_sql

os.makedirs("logs", exist_ok=True)


def log_query(entry: dict):
    log_file = f"logs/queries_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


async def run_pipeline(question: str) -> dict:
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "decomposition": None,
        "sql": None,
        "retry_sql": None,
        "status": None,
        "error": None,
        "retry_needed": False,
        "result_count": 0,
        "latency_ms": None,
    }

    start = time.time()

    try:
        # Step 1: Decompose the question
        decomposition = extract_decomposition(question)
        log_entry["decomposition"] = decomposition

        # Step 2: Generate SQL
        sql = generate_sql(question, decomposition)
        log_entry["sql"] = sql

        # Step 3: Validate SQL
        is_valid, validation_error = validate_sql(sql)
        if not is_valid:
            log_entry["status"] = "blocked"
            log_entry["error"] = validation_error
            log_entry["latency_ms"] = round((time.time() - start) * 1000)
            log_query(log_entry)
            return {
                "question": question,
                "decomposition": decomposition,
                "sql": sql,
                "result": [],
                "status": "blocked",
                "error": validation_error,
                "retry_needed": False,
            }

        # Step 4: Execute SQL
        try:
            result = await execute_query(sql)
            log_entry["status"] = "success"
            log_entry["result_count"] = len(result)

        except Exception as exec_error:
            # Step 5: Retry once with Gemini fix
            log_entry["retry_needed"] = True
            error_msg = str(exec_error)

            fixed_sql = fix_sql(sql, error_msg)
            log_entry["retry_sql"] = fixed_sql

            is_valid2, validation_error2 = validate_sql(fixed_sql)
            if not is_valid2:
                log_entry["status"] = "failed"
                log_entry["error"] = f"Retry SQL blocked: {validation_error2}"
                log_entry["latency_ms"] = round((time.time() - start) * 1000)
                log_query(log_entry)
                return {
                    "question": question,
                    "decomposition": decomposition,
                    "sql": sql,
                    "retry_sql": fixed_sql,
                    "result": [],
                    "status": "failed",
                    "error": log_entry["error"],
                    "retry_needed": True,
                }

            try:
                result = await execute_query(fixed_sql)
                sql = fixed_sql
                log_entry["sql"] = fixed_sql
                log_entry["status"] = "success_after_retry"
                log_entry["result_count"] = len(result)
            except Exception as retry_error:
                log_entry["status"] = "failed"
                log_entry["error"] = str(retry_error)
                log_entry["latency_ms"] = round((time.time() - start) * 1000)
                log_query(log_entry)
                return {
                    "question": question,
                    "decomposition": decomposition,
                    "sql": sql,
                    "retry_sql": fixed_sql,
                    "result": [],
                    "status": "failed",
                    "error": str(retry_error),
                    "retry_needed": True,
                }

    except Exception as e:
        log_entry["status"] = "error"
        log_entry["error"] = str(e)
        log_entry["latency_ms"] = round((time.time() - start) * 1000)
        log_query(log_entry)
        return {
            "question": question,
            "sql": None,
            "result": [],
            "status": "error",
            "error": str(e),
            "retry_needed": False,
        }

    log_entry["latency_ms"] = round((time.time() - start) * 1000)
    log_query(log_entry)

    return {
        "question": question,
        "decomposition": decomposition,
        "sql": sql,
        "result": result[:100],  # cap at 100 rows
        "status": log_entry["status"],
        "retry_needed": log_entry["retry_needed"],
        "result_count": len(result),
        "latency_ms": log_entry["latency_ms"],
    }
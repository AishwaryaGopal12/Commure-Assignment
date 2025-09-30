"""
Utility functions for SQL script execution and query evaluation.

This module provides helper functions for executing SQL scripts,
comparing queries, and evaluating SQL generation systems.
"""
import os
import time
from pathlib import Path
from typing import List
from openai import OpenAI

def execute_sql_script(cursor, script_file_path):
    """
    Execute a SQL script file using the provided database cursor.

    Reads a SQL script from the SQL_Files directory relative to this module's location
    and executes it using the cursor's executescript method.

    Args:
        cursor: Database cursor object with executescript method (e.g., sqlite3.Cursor).
        script_file_path (str): Relative path to the SQL script file within the SQL_Files directory.

    """
    # Get the directory where this Python file (utils.py) is located
    # This ensures the path works regardless of where the script is called from
    base_dir = Path(__file__).resolve().parent

    # Construct the full path to the SQL file by joining base directory with SQL_Files folder
    # and the provided script file name
    sql_file = os.path.join(base_dir, "SQL_Files", script_file_path)

    # Open the SQL file in read mode and load its entire contents
    with open(sql_file, 'r') as file:
        sql_script = file.read()

    # Execute the entire SQL script at once using executescript
    # This method can handle multiple SQL statements separated by semicolons
    cursor.executescript(sql_script)

def judge_sql_similarity(nlq: str, sql1: str, sql2: str) -> str:
    """
    Use an LLM to judge whether two SQL queries are semantically equivalent.

    Sends a prompt to GPT-4o to determine if two SQL queries would produce similar results
    for a given natural language question. The judgment allows for minor differences like
    extra columns (e.g., ID fields) but identifies substantive differences in query intent.

    Args:
        nlq (str): The natural language question that prompted the SQL queries.
        sql1 (str): The first SQL query to compare (typically the expected/reference query).
        sql2 (str): The second SQL query to compare (typically the generated query).

    Returns:
        str: One of the following:
            - "Equivalent": Queries are semantically equivalent.
            - "Not Equivalent": Queries have different meanings or results.
            - "Error": An error occurred during LLM call.
    """
    # Construct a detailed prompt that instructs the LLM to judge SQL equivalence
    # The prompt provides context about the question and both SQL queries
    prompt = f"""
            You are a SQL expert. A user asked a question, and two SQL queries were generated in response. Judge if both queries are equivalent in meaning and would produce the similar result. If there are extra columns like ID column etc. that is fine. When executed, they should produce a similar result. For instance, if the question is to fetch all doctor names, then getting doctor names with Doctor ID is fine but getting the appointments of doctors is not correct.
            
            Respond ONLY with one of the following:
            - "Equivalent"
            - "Not Equivalent"
            
            User Question: {nlq}
            
            Query 1:
            {sql1}
            
            Query 2:
            {sql2}
            
            Are the queries equivalent?
            """
    try:
        # Initialize OpenAI client (API key should be set in environment variables)
        client = OpenAI()

        # Make API call to GPT-4o model with the constructed prompt
        # Temperature=0 ensures deterministic, consistent responses
        resp = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o for high-quality judgments
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # Deterministic output for consistency
        )

        # Extract the decision from the response and remove any leading/trailing whitespace
        decision = resp.choices[0].message.content.strip()

        return decision
    except Exception as err:
        # If any error occurs during the API call, log it and return "Error"
        print(f"[Error] LLM judge failed: {err}")
        return "Error"

def evaluate(sql_helper, test_cases) -> List[dict]:
    """
    Evaluate a SQL generation system against a set of test cases.

    Runs each test case through the SQL helper, compares generated SQL with expected SQL
    using both exact matching and LLM-based semantic judgment. Includes retry logic for
    resilience against temporary API failures.

    Args:
        sql_helper: Object with a get_sql(nlq: str) method that generates SQL from natural
                    language questions. Should return a tuple/list where first element is
                    the generated SQL string.
        test_cases (list): List of dictionaries, each containing:
            - 'question' (str): Natural language question.
            - 'actual_query' (str): Expected/reference SQL query.

    Returns:
        List[dict]: List of result dictionaries, one per test case, containing:
            - 'question' (str): The natural language question.
            - 'expected_sql' (str): The reference SQL query.
            - 'generated_sql' (str or None): The generated SQL query, or None if error.
            - 'exact_match' (bool): Whether generated SQL exactly matches expected SQL.
            - 'llm_judged_equivalent' (str or None): LLM judgment if not exact match.
            - 'error' (str, optional): Error message if generation failed.
    """
    # Initialize empty list to store evaluation results for all test cases
    results = []

    # Iterate through each test case in the provided list
    for case in test_cases:
        # Wait 2 seconds before processing to avoid hitting API rate limits
        time.sleep(2)

        nlq = case['question']
        print(nlq)  # Print question for progress tracking

        expected_sql = case['actual_query']

        try:
            # First attempt: Try to generate SQL from the natural language question
            try:
                generated_sql = sql_helper.get_sql(nlq)
            except Exception as err:
                # If first attempt fails, log error and retry after 4 seconds
                print(f"[evaluate] Error occurred: {err}. Sleeping 4s and retrying once...")
                time.sleep(4)
                generated_sql = sql_helper.get_sql(nlq)

            # Check if SQL generation returned a valid result
            # The helper should return a tuple/list where first element is the SQL string
            if not generated_sql or not generated_sql[0]:
                raise ValueError("Agent returned no SQL.")

            exact_match = generated_sql[0].strip().lower() == expected_sql.strip().lower()

            # Initialize LLM judgment as None (only used if exact match fails)
            llm_judgment = None

            # If queries don't match exactly, use LLM to judge semantic equivalence
            if not exact_match:
                try:
                    # First attempt to get LLM judgment
                    llm_judgment = judge_sql_similarity(nlq, expected_sql, generated_sql[0])
                except Exception as err:
                    # If LLM judge fails, retry after 4 seconds
                    print(f"[judge] Error: {err}. Sleeping 4s and retrying once...")
                    time.sleep(4)
                    llm_judgment = judge_sql_similarity(nlq, expected_sql, generated_sql[0])

            # Append successful evaluation result to results list
            results.append({
                "question": nlq,
                "expected_sql": expected_sql,
                "generated_sql": generated_sql[0],
                "exact_match": exact_match,
                "llm_judged_equivalent": llm_judgment
            })

        except Exception as err:
            # If all attempts fail, log the error and add a failure record
            print(f"[evaluate] Skipped due to error after retry: {err}")
            results.append({
                "question": nlq,
                "expected_sql": expected_sql,
                "generated_sql": None,  # No SQL was generated
                "exact_match": False,  # Cannot match if generation failed
                "llm_judged_equivalent": None,  # Cannot judge if no SQL generated
                "error": str(err)  # Include error message for debugging
            })

    # Return the complete list of evaluation results
    return results
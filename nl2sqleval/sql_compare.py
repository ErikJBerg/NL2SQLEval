import difflib
import sqlite3
import logging

from .database import Database


def compare_queries(expected: str, generated: str):
    """Compare two queries and highlight the differences."""
    # Split the queries into tokens
    expected_tokens = expected.split()
    generated_tokens = generated.split()

    # Calculate the difference using difflib
    diff = difflib.ndiff(expected_tokens, generated_tokens)

    # Reconstruct the queries with highlighting
    expected_highlighted = []
    generated_highlighted = []
    for line in diff:
        if line.startswith('+ '):
            generated_highlighted.append(f"\033[92m{line[2:]}\033[0m")
            expected_highlighted.append(f"\033[91m_\033[0m")
        elif line.startswith('- '):
            expected_highlighted.append(f"\033[91m{line[2:]}\033[0m")
            generated_highlighted.append(f"\033[92m_\033[0m")
        else:
            expected_highlighted.append(line)
            generated_highlighted.append(line)

    expected_highlighted = ' '.join(expected_highlighted)
    generated_highlighted = ' '.join(generated_highlighted)

    return expected_highlighted, generated_highlighted


def validate_query(query: str, database: Database):
    """Validate the query by executing it on the database."""
    try:
        cursor = database.get_cursor()
        cursor.execute(query)
        return True
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return False


def compare_results(expected_query: str, generated_query: str, database: Database):
    """Compare the results of two queries.

    Args:
        expected_query (str): The expected query
        generated_query (str): The generated query
        database (Database): Database object to execute the queries

    Returns:
        Tuple: A tuple containing the comparison result (True/False), the expected results, and the generated results
            - in case of a partial match, the comparison result is 'partial'
            - in case of failure to execute the queries, the results are returned as dictionaries with an 'error' key

    """
    try:
        cursor = database.get_cursor()
    except Exception as e:
        logging.error(f"Error getting cursor: {e}", exc_info=True)
        return False, {'error': str(e)}, {'error': str(e)}

    try:
        expected_result = cursor.execute(expected_query).fetchall()
    except Exception as e:
        expected_result = {'error': str(e)}

    try:
        generated_result = cursor.execute(generated_query).fetchall()
    except Exception as e:
        generated_result = {'error': str(e)}

    if 'error' in generated_result or len(expected_result) != len(generated_result):
        return False, expected_result, generated_result

    for exp_row, gen_row in zip(expected_result, generated_result):
        if exp_row != gen_row:
            if all(item in gen_row for item in exp_row):
                return 'partial', expected_result, generated_result
            return False, expected_result, generated_result

    return True, expected_result, generated_result

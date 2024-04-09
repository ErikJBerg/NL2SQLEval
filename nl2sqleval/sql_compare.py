import difflib
import sqlite3
import logging
import sqlparse
import re

import sqlglot
from sqlglot import parse_one, exp, diff as sqlglot_diff
from sqlglot.optimizer import optimize

from .database import Database


def extract_clauses(parsed_query: sqlglot.Expression) -> dict:
    """Extract the clauses from a parsed SQL query.

    Args:
        parsed_query (sqlglot.SQL): The parsed SQL query

    Returns:
        dict: A dictionary containing the extracted clauses
            - the keys are the clause types (Select, From, Where, Group, Having, Order, Limit)
    """
    clauses = {}

    for clause in (
            exp.Select, exp.From, exp.Where, exp.Group, exp.Having, exp.Order, exp.Limit
    ):
        found_clauses = [clause.sql() for clause in parsed_query.find_all(clause)]
        if found_clauses:
            clauses[clause.key] = found_clauses
    return clauses


def compare_queries(
        expected: str,
        generated: str,
        optimize_query=False
) -> tuple[str, list[tuple[str, str]], tuple[str, str]]:
    """Compare two queries and calculate the similarity score.

    Args:
        expected (str): The expected query
        generated (str): The generated query
        optimize_query (bool): Whether to optimize the queries before comparing

    Returns:
        Tuple: A tuple containing:
            - the similarity score
            - the differences between the queries
            - the changes highlighted in queries as a string

        the similarity score is a float between 0 and 1, where 1 means the queries are identical
        the differences are a list of tuples,
            - where each tuple contains the highlighted difference as the actions to be taken
                if trying to convert the expected query to the generated query
    """

    # Parse queries
    expected_parsed = parse_one(expected)
    generated_parsed = parse_one(generated)

    differences_ast = sqlglot_diff(
        expected_parsed,
        generated_parsed
    )

    normalized_differences = [
        (change_action.expression.sql(), change_action.__class__.__name__)
        for change_action in differences_ast if hasattr(change_action, 'expression')
    ]

    if optimize_query:
        try:
            expected_normalized = optimize(expected_parsed).sql()
            generated_normalized = optimize(generated_parsed).sql()
        except Exception as e:
            logging.error(f"Error optimizing queries: {e}", exc_info=True)
            expected_normalized = expected
            generated_normalized = generated

        # Split the queries into tokens
        expected_tokens = [str(token) for token in sqlparse.parse(expected_normalized)[0].flatten() if str(token).strip()]
        generated_tokens = [str(token) for token in sqlparse.parse(generated_normalized)[0].flatten() if str(token).strip()]

        # Calculate the similarity score
        similarity_score = difflib.SequenceMatcher(None, expected_tokens, generated_tokens).ratio()
    else:

        # Split the queries into tokens
        expected_tokens = [str(token) for token in sqlparse.parse(expected)[0].flatten() if str(token).strip()]
        generated_tokens = [str(token) for token in sqlparse.parse(generated)[0].flatten() if str(token).strip()]

        # Calculate the similarity score
        similarity_score = difflib.SequenceMatcher(None, expected_tokens, generated_tokens).ratio()

    # Highlight the differences
    differ = difflib.Differ()

    # Generate the differences
    diff = list(differ.compare([re.sub(r'\s+', ' ', expected)], [re.sub(r'\s+', ' ', generated)]))

    # Build the difference visualization string
    diff_string = ""
    for line in diff:
        if line.startswith('- '):
            diff_string += '-' + line[2:] + '\n'
        elif line.startswith('+ '):
            diff_string += '+' + line[2:] + '\n'
        elif line.startswith('? '):
            diff_string += ' ' + line[2:].rstrip() + '\n'
            diff_string += '?' + ' ' * (len(line) - 3) + '^\n'

    # Remove the trailing newline character
    diff_string = diff_string.rstrip()

    return similarity_score, normalized_differences, diff_string


def compare_clauses(expected: str, generated: str):
    """Compare the clauses of two queries.

    Args:
        expected (str): The expected query
        generated (str): The generated query

    Returns:
        Tuple: A tuple containing the similarity scores for each clause type and the average similarity score for all
            - the similarity scores are a dictionary where the keys are the clause types
                - for now we support: Select, From, Where, Group, Having, Order, Limit
    """
    try:
        # Parse the SQL queries using sqlglot
        expected_parsed = parse_one(expected)
        generated_parsed = parse_one(generated)

        # Extract the clauses from the parsed queries
        expected_clauses = extract_clauses(expected_parsed)
        generated_clauses = extract_clauses(generated_parsed)

        # Calculate the similarity score for each clause
        clause_similarities = {}
        for clause_type in expected_clauses:
            if clause_type in generated_clauses:
                expected_clause_list = expected_clauses[clause_type]
                generated_clause_list = generated_clauses[clause_type]

                clause_similarity_scores = []
                for expected_clause, generated_clause in zip(expected_clause_list, generated_clause_list):
                    clause_similarity = difflib.SequenceMatcher(None, expected_clause, generated_clause).ratio()
                    clause_similarity_scores.append(clause_similarity)

                avg_clause_similarity = sum(clause_similarity_scores) / len(clause_similarity_scores)
                clause_similarities[clause_type] = avg_clause_similarity
            else:
                clause_similarities[clause_type] = 0.0

        # Calculate the average similarity score for all clauses
        avg_similarity = sum(clause_similarities.values()) / len(clause_similarities)

        return clause_similarities, avg_similarity

    except Exception as e:
        logging.error(f"Error comparing clauses: {e}", exc_info=True)
        return {}, 0.0


def validate_query(query: str, database: Database):
    """Validate the query by executing it on the database."""
    try:
        cursor = database.get_cursor()
        cursor.execute(query)
        return True
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return False


def compare_results(
        expected_query: str,
        generated_query: str,
        database: Database,
        ignore_row_order=True,
        ignore_column_order=True
):
    """Compare the results of two queries.

    Args:
        expected_query (str): The expected query
        generated_query (str): The generated query
        database (Database): Database object to execute the queries
        ignore_row_order (bool): Whether to ignore the order of rows in the comparison (default: True)
        ignore_column_order (bool): Whether to ignore the order of columns in the comparison (default: True)

    Returns:
        Tuple: A tuple containing the comparison result (True/False/partial/partial_incomplete),
               the expected results, and the generated results
            - in case of an exact match, the comparison result is True
            - in case of a partial match (all expected values in generated results), the comparison result is 'partial'
            - in case of a partial match (at least one expected value in generated results), the comparison result is 'partial_incomplete'
            - in case of no match, the comparison result is False
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

    if 'error' in generated_result or 'error' in expected_result or len(expected_result) != len(generated_result):
        return False, expected_result, generated_result

    if ignore_row_order:
        expected_result = sorted(expected_result, key=lambda row: [str(item) for item in row])
        generated_result = sorted(generated_result, key=lambda row: [str(item) for item in row])

    if ignore_column_order:
        expected_result = [sorted(str(item) for item in row) for row in expected_result]
        generated_result = [sorted(str(item) for item in row) for row in generated_result]

    partial_match = False
    partial_incomplete_match = False

    for exp_row, gen_row in zip(expected_result, generated_result):
        if exp_row != gen_row:
            if all(str(item) in [str(i) for i in gen_row] for item in exp_row) and not partial_incomplete_match:
                partial_match = True
            elif any(str(item) in [str(i) for i in gen_row] for item in exp_row):
                partial_incomplete_match = True
            else:
                return False, expected_result, generated_result

    if partial_match:
        return 'partial', expected_result, generated_result
    elif partial_incomplete_match:
        return 'partial_incomplete', expected_result, generated_result
    else:
        return True, expected_result, generated_result

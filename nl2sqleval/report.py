from .sql_compare import compare_queries, validate_query, compare_results
from .database import Database


def generate_report(
        expected_queries: list[dict],
        generated_queries: list[dict],
        database: Database
) -> list:
    """Generate comparison report from expected and generated queries.
    Take in a list of expected and generated queries and:
        - compare queries
        - check validity of each query
        - compare the results of the queries and check partial or complete match

    Args:
        expected_queries (list): List of expected queries as dictionaries containing 'question' and 'query' keys
        generated_queries (list): List of generated queries as dictionaries containing 'question' and 'query' keys
        database (Database): Database object to execute the queries

    Returns:
        list: List of dictionaries containing the comparison results
    """
    report = []
    for expected_query, generated_query in zip(expected_queries, generated_queries):
        question = expected_query['question']
        expected_sql = expected_query['query']
        generated_sql = generated_query['query']

        # Compare the queries and highlight the differences
        expected_highlighted, generated_highlighted = compare_queries(expected_sql, generated_sql)

        # Validate the generated query
        valid_query = validate_query(generated_sql, database)

        # Compare the results of the queries
        same_results, expected_result, generated_result = compare_results(expected_sql, generated_sql, database)

        report.append({
            'question': question,
            'expected_sql': expected_highlighted,
            'generated_sql': generated_highlighted,
            'expected_result': expected_result,
            'generated_result': generated_result,
            'valid_query': valid_query,
            'matching_results': same_results
        })

    return report


def print_report(report: list):
    """Print the comparison report.

    Args:
        report (list): List of dictionaries containing the comparison results as dictionaries with keys:
            - question
            - expected_sql
            - generated_sql
            - valid_query
            - matching_results
    """
    for entry in report:
        print(f"Question: {entry['question']}")
        print(f"Expected SQL: {entry['expected_sql']}")
        print(f"Generated SQL: {entry['generated_sql']}")
        print(f"Valid query: {entry['valid_query']}")
        print(f"Same results: {entry['matching_results']}")
        # print(f"Expected results: {entry['expected_result']}")
        # print(f"Got results: {entry['generated_result']}")
        print('------')

    # Count the number of valid queries and queries with same results
    valid_queries = sum(entry['valid_query'] for entry in report)
    matching_results_count = sum(entry['matching_results'] for entry in report if entry['matching_results'] is True)
    partial_results_count = len([entry['matching_results'] for entry in report if entry['matching_results'] == 'partial'])

    print(f"Number of valid queries: {valid_queries}/{len(report)}")
    print(f"Number of queries with same results: {matching_results_count}/{len(report)}")
    print(f"Number of queries with partially matching results: {partial_results_count}/{len(report)}")

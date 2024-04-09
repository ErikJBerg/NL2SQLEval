from statistics import mean

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
        token_similarity_score, changes, string_comparison = compare_queries(expected_sql, generated_sql)

        # Validate the generated query
        valid_query = validate_query(generated_sql, database)

        # Compare the results of the queries
        same_results, expected_result, generated_result = compare_results(expected_sql, generated_sql, database)

        report.append(
            {
                'question': question,
                'expected': expected_sql,
                'generated': generated_sql,
                'comparison_string': string_comparison,
                'expected_result': expected_result,
                'generated_result': generated_result,
                'valid_query': valid_query,
                'same_results': same_results,
                'query_token_similarity_score': token_similarity_score,
                'changes': changes
            }
        )

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
    valid_queries = [comparison for comparison in report if comparison['valid_query']]
    queries_with_same_results = [comparison for comparison in report if comparison['same_results'] is True]
    queries_with_partially_matching_results = [
        comparison for comparison in report if comparison['same_results'] == 'partial'
    ]

    total_queries = len(report)
    num_valid_queries = len(valid_queries)
    num_queries_with_same_results = len(queries_with_same_results)
    num_queries_with_partially_matching_results = len(queries_with_partially_matching_results)

    # Calculate additional metrics
    percentage_valid_queries = (num_valid_queries / total_queries) * 100
    percentage_queries_with_same_results = (num_queries_with_same_results / total_queries) * 100

    similarity_scores = [r['query_token_similarity_score'] for r in valid_queries]
    average_similarity_score = mean(similarity_scores) if similarity_scores else 0.0

    for result in report:
        print("------")
        print(f"Question: {result['question']}")
        print(f"Expected SQL: {result['expected']}")
        print(f"Comparison string:\n{result['comparison_string']}")
        print(f"Generated SQL: {result['generated']}")
        print(f"Valid query: {result['valid_query']}")
        print(f"Same results: {result['same_results']}")

    print(f"\nPercentage of valid queries: {percentage_valid_queries:.2f}%")
    print(f"Percentage of queries with same results: {percentage_queries_with_same_results:.2f}%")
    print(f"Average similarity score: {average_similarity_score:.2f}")

    print(f"Number of valid queries: {num_valid_queries}/{total_queries}")
    print(f"Number of queries with same results: {num_queries_with_same_results}/{total_queries}")
    print(f"Number of queries with partially matching results: {num_queries_with_partially_matching_results}/{total_queries}")

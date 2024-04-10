from statistics import mean
from collections import Counter

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
        - track errors that occur during query execution

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

        # Track errors that occur during query execution
        if isinstance(expected_result, dict):
            expected_error = expected_result.get('error', None)
        else:
            expected_error = None

        if isinstance(generated_result, dict):
            generated_error = generated_result.get('error', None)
        else:
            generated_error = None

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
                'changes': changes,
                'expected_error': expected_error,
                'generated_error': generated_error
            }
        )

    return report


def calculate_change_similarity_score(changes: list[tuple]) -> float:
    # Assign weights to different change types (adjust as needed)
    weights = {'Insert': 1, 'Remove': 2}
    weighted_changes = sum(weights.get(change[1], 1) for change in changes)
    max_weighted_changes = len(changes) * max(weights.values())
    if max_weighted_changes == 0 or weighted_changes == 0:
        return 0.0
    return 1 - (weighted_changes / max_weighted_changes)


def print_report(report: list):
    """Print the comparison report.

    Args:
        report (list): List of dictionaries containing the comparison results as dictionaries with keys:
            - question
            - expected
            - generated
            - comparison_string
            - expected_result
            - generated_result
            - valid_query
            - same_results
            - query_token_similarity_score
            - changes
            - expected_error
            - generated_error
    """
    valid_queries = [comparison for comparison in report if comparison['valid_query']]
    queries_with_same_results = [comparison for comparison in report if comparison['same_results'] is True]
    queries_with_partially_matching_results = [
        comparison for comparison in report if 'partial' in str(comparison['same_results'])
    ]
    expected_errors = [comparison['expected_error'] for comparison in report if comparison['expected_error']]
    generated_errors = [comparison['generated_error'] for comparison in report if comparison['generated_error']]

    total_queries = len(report)
    num_valid_queries = len(valid_queries)
    num_queries_with_same_results = len(queries_with_same_results)
    num_queries_with_partially_matching_results = len(queries_with_partially_matching_results)

    percentage_valid_queries = (num_valid_queries / total_queries) * 100
    percentage_queries_with_same_results = (num_queries_with_same_results / total_queries) * 100

    # Calculate average number of changes per query
    all_changes = [result['changes'] for result in valid_queries]
    total_changes = sum(len(changes) for changes in all_changes)
    average_changes_per_query = total_changes / num_valid_queries if num_valid_queries > 0 else 0

    # Calculate distribution of change types
    change_types = Counter()
    for changes in all_changes:
        for change in changes:
            change_types[change[1]] += 1

    # Calculate change similarity score
    change_similarity_scores = [calculate_change_similarity_score(result['changes']) for result in valid_queries]
    average_change_similarity_score = mean(change_similarity_scores) if change_similarity_scores else 0.0

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
        print(f"Expected error: {result['expected_error']}")
        print(f"Generated error: {result['generated_error']}")
        print(f'Similarity score: {result["query_token_similarity_score"]:.2f}')
        print(f'Changes: {result["changes"]}')

    print(f"\nPercentage of valid queries: {percentage_valid_queries:.2f}%")
    print(f"Percentage of queries with same results: {percentage_queries_with_same_results:.2f}%")
    print(f"Average similarity score: {average_similarity_score:.2f}")
    print('------')

    print('Change statistics:')
    print(f"Total number of changes: {total_changes}")
    print(f"Average number of changes per query: {average_changes_per_query:.2f}")
    print(f"Change distribution: {change_types}")
    print(f"Average change similarity score: {average_change_similarity_score:.2f}")
    print('------')

    print(f"Number of valid queries: {num_valid_queries}/{total_queries}")
    print(f"Number of queries with same results: {num_queries_with_same_results}/{total_queries}")
    print(
        "Number of queries with partially matching results: "
        f"{num_queries_with_partially_matching_results}/{total_queries}"
    )
    print(f"Ratio of generated/expected errors: {len(generated_errors)}/{len(expected_errors)}")
    print("------")


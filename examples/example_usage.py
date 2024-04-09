import json
import argparse

from nl2sqleval import generate_report, print_report
from nl2sqleval.database import Database


def parse_arguments():
    parser = argparse.ArgumentParser(description='Evaluate SQL queries generated from natural language.')
    parser.add_argument(
        '--db_path',
        type=str,
        default='../data/database.sqlite',
        help='Path to the SQLite database file'
    )
    parser.add_argument(
        '--expected_queries_path',
        type=str,
        default='../data/examples_queries_test.json',
        help='Path to the JSON file containing the expected queries'
    )
    parser.add_argument(
        '--generated_queries_path',
        type=str,
        default='../data/generated_queries_test.json',
        help='Path to the JSON file containing the generated queries'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    database = Database(args.db_path)

    # Load the expected queries from the specified file
    with open(args.expected_queries_path, 'r') as f:
        expected_queries = json.load(f)

    # Load the generated queries from the specified file
    with open(args.generated_queries_path, 'r') as f:
        generated_queries = json.load(f)

    # Compare the queries
    report = generate_report(
        expected_queries, generated_queries, database
    )

    print_report(report)

    database.close()

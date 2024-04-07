import json

from nl2sqleval import generate_report, print_report
from nl2sqleval.database import Database


if __name__ == '__main__':
    db_path = "../data/database.sqlite"
    database = Database(db_path)

    # Load the expected queries from data/examples_queries_test.json
    with open('../data/examples_queries_test.json', 'r') as f:
        expected_queries = json.load(f)

    # Load the generated queries from data/generated_queries_test.json
    with open('../data/generated_queries_test.json', 'r') as f:
        generated_queries = json.load(f)

    # Compare the queries
    report = generate_report(
        expected_queries, generated_queries, database
    )

    print_report(report)

    database.close()

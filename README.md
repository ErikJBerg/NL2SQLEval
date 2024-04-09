# NL2SQLEval

NL2SQLEval is a Python library for evaluating and comparing SQL queries generated from natural language queries. It provides a framework for assessing the validity and correctness of generated SQL queries against expected ground truth queries.

## Features

- Compare generated SQL queries with expected ground truth queries
- Highlight differences between queries for easy identification
- Validate the syntax and executability of generated SQL queries
- Compare the results of generated queries with expected results
- Generate comprehensive evaluation reports
- Integrate with CI/CD pipelines for continuous monitoring and assessment

## Installation

To install NL2SQLEval we will enable pypi hosting, in the future you will be able to use pip:

```
pip install nl2sqleval
```

## Usage

### Example Scenario setup

#### Database Setup

The NL2SQLEval package requires a SQLite database to validate and compare SQL queries. For demonstration purposes, we'll use the "The History of Baseball" dataset from Kaggle.

1. Download the dataset from [https://www.kaggle.com/datasets/seanlahman/the-history-of-baseball](https://www.kaggle.com/datasets/seanlahman/the-history-of-baseball).

2. Extract the downloaded ZIP file and locate the `database.sqlite` file.

3. Place the `database.sqlite` file in a convenient location on your machine.

4. Update the `db_path` variable in your code to point to the location of the `database.sqlite` file:

   ```python
   db_path = "/path/to/your/database.sqlite"
   database = Database(db_path)

#### Running the Example

In the examples folder you will find a `example_usage.py` file that demonstrates the usage of the NL2SQLEval package. 
After example database setup seen above you can run this file to see the evaluation report.


### Basic Usage

```python
from nl2sqleval import SQLCompare

# Load the expected and generated queries from JSON files
expected_queries = json.load(open('examples_queries_test.json'))
generated_queries = json.load(open('generated_queries_test.json'))

# Create an instance of SQLCompare
comparer = SQLCompare(expected_queries, generated_queries)

# Compare the queries and generate a report
report = comparer.compare_queries()

# Print the evaluation report
print(report)
```

### Advanced Usage

```python
from nl2sqleval import SQLCompare

# Load the expected and generated queries from JSON files
expected_queries = json.load(open('examples_queries_test.json'))
generated_queries = json.load(open('generated_queries_test.json'))

# Create an instance of SQLCompare with custom options
comparer = SQLCompare(expected_queries, generated_queries, database='path/to/database.sqlite')

# Compare the queries and generate a detailed report
report = comparer.compare_queries(validate_syntax=True, compare_results=True)

# Save the report to a file
with open('evaluation_report.json', 'w') as f:
    json.dump(report, f, indent=2)
```

## Configuration

NL2SQLEval can be configured using the following options:

- `database`: Path to the SQLite database file for validating queries (default: `None`)
- `validate_syntax`: Whether to validate the syntax and executability of generated queries (default: `False`)
- `compare_results`: Whether to compare the results of generated queries with expected results (default: `False`)

## Examples

Examples of using NL2SQLEval can be found in the `examples` directory of the repository. The examples demonstrate different use cases and configurations.

## Contributing

Contributions to NL2SQLEval are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

NL2SQLEval is released under the [MIT License](https://opensource.org/licenses/MIT).

## Contact

For any questions or inquiries, please contact the maintainer:

- Name: [Your Name]
- Email: [Your Email]
- GitHub: [Your GitHub Profile]

Feel free to customize and expand upon this README template based on your specific library and its features.

## TODO:

For a production-ready solution, we need to add error handling, logging, and more robust input validation to handle different scenarios gracefully.

# NL2SQLEval

NL2SQLEval is a Python library for evaluating and comparing SQL queries generated from natural language queries. 
It provides a framework for assessing the validity and correctness of generated SQL queries against expected ground truth queries.

## Features

- Compare generated SQL queries with expected ground truth queries
- Highlight differences between queries for easy identification
- Validate the syntax and executability of generated SQL queries
- Compare the results of generated queries with expected results
  - Support for partial matching of query results
  - Detection of incomplete matching of query results
  - Handling of errors during query execution
  - Keeps metrics of raised exceptions during query execution
- Generate comprehensive evaluation reports

## Installation

To install NL2SQLEval, you can clone the source code repository and install it locally.
Use the following commands to install the package:

```bash
python setup.py install
```

## Usage

### Example Scenario Setup

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
from nl2sqleval.database import Database
from nl2sqleval.report import generate_report, print_report

# Load the expected and generated queries
expected_queries = [...]
generated_queries = [...]

# Create an instance of the Database class
db_path = "path/to/your/database.sqlite"
database = Database(db_path)

# Compare the queries and generate a report
report = generate_report(expected_queries, generated_queries, database)

# Print the evaluation report
print_report(report)
```

## Configuration

NL2SQLEval can be configured using the following options when calling the `compare_results` function:

- `ignore_row_order`: Whether to ignore the order of rows in the comparison of query results (default: `True`)
- `ignore_column_order`: Whether to ignore the order of columns in the comparison of query results (default: `True`)

## Contributing

Contributions to NL2SQLEval are welcome! 
If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

NL2SQLEval is released under the [MIT License](https://opensource.org/licenses/MIT).

## Contact

For any questions or inquiries, please contact the maintainer:

- Name: Erik Citterberg
- GitHub: [ErikJBerg](https://github.com/ErikJBerg)


## TODO:

For a production-ready solution, we need:
- add error handling, logging, and more robust input validation to handle different scenarios gracefully
- add detailed reporting: 
  - in result comparison, we should return more detailed information about the differences between the result sets (include the indices of the rows or columns that differ/provide a diff-like representation of the changes) 
  - in result comparison, we should also consider the order of the rows in the result set
  - in result comparison, we should consider the data types and formats of the columns in the result set
- add support for more database management systems (e.g., MySQL, PostgreSQL, SQL Server)
- implement analysis of correlation between changes and other metrics: 
  - explore the relationship between the changes and other metrics such as query validity, result similarity, and error occurrence. 
  - investigate whether certain types of changes are more likely to lead to invalid queries, different results, or errors.

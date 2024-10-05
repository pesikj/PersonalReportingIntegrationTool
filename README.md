# Personal Reporting Integration Tool

This repository is an integration tool that connects various personal data sources to streamline reporting. It includes connectors for tracking expenses, bank statements, project management, and fitness data.

## Project Overview
The tool aggregates data from multiple sources such as Fio Bank, Buxfer, Freedcamp, Garmin Connect, and more. It standardizes the data formats, enabling you to generate comprehensive personal reports across different domains (finance, health, and project tracking).

## Features
- **Expense Tracking**: Integrates with [Buxfer](https://buxfer.com/) to collect and categorize expenses.
- **Bank Statement Parsing**: Supports [Fio Bank](https://www.fio.cz/) statement parsing for financial tracking.
- **Project Management Data**: Uses [Freedcamp](https://freedcamp.com/) to import project-related metrics.
- **Shopping and Consumption**: Supports [Rohlik](https://www.rohlik.cz/) for grocery purchase data.

## Installation
To set up the project locally, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/pesikj/PersonalReportingIntegrationTool.git
    cd PersonalReportingIntegrationTool
    ```

2. Install the necessary dependencies:

    ```bash
    pip install -r requirements.txt
    ```


## Folder Structure
- **`BuxferConnector`**: Contains scripts for interacting with Buxfer API.
- **`FioBankStatementParser`**: Parses bank statements from Fio Bank.
- **`FreedcampConnector`**: Scripts to pull project data from Freedcamp.
- **`RohlikParser`**: Extracts shopping data from Rohlik.

## Contributing
Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -m 'Add feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact
For any questions or suggestions, feel free to reach out by opening an issue.

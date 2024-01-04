# Tapvalidator

TAP validation library (Python)

## TAP Validator Module

This Python module provides TAP (Table Access Protocol) validation capabilities.<br>
It allows validating and comparing two different TAP services or validating a single TAP service. <br>
The validation can cover various aspects of a TAP service, or it can focus specifically on validating the tables of a TAP service.

## Features

**Comparison**: Compare SQL queries between two TAP services.<br>
**Validation**: Validate a TAP service based on a list of queries.<br>
**Table Validation**: Validate the tables of a TAP service.<br>


## Installation

### Using Pip

    pip install -r requirements.txt
    pip install .

### Using Poetry

    poetry install


## Usage

    from tapvalidator.models.validation_config import ValidationConfiguration
    from tapvalidator.validators.tap_validator import TAPValidator

    # Configure the TAP services and other options
    config = ValidationConfiguration(
        first_service=TAPService(url="your_first_tap_service_url"),
        second_service=TAPService(url="your_second_tap_service_url"),
        alerter=AlerterFactory.get_alerter("your_slack_webhook_url"),
        alert_destination="your_slack_webhook_url",
        queries="path/to/your/query_file.txt",
    )

    # Create an instance of TAPValidator
    tap_validator = TAPValidator(config)

    # Run the desired action (COMPARISON, VALIDATION, TABLE_VALIDATION_ONLY)
    asyncio.run(tap_validator.run(mode="COMPARISON", fullscan=False))


Make sure to replace placeholder URLs and paths with your actual TAP service URLs, Slack webhook URL, and query file path.


## Command-Line Interface (CLI)

    python tap_validator.py --mode TABLE_VALIDATION_ONLY --tap_service your_first_tap_service_url  --slack_webhook your_slack_webhook_url

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the LICENSE file for details.

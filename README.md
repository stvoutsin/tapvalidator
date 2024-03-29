# Tapvalidator

TAP validation library (Python)

## TAP Validator Module

This Python module provides TAP (Table Access Protocol) validation capabilities.<br>
It allows validating and comparing two different TAP services or validating a single TAP service. <br>
The validation can cover various aspects of a TAP service, or it can focus specifically on validating the tables of a TAP service.

## Features

**Comparison**: Compare SQL queries between two TAP services.<br>
**Table Validation**: Validate the tables of a TAP service.<br>
**Validation**: Validate a TAP service, including Table Validation<br>

### Requirements

The library uses Dramatiq. This requires an instance of Redis to be running, and the URL needs to be passed in to the tapvalidator/settings.ini file
To start the workers run:

    dramatiq tasks

If using docker-compose to run the library, this step is handled for you.


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

    # Run the desired action (COMPARISON, VALIDATION, TABLE_VALIDATION)
    asyncio.run(tap_validator.run(mode="COMPARISON", fullscan=False))


Make sure to replace placeholder URLs and paths with your actual TAP service URLs, Slack webhook URL, and query file path.


## Command-Line Interface (CLI)

    python tap_validator.py --mode TABLE_VALIDATION_ONLY --tap_service your_first_tap_service_url  --slack_webhook your_slack_webhook_url

## Docker

The library can also be used via Docker: <br>
First create an .env file with the required params:

        TAP_SERVICE=http://your_tap_service_url
        MODE=your_mode_value
        SLACK_WEBHOOK=https://your_slack_webhook_url

Using docker-compose, run the stack:

    docker-compose --env-file .env up

Note: This will bring up Redis, Dramatiq and run the tapvalidator

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the LICENSE file for details.

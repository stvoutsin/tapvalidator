k# Tapvalidator

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



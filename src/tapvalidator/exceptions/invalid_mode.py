class InvalidRunMode(Exception):
    """Exception raised for run mode for Validator is not from known list

    Attributes:
        mode: The Run Mode
        message: explanation of the error
    """

    def __init__(self, mode, message="Unknown 'run mode' for TAPValidator"):
        self.mode = mode
        self.message = f"{message}: {mode}"
        super().__init__(self.message)

class PipelineException(Exception):
    pass


class PipelineExecutionAlreadyRunning(PipelineException):
    pass


class PipelineExecutionNotStarted(PipelineException):
    pass


class PipelineExecutionError(PipelineException):
    pass


class AzurePipelineAPIError(PipelineException):
    pass

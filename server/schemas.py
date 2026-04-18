from pydantic import BaseModel


class ParsedError(BaseModel):
    file: str
    line: int
    message: str


class PioRunnerOutput(BaseModel):
    returncode: int
    stdout: str
    stderr: str


class CommandResult(BaseModel):
    success: bool
    stdout: str = ""
    stderr: str = ""
    error: str | None = None


class BuildResult(CommandResult):
    errors: list[ParsedError]


class MonitorResult(BaseModel):
    success: bool
    output: str = ""
    error: str | None = None

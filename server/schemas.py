from pydantic import BaseModel


class ParsedError(BaseModel):
    file: str
    line: int
    message: str

class PioRunnerOutput(BaseModel):
    returncode: int | None
    stdout: str | None
    stderr: str | None
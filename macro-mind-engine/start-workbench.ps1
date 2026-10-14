$ErrorActionPreference = 'Stop'
$engineDirectory = $PSScriptRoot
$pythonExecutable = Join-Path $engineDirectory '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExecutable)) { throw 'Project Python environment not found: .venv\Scripts\python.exe' }
$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $engineDirectory 'src'
    & $pythonExecutable -m macromind.web @args
} finally {
    $env:PYTHONPATH = $previousPythonPath
}

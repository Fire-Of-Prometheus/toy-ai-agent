import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path, args=None):

    working_dir_abs = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
    
    # Will be True or False
    valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs

    if not valid_target_file:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(target_file):
        return f'Error: "{file_path}" does not exist or is not a regular file'

    _root, extension = os.path.splitext(target_file)
    if extension != ".py":
        return f'Error: "{file_path}" is not a Python file'

    command = ["python", target_file]
    
    if args:
        command.extend(args)
    
    try:
        complete_process = subprocess.run(command, capture_output=True, cwd=working_dir_abs, text=True, timeout=30)
        output = ''

        if complete_process.returncode != 0:
            output += f"Process exited with code {complete_process.returncode}"

        if not complete_process.stderr and not complete_process.stdout:
            output += "No output produced"

        if complete_process.stdout:
            output += f"STDOUT: {complete_process.stdout}"

        if complete_process.stderr:
            output += f"STDERR: {complete_process.stderr}"

        return output
    
    except Exception as e:
        print(f"Error: executing Python file: {e}")

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a python file indicated by the given file_path, with the specified arguments",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path of the python file that is to be executed.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="A list of arguments to be added to the python file execution (default is no arguments)",
                items=types.Schema(type=types.Type.STRING, description="Individual Argument for python execution"),
            ),
        },
        required=["file_path"],
    ),
)
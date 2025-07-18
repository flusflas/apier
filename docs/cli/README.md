# apier CLI Documentation

This document describes the command-line interface (CLI) for apier, which is used to generate API client libraries and manage OpenAPI specifications.

## Commands

### build

Generate an API client from one or more OpenAPI files.

**Usage:**
```
apier build --input <path> --output <dir> (--template <name> | --custom-template <path>) [OPTIONS]
```

**Description:**
- Takes one or more OpenAPI files or directories (via `--input`/`-i`).
- If a directory is provided, all files within will be used.
- If multiple OpenAPI files are provided, they will be merged before generating the client.
- You must provide either `--template` to use a built-in template (e.g., `python-tree`) or `--custom-template` to define the client structure.

**Options:**
- `-i, --input PATH`              One or more OpenAPI files or directories. **[required]**
- `-o, --output DIRECTORY`        Output directory for the generated API client code. **[required]**
- `-t, --template [python-tree]`  Template name for client generation (allowed: `python-tree`).
- `--custom-template PATH`        Path to a custom template directory for client generation.
- `--overwrite`                   Overwrite the output directory if it already exists.
- `-h, --help`                    Show help message and exit.

**Examples:**
- Generate a Python client using the `python-tree` built-in template:
  ```
  apier build -i openapi.yaml -o ./client --template python-tree
  ```
- Generate a client using a custom template:
  ```
  apier build -i openapi.yaml -o ./client --custom-template ./my_template
  ```
- Merge multiple OpenAPI files and generate a client:
  ```
  apier build -i spec1.yaml -i spec2.yaml -o ./client --template python-tree
  ```
- Overwrite the output directory if it exists:
  ```
  apier build -i openapi.yaml -o ./client --template python-tree --overwrite
  ```

---

### merge

Merge multiple OpenAPI files into a single specification.

**Usage:**
```
apier merge --input <path> --outout <path> [OPTIONS]
```

**Description:**
- Takes one or more OpenAPI files or directories (via `--input`/`-i`).
- If a directory is provided, all files within will be used.
- Merges the input files into a single OpenAPI file.
- The resulting merged file is written to the specified output path.

**Options:**
- `-i, --input PATH`   One or more OpenAPI files or directories to merge. **[required]**
- `-o, --outout PATH`  Output file path for the merged OpenAPI spec. **[required]**
- `--overwrite`        Overwrite the output file if it already exists.
- `-h, --help`         Show help message and exit.

**Examples:**
- Merge two OpenAPI files into a single YAML file:
  ```
  apier merge -i spec1.yaml -i spec2.yaml -o merged.yaml
  ```
- Merge all OpenAPI files in a directory:
  ```
  apier merge -i ./openapi_specs/ -o merged.yaml
  ```
- Overwrite the output file if it exists:
  ```
  apier merge -i spec1.yaml -i spec2.yaml -o merged.yaml --overwrite
  ```

---

For more information on templates and advanced usage, see the main documentation.

# AWS S3 CLI

A simple command-line interface (CLI) for managing AWS S3 buckets using Python and Boto3.

## Prerequisites

- Python 3.6 or later
- AWS account with S3 access
- [Poetry](https://python-poetry.org/)

## Installation

1. Clone this repository:

```bash
git clone git@github.com:IrakliDevelop/s3-cli-python.git;
cd s3-cli
```

2. Install the dependencies using Poetry:

```bash
poetry install
```

3. Create a `.env` file in the project directory with your AWS credentials:

```bash
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=your_aws_region
```

Replace `your_access_key_id`, `your_secret_access_key`, and `your_aws_region` with your actual AWS credentials and region.

## Usage

Run the CLI using the following command:
```bash
poetry run python s3_cli.py <command> [arguments]
```

Replace `<command>` with one of the available commands and provide any required arguments.

### Available Commands

- `list`: List all S3 buckets.
- `create <bucket_name>`: Create a new S3 bucket with the given name.
- `delete <bucket_name>`: Delete an existing S3 bucket with the given name.
- `upload-small <file_path> <bucket_name> [--object-name <object_name>]`: Upload a small file to an S3 bucket.
- `upload-large <file_path> <bucket_name> [--object-name <object_name>] [--part-size <part_size>]`: Upload a large file to an S3 bucket.
- `set-lifecycle-policy <bucket_name> [--days <days>]`: Create a lifecycle policy to delete objects after a specified number of days.

For more information on the arguments and options for each command, run:
```bash
poetry run python s3_cli.py <command> --help
```

Replace `<command>` with one of the available commands.


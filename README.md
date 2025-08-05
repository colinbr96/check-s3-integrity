# check-s3-integrity
Check S3 object integrity against a local file.

## Setup

1. Create Python virtualenv (recommended):

   `python -m venv venv`

2. Activate the virtualenv:

   `. venv/Scripts/activate`

3. Verify that you're in the virtualenv:

   `pip -V`

   It should contain `check-s3-integrity/venv` in the path.

4. Install dependencies:

   `pip install -r requirements.txt`


## Usage

```sh
python check_s3_integrity.py --help
```

Example:

```sh
python check_s3_integrity.py --bucket MyFiles --key Backup.zip --local-file "/tmp/Backup.zip"
```

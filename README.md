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
python check_s3_integrity.py --bucket my-photo-backups --key Photos.zip --local-file "/home/me/Documents/Photos.zip"
```

Example output:

```text
Local File:         /home/me/Documents/Photos.zip
Local File Size:    10205763332 bytes (9.5 GiB)

S3 Object:          s3://my-photo-backups/Photos.zip
ETag:               d77db227ef828cb6be25399caff44790-595
Object Size:        10205763332 bytes (9.5 GiB)
Total Parts:        595
Part Size:          17179870 bytes (16.4 MiB)

Calculating ETag |██████████████████████████████████████████████████| 100.0% Complete
Integrity check passed. Local file matches S3 object.
```

import argparse
import hashlib
import json
import os
import sys

import boto3
import botocore


s3 = boto3.client('s3')


def get_human_readable_size(size: float) -> str:
    """Convert bytes to a human-readable format."""
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PiB"


def get_object_part_head(bucket_name: str, object_key: str, part_number: int):
    response = s3.head_object(Bucket=bucket_name, Key=object_key, PartNumber=part_number)
    return response


def get_size_of_local_file(local_file_path: str) -> int:
    return os.path.getsize(local_file_path)


def print_progress_bar(iteration, total, msg = '', length = 50):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = '█' * filledLength + '-' * (length - filledLength)
    print(f'\r{msg} |{bar}| {percent}% Complete', end = "\r")

    # Print empty line on complete
    if iteration >= total:
        print()


def get_etag_of_local_file(local_file_path: str, chunk_size: int, local_file_size: int) -> str:
    md5s = []

    try:
        with open(local_file_path, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                md5 = hashlib.md5(data)
                print_progress_bar(f.tell(), local_file_size, msg='Calculating ETag')
                md5s.append(md5)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(1)

    if len(md5s) == 1:
        return md5s[0].hexdigest()

    digests = b''.join(m.digest() for m in md5s)
    return f"{hashlib.md5(digests).hexdigest()}-{len(md5s)}"


def parse_args():
    parser = argparse.ArgumentParser(description='Check S3 object integrity against a local file.')
    parser.add_argument('--bucket', type=str, required=True, help='S3 bucket name')
    parser.add_argument('--key', type=str, required=True, help='S3 object key')
    parser.add_argument('--local-file', type=str, required=True, help='Path to the local file')
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        local_file_size = get_size_of_local_file(args.local_file)
        print(f"Local File:      {args.local_file}")
        print(f"Local File Size: {local_file_size} bytes")
        print()
    except FileNotFoundError:
        print(f"Local file not found: '{args.local_file}'")
        sys.exit(1)

    try:
        first_part_metadata = get_object_part_head(args.bucket, args.key, 1)
        etag = json.loads(first_part_metadata['ETag'])
        object_size = int(first_part_metadata['ContentRange'].split('/')[1])
        display_size = get_human_readable_size(object_size)
        total_parts = first_part_metadata['PartsCount']
        part_size = first_part_metadata['ContentLength']

        print(f"S3 Object:       s3://{args.bucket}/{args.key}")
        print(f"ETag:            {etag}")
        print(f"Object Size:     {object_size} bytes")
        print(f"Display Size:    {display_size}")
        print(f"Total Parts:     {total_parts}")
        print(f"Part Size:       {part_size} bytes")
        print()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"S3 object not found: 's3://{args.bucket}/{args.key}'")
        else:
            print(f"Error fetching S3 object metadata: {e}")
        sys.exit(1)

    if local_file_size != object_size:
        print(f"Size mismatch: Local file size {local_file_size} bytes, S3 object size {object_size} bytes.")
        sys.exit(1)

    local_etag = get_etag_of_local_file(args.local_file, part_size, local_file_size)
    if local_etag != etag:
        print(f"ETag mismatch: Local file ETag: {local_etag}, S3 object ETag: {etag}")
        sys.exit(1)

    print("Integrity check passed. Local file matches S3 object.")


if __name__ == "__main__":
    main()

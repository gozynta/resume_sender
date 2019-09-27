#!/usr/bin/env python3

# ******************************************************************************
#  All code written for this project                                           *
#  Copyright 2013 - 2019                                                       *
#  by Gozynta, LLC.                                                            *
#  All Rights Reserved                                                         *
# ******************************************************************************
import hashlib
import mimetypes

import click
import requests

from util import load_cache

BASE_URL = 'https://job-application.gozynta.com'


@click.command()
@click.argument('fullname')
@click.argument('email')
@click.argument('resume_path', type=click.Path(exists=True))
def main(fullname: str, email: str, resume_path: str):
    click.echo('Sending application for "{} <{}>"'.format(fullname, email))

    applicant_id = submit_applicant(fullname, email)
    # click.echo(applicant_id)

    sha256hash = upload_resume(applicant_id, resume_path)
    click.echo('Resume uploaded successfully, thank you for your application. sha256:{}'.format(sha256hash))


def submit_applicant(fullname: str, email: str) -> str:
    """
    Submit applicant's name and email, and get the resultant applicant_id.

    :param fullname: Full name of candidate
    :param email: Email address of candidate
    :return: applicant id - to be used as filename for the upload step.
    """
    data = dict(
        applicantEmail=email,
        applicantName=fullname
    )

    with load_cache() as applicant_cache:
        if email in applicant_cache:
            applicant_id = applicant_cache[email]
        else:
            r = requests.post(BASE_URL + '/submit_applicant_info', json=data)
            if r.status_code != 200:
                raise click.ClickException(r.text)
            applicant_id = r.json()
            applicant_cache[email] = applicant_id

    return applicant_id


def upload_resume(applicant_id, resume_path, content_type=None):
    """
    Upload the applicant's resume file.

    :param applicant_id: From submit_application()
    :param resume_path: Path to resume file that you want to submit.
    :param content_type: Optional - content type of the resume file (otherwise guessed from filename).
    :return: the sha256 hash of the uploaded file
    """
    blocksize = 8 * 1024  # Read large files in 8k blocks

    if not content_type:
        content_type = mimetypes.guess_type(resume_path, strict=False)[0]

    file_handle = click.open_file(resume_path, mode='rb')

    # Calculate hash to check that the file uploaded successfully
    file_hash = hashlib.sha256()
    for block in iter(lambda: file_handle.read(blocksize), b""):
        file_hash.update(block)

    # Upload the file
    file = (applicant_id, file_handle, content_type)
    response = requests.post(
        BASE_URL + '/upload',
        files={'file': file})

    if response.status_code == 418:  # I'm a teapot
        raise click.ClickException(response.text + ' Perhaps there\'s a small bug in this program? <nudge><nudge>')
    elif response.status_code != 200:  # All other non-success codes (unexpected errors)
        raise click.ClickException(response.text)

    # Confirm remote hash is the same as locally calculated hash.
    if file_hash.hexdigest() != response.text:
        raise click.ClickException('Error: Hash mismatch.  File upload error?')

    return response.text


if __name__ == '__main__':
    main()

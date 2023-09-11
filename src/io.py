import argparse
import sys
from os import getenv
from typing import List

DEFAULT_GITHUB_API_URL = 'https://api.github.com'


class Options:
    def __init__(
            self,
            ignore_branches: list[str],
            last_commit_age_days: int,
            allowed_prefixes: list[str],
            github_token: str,
            github_repo: str,
            dry_run: bool = True,
            github_base_url: str = DEFAULT_GITHUB_API_URL
    ):
        self.ignore_branches = ignore_branches
        self.last_commit_age_days = last_commit_age_days
        self.allowed_prefixes = allowed_prefixes
        self.github_token = github_token
        self.github_repo = github_repo
        self.dry_run = dry_run
        self.github_base_url = github_base_url

    def validate(self):
        errors = []
        if self.github_token is None:
            errors.append("github_token is undefined")

        if self.github_repo is None:
            errors.append("github_repo is undefined")

        if self.github_base_url is None:
            errors.append("github_base_url is undefined")

        if self.last_commit_age_days is None:
            errors.append("last_commit_age_days is undefined")

        if len(errors) > 0:
            raise RuntimeError(f"Errors found while parsing input options: {errors}")


class InputParser:
    @staticmethod
    def get_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser('Github Actions Delete Old Branches')

        parser.add_argument("--ignore_branches", help="Comma-separated list of branches to ignore")

        parser.add_argument("--allowed_prefixes",
                            help="Comma-separated list of prefixes a branch must match to be deleted")
        parser.add_argument("--github_token")

        parser.add_argument(
            "--github_base_url",
            default=DEFAULT_GITHUB_API_URL,
            help="The API base url to be used in requests to GitHub Enterprise"
        )

        parser.add_argument(
            "--last_commit_age_days",
            help="How old in days must be the last commit into the branch for the branch to be deleted",
            type=int,
            required=True,
        )

        parser.add_argument(
            "--dry_run",
            choices=["yes", "no"],
            default="yes",
            help="Whether to delete branches at all. Defaults to 'yes'. Possible values: yes, no (case sensitive)"
        )

        return parser.parse_args()

    def parse_input(self) -> Options:
        args = self.get_args()

        branches_raw: str = args.ignore_branches
        ignore_branches = branches_raw.split(',')
        if ignore_branches == ['']:
            ignore_branches = []

        allowed_prefixes = args.allowed_prefixes.split(',')
        if allowed_prefixes == ['']:
            allowed_prefixes = []

        # Dry run can only be either `true` or `false`, as strings due to github actions input limitations
        dry_run = False if args.dry_run == 'no' else True

        options = Options(
            ignore_branches=ignore_branches,
            last_commit_age_days=args.last_commit_age_days,
            allowed_prefixes=allowed_prefixes,
            dry_run=dry_run,
            github_token=args.github_token,
            github_repo=getenv('GITHUB_REPOSITORY'),
            github_base_url=args.github_base_url
        )

        options.validate()

        return options

def format_output(output_strings: dict) -> None:
    file_path = getenv('GITHUB_OUTPUT')

    with open(file_path, "a") as gh_output:
        for name, value in output_strings.items():
            gh_output.write(f'{name}={value}\n')

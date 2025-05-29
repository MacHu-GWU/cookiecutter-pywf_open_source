# -*- coding: utf-8 -*-

"""
A utility script to update GitHub release and tag using the latest commit SHA on main branch.

Requirements::

    pip install "PyGithub>=2.5.0,<3.0.0"
"""

import typing as T
import dataclasses
from functools import cached_property

from github import Github, GithubException, Repository, GitTag, GitRef, GitRelease

__version__ = "0.1.1"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__license__ = "MIT"


@dataclasses.dataclass
class GitHubReleaseManager:
    version: str = dataclasses.field()
    github_account: str = dataclasses.field()
    github_repo_name: str = dataclasses.field()
    github_token: str = dataclasses.field()
    log_func: T.Callable = dataclasses.field(default=print)

    @cached_property
    def gh(self) -> "Github":
        return Github(self.github_token)

    @cached_property
    def repo(self) -> "Repository":
        return self.gh.get_repo(f"{self.github_account}/{self.github_repo_name}")

    @cached_property
    def repo_default_branch(self) -> str:
        return self.repo.default_branch

    def get_latest_commit_sha(self) -> str:
        return self.repo.get_branch(self.repo_default_branch).commit.sha

    @property
    def release_name(self) -> str:
        return self.version

    @property
    def tag_name(self) -> str:
        return self.version

    def get_git_tag_and_ref(self) -> tuple[
        T.Optional["GitTag"],
        T.Optional["GitRef"],
    ]:
        try:
            ref = self.repo.get_git_ref(f"tags/{self.tag_name}")
        except GithubException as e:
            if e.status == 404:
                return (None, None)
            else:  # pragma: no cover
                raise e
        except Exception as e:
            raise e

        tag_sha = ref.object.sha

        try:
            tag = self.repo.get_git_tag(tag_sha)
        except GithubException as e:
            if e.status == 404:
                return (None, ref)
            else:  # pragma: no cover
                raise e
        except Exception as e:
            raise e

        return (tag, ref)

    def get_git_release(self) -> T.Optional["GitRelease"]:
        try:
            return self.repo.get_release(self.release_name)
        except GithubException as e:
            if e.status == 404:
                return None
            else:  # pragma: no cover
                raise e
        except Exception as e:  # pragma: no cover
            raise e

    def is_tag_latest_on_main(self) -> tuple[
        bool,
        T.Optional["GitTag"],
        T.Optional["GitRef"],
        T.Optional[str],
    ]:
        """
        Check if the tag is the latest on the main branch.

        :returns: a tuple of four elements:
        """
        latest_commit_sha = self.get_latest_commit_sha()
        tag, ref = self.get_git_tag_and_ref()
        if tag is None:
            return (False, tag, ref, latest_commit_sha)
        else:
            flag = tag.object.sha == latest_commit_sha
            return (flag, tag, ref, latest_commit_sha)

    def clean_up_existing_release(self) -> bool:
        """
        :returns: a boolean flag to indicate whether the operation is performed.
        """
        release = self.get_git_release()
        if release is not None:
            release.delete_release()
            return True
        else:
            return False

    def clean_up_existing_tag(self) -> bool:
        """
        :returns: a boolean flag to indicate whether the operation is performed.
        """
        try:
            ref = self.repo.get_git_ref(f"tags/{self.tag_name}")
            ref.delete()
            return True
        except GithubException as e:
            if e.status == 404:
                return False
            else:  # pragma: no cover
                raise e

    def create_tag(
        self,
        latest_commit_sha: T.Optional[str] = None,
    ) -> tuple["GitTag", "GitRef"]:
        if latest_commit_sha is None:
            latest_commit_sha = self.get_latest_commit_sha()
        tag = self.repo.create_git_tag(
            tag=self.release_name,
            message=f"Release {self.release_name}",
            object=latest_commit_sha,
            type="commit",
        )
        ref = self.repo.create_git_ref(
            ref=f"refs/tags/{self.tag_name}",
            sha=tag.sha,
        )
        return tag, ref

    def create_release(self) -> "GitRelease":
        return self.repo.create_git_release(
            tag=self.tag_name,
            name=self.release_name,
            message=f"Release {self.release_name}",
        )

    def update_release(self) -> tuple[
        bool,
        T.Optional["GitTag"],
        T.Optional["GitRef"],
        T.Optional["GitRelease"],
    ]:
        """
        Update the GitHub release and tag.

        :returns: a boolean flag to indicate whether the operation is performed.
        """
        self.log_func("Checking if the tag is latest on main branch...")
        (flag, tag, ref, latest_commit_sha) = self.is_tag_latest_on_main()
        self.log_func(
            f"Tag = {tag}, Ref = {ref}, Latest commit SHA = {latest_commit_sha}"
        )
        if flag is True:
            self.log_func("Tag is latest on main branch, no need to update.")
            return False, tag, ref, None
        else:
            self.log_func("Tag is not latest on main branch, updating ...")
        self.log_func("Cleaning up existing release and tag ...")
        self.clean_up_existing_release()
        if tag is not None:
            self.log_func("Cleaning up existing tag ...")
            self.clean_up_existing_tag()
        self.log_func("Creating new tag ...")
        tag, ref = self.create_tag(latest_commit_sha=latest_commit_sha)
        self.log_func("Creating new release ...")
        release = self.create_release()
        self.log_func("Done!")
        return True, tag, ref, release


if __name__ == "__main__":
    # ===== Set parameter here =====
    from home_secret import hs

    manager = GitHubReleaseManager(
        version="0.1.1",
        github_account="MacHu-GWU",
        github_repo_name="cookiecutter-pywf_open_source",
        github_token=hs.v("providers.github.accounts.sh.users.sh.secrets.dev.value"),
    )
    manager.update_release()

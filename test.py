import os, shutil, os.path
from git import Repo


#target_dir = os.getcwd() + "\\repodir"
target_dir = os.getcwd() + "/repodir"
git_url = "https://e0358664:dPGnbysq6N7pyLg_fMsu@gitlab-its.sanofi.com/salt/certificates.git"


def clone(target_dir, git_url):
    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir)
        print(f"removing {target_dir}")
    os.mkdir(target_dir)
    print("dir created")
    Repo.clone_from(git_url, target_dir)

clone(target_dir, git_url)

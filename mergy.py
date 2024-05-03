import os
import sys
import shutil
from tempfile import TemporaryDirectory
import subprocess
from os import path
from urllib.request import urlretrieve


OUTPUT_REPO = path.abspath("./mono-repo/")
GFR_PATH = path.abspath("./git-filter-repo")
GFR_URL = "https://raw.githubusercontent.com/newren/git-filter-repo/main/git-filter-repo"


def bootstrap_repo():
    while True:
        try:
            os.mkdir(OUTPUT_REPO)
            run_repo_cmd("git", "init")
            break
        except FileExistsError:
            shutil.rmtree(OUTPUT_REPO)


def run_repo_cmd(*cmd):
    subprocess.run(
        cmd,
        cwd=OUTPUT_REPO,
        check=True
    )

def run_cmd(cwd, *cmd):
    subprocess.run(
        cmd,
        cwd=cwd,
        check=True
    )

def make_wip():
    try:
        os.mkdir(WIP_DIR)
    except FileExistsError:
        clear_wip()
        os.mkdir(WIP_DIR)
    run_wip_cmd("git", "init")

def clear_wip():
    shutil.rmtree(WIP_DIR)


def merge_and_move(remote, name, branch):
    with TemporaryDirectory() as tmp_dir:
        run_cmd(tmp_dir, "git", "init")

        run_cmd(tmp_dir, "git", "remote", "add", name, remote)
        run_cmd(tmp_dir, "git", "fetch", name)
        run_cmd(tmp_dir, "git", "merge", "--allow-unrelated-histories", f"{name}/{branch}", "--no-edit")
        run_cmd(tmp_dir, "git", "remote", "remove", name)

        repo_subdir = path.join(name, branch)
        run_cmd(
            tmp_dir,
            sys.executable,
            GFR_PATH,
            "--to-subdirectory-filter",
            f"{repo_subdir}/",
            "--force"
        )

        run_repo_cmd("git", "remote", "add", "wip", tmp_dir)
        run_repo_cmd("git", "fetch", "wip")
        run_repo_cmd(
            "git",
            "merge",
            "--allow-unrelated-histories",
            "wip/master",
            "--no-edit",
            "-m",
            f"restructured subtree merge in {name}/{branch}",
        )
        run_repo_cmd("git", "remote", "remove", "wip")


def parse_file(file_path):
    triplets = []
    with open(file_path, "r") as fh:
        base_path = next(fh).strip()
        for line in fh:
            l = line.split()
            owner_and_name = l[0]
            if len(l) < 2:
                branch = "master"
                print(f"No branch specified for {owner_and_name}, defaulting to {branch}")
            else:
                branch = l[1]
            name = owner_and_name.replace("/", "_")
            triplets.append((f"{base_path}/{owner_and_name}.git", name, branch))
    return triplets


if __name__ == "__main__":
    if not path.isfile(GFR_PATH):
        urlretrieve(GFR_URL, GFR_PATH)

    repo_triplets = parse_file(sys.argv[1])
    print("=== Repos ===")
    for _, name, branch in repo_triplets:
        print(name, branch)

    bootstrap_repo()
    for remote, name, branch in repo_triplets:
        print("\n==>", name, branch)
        merge_and_move(remote, name, branch)

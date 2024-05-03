import os
import sys
import shutil
import subprocess
from os import path


OUTPUT_REPO = path.abspath("./mono-repo/")
WIP_DIR_NAME = "wip-tmp"
WIP_DIR = path.join(OUTPUT_REPO, WIP_DIR_NAME)


def bootstrap_repo():
    while True:
        try:
            os.mkdir(OUTPUT_REPO)
            os.mkdir(WIP_DIR)
            run_cmd("git", "init")
            break
        except FileExistsError:
            shutil.rmtree(OUTPUT_REPO)


def unpack_repo():
    contents = os.listdir(WIP_DIR)
    for c in contents:
        run_cmd("git", "mv", path.join(WIP_DIR, c), ".")
    os.rmdir(WIP_DIR)
    run_cmd("git", "commit", "-m", f"unpack tmp folder {WIP_DIR_NAME}")


def run_cmd(*cmd):
    subprocess.run(
        cmd,
        cwd=OUTPUT_REPO,
        check=True
    )


def merge_and_move(remote, name, branch):
    run_cmd("git", "remote", "add", name, remote)
    run_cmd("git", "fetch", name, "--tags")
    run_cmd("git", "merge", "--allow-unrelated-histories", f"{name}/{branch}", "--no-edit")
    run_cmd("git", "remote", "remove", name)

    repo_subdir = path.join(WIP_DIR, name, branch)
    os.makedirs(repo_subdir)
    contents = os.listdir(OUTPUT_REPO)
    contents = filter(lambda s: s != ".git" and s != WIP_DIR_NAME, contents)
    for c in contents:
        run_cmd("git", "mv", c, repo_subdir+"/")
    run_cmd("git", "commit", "-m", f"move {name}/{branch} into tmp folder {WIP_DIR_NAME}")


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
    repo_triplets = parse_file(sys.argv[1])
    print("Will try to fetch:")
    for _, name, branch in repo_triplets:
        print(name, branch)

    bootstrap_repo()
    for remote, name, branch in repo_triplets:
        merge_and_move(remote, name, branch)
    unpack_repo()

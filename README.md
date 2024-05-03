# Mergy
A small python script to merge several git repositories into one repository,
with each sub-repository restructured into folders and with modified history to
reflect the new structure. This keeps all git commits as per the
sub-repositories, but pointing to the new path.

## Usage
Requires `python 3` (tested on 3.12) and `git`. Run with:

```shell
python merge.py <path to repository list>
```
The final repository will be contained in a subfolder `mono-repo`.

The repository list needs to be in the following format:
```
<base URL path>
<repository> <branch>
<repository> <branch>
...
```

Example:
```
git@github.com:
Oxel/mergy master
Oxel/mergy testing
```

A longer example can be found in [repo.txt](./repos.txt).

Currently, only one base URL (host server) is possible.

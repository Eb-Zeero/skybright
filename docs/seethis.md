| Configuration name | Infix |
| --- | --- |
| development | `DEV_` |
| testing | `TEST_` |
| production | no prefix |

# Installation

## On your machine for development

Download the content of the repository as a zip file and extract the file into a directory of your choice. Don't clone the repository, unless you are actually planning to update the start setup rather than to create a new Flask site.

You should then put the new directory (let's call it `/path/to/site`) under version control.

```bash
cd /path/to/site
git init
```

Make sure you've installed [Java](http://www.oracle.com/technetwork/java/javase/downloads/index-jsp-138363.html) (required for building bundles of static files with Flask-Assets) and Python 3. Create a virtual environment

```bash
python3 -m venv venv
```
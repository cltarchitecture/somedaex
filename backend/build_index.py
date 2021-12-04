from importlib import import_module
from inspect import isabstract, isclass
from os import scandir
from pathlib import Path
from somedaex.pipeline.task import Task
from termcolor import cprint


PACKAGE_PATH = "somedaex/task_types"
PACKAGE_NAME = "somedaex.task_types"
INDEX_VAR_NAME = "task_types"


def accepted(key):
    cprint(f"  ✔︎ {key}", "green")


def rejected(key, reason):
    cprint(f"  ✘ {key} ({reason})", "red")


def findTasksInFile(path: Path, package: str):
    class_names = []
    module = import_module("." + path.stem, package)
    print(module.__name__ + ":")

    for key in dir(module):
        attr = getattr(module, key)
        if not isclass(attr):
            # rejected(key, 'not a class')
            pass
        elif not issubclass(attr, Task):
            rejected(key, "not a Task")
        elif isabstract(attr):
            rejected(key, "abstract")
        else:
            class_names.append(key)
            accepted(key)

    if len(class_names) > 0:
        return {module.__name__: class_names}

    return {}


def findTasksInDir(path: Path, package: str):
    tasks = {}
    for entry in scandir(path):
        entry_path = Path(entry.path)

        if entry.is_dir():
            subpackage = package + "." + entry.name
            tasks.update(findTasksInDir(entry_path, subpackage))

        elif entry.is_file() and entry.path.endswith(".py"):
            tasks.update(findTasksInFile(entry_path, package))

    return tasks


def copy_doc(path: Path, out):
    with open(path, "r") as docfile:
        doc = docfile.read()
        doc = doc.replace('"""', '\\"\\"\\"')
        out.write(f'"""{doc}"""\n\n')


this_script = Path(__file__)
backend_folder = this_script.parent
tasks_folder = backend_folder / PACKAGE_PATH
index_file = tasks_folder / "__init__.py"
documentation_file = tasks_folder / "__doc__.txt"

index_file.unlink(missing_ok=True)
tasks = findTasksInDir(tasks_folder, PACKAGE_NAME)

import_lines = ["from ..pipeline import TypeIndex"]
index_lines = [f"{INDEX_VAR_NAME} = TypeIndex()"]

for pkg in sorted(tasks.keys()):
    names = sorted(tasks[pkg])
    name_list = ", ".join(names)
    relative_pkg = pkg.replace("somedaex.task_types", "")
    import_lines.append(f"from {relative_pkg} import {name_list}")
    for name in names:
        index_lines.append(f"{INDEX_VAR_NAME}.add({name})")

with open(index_file, "w") as f:
    copy_doc(documentation_file, f)
    f.write("\n".join(import_lines))
    f.write("\n\n")
    f.write("\n".join(index_lines))
    f.write("\n")

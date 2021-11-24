from importlib import import_module
from inspect import isabstract, isclass
from os import scandir
from pathlib import Path
from pipeline.task import Task
from termcolor import cprint


PACKAGE_PATH = "lib/task_types"
PACKAGE_NAME = "task_types"
INDEX_VAR_NAME = "task_types"


def accepted(key):
    cprint("  ✔︎ {}".format(key), "green")


def rejected(key, reason):
    cprint("  ✘ {} ({})".format(key, reason), "red")


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
        out.write('"""{}"""\n\n'.format(doc))


this_script = Path(__file__)
backend_folder = this_script.parent.parent
tasks_folder = backend_folder / PACKAGE_PATH
index_file = tasks_folder / "__init__.py"
documentation_file = tasks_folder / "__doc__.txt"

index_file.unlink(missing_ok=True)
tasks = findTasksInDir(tasks_folder, PACKAGE_NAME)

import_lines = ["from pipeline import TypeIndex"]
index_lines = ["{} = TypeIndex()".format(INDEX_VAR_NAME)]

for pkg in sorted(tasks.keys()):
    names = sorted(tasks[pkg])
    import_lines.append("from {} import {}".format(pkg, ", ".join(names)))
    for name in names:
        index_lines.append("{}.add({})".format(INDEX_VAR_NAME, name))

with open(index_file, "w") as f:
    copy_doc(documentation_file, f)
    f.write("\n".join(import_lines))
    f.write("\n\n")
    f.write("\n".join(index_lines))
    f.write("\n")

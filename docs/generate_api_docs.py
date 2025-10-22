from mkdocs_gen_files import open as open_file
from pathlib import Path
import pkgutil

package = "prenatalppkt"
for module in pkgutil.walk_packages([package]):
    mod_name = f"{package}.{module.name}"
    path = Path("api", f"{module.name}.md")
    with open_file(path, "w") as f:
        print(f"::: {mod_name}", file=f)

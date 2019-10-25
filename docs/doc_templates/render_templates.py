import os
from pathlib import Path
import subprocess
from jinja2 import Environment, FileSystemLoader, select_autoescape

templates_dir = "."
target_dir = ".."

# All template file names must end with .md
template_file_names = [ file_name for file_name in os.listdir(templates_dir) if ".md" in file_name ]
print(template_file_names)
render_env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(["html", "xml"])
)

def get_help_message(shell_script_name):
    process = subprocess.Popen([shell_script_name, "-h"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()
    return stdout.decode("ascii")

def save_rendered_doc_file(template_file_name, contents):
    target_file_name = os.path.join(target_dir, template_file_name)
    with open(target_file_name, "w") as target_file:
        target_file.write(contents)

meshmerizeme_limitations = """
MeshmerizeMe does not currently support SVG files containing any of the following:
- Nested viewBoxes/viewPorts
- Nested `<svg>` elements
- Use of the "preserveAspectRatio" attribute
- Use of units other than pixels
- `<use>`, `<symbol>`, and `<def>` tags
"""

render_params = {
    "meshmerizeme_help_message" : get_help_message("MeshmerizeMe"),
    "contourizeme_help_message" : get_help_message("ContourizeMe"),
    "meshmerizeme_limitations"  : meshmerizeme_limitations
}

for template_file_name in template_file_names:
    template = render_env.get_template(template_file_name)
    rendered_contents = template.render(render_params=render_params)
    save_rendered_doc_file(template_file_name, rendered_contents)

import os
import sys
import json
import zipfile
from pathlib import Path

import click
from gitignore_parser import parse_gitignore

DEFAULT_NAME = f"{Path('.').name}.zip"

@click.group()
def cli():
    pass

@click.group()
def versioning():
    """Version related commands."""

@click.group()
def packaging():
    """Packaging related commands."""

@packaging.command()
@click.option('--package-name', '-n', default=f"{Path.cwd().name}.zip", help='Zip file name.')
@click.option('--ignore-file', '-i', default='./ignore-packaging', help='path to file containing ignore patterns.')
def package(package_name=f"{Path.cwd().name}.zip", ignore_file='./ignore-packaging'):
    if not Path(ignore_file).exists():
        click.echo(f"Unable to locate {ignore_file}!!"
        sys.exit(1)
    matches = parse_gitignore(ignore_file, base_dir='.')

    staging = []
    for path in Path(".").glob("**/*"):
        if matches(str(path.resolve())):
            continue
        staging.append(path)

    def zipdir(root, ziph):
        for path in staging:
            if path.name != package_name:
                click.echo(f"Zipping: {path.relative_to('.')}")
                ziph.write(os.path.join(root, path.relative_to(".")), path.relative_to("."))
        
    zipf = zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED)
    zipdir(os.getcwd(), zipf)
    zipf.close()
    click.echo(f"Saved {package_name}")


@versioning.command()
def version():
    with open('./plugin.json', 'r') as f:
        plugin = json.load(f)
    click.echo(plugin['Version'])

@versioning.command()
@click.argument("new_version")
def update_version(new_version):
    with open('./plugin.json', 'r') as f:
        plugin = json.load(f)
    plugin['Version'] = new_version
    with open('./plugin.json', 'w') as f:
        f.write(json.dumps(plugin, indent=4))
    click.echo(f"Changed version to: {plugin['Version']}")

if __name__ == "__main__":
    cli = click.CommandCollection(sources=[packaging, versioning])
    cli()

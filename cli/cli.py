import os
import typer
from typing import List, Optional
from dotenv import load_dotenv
from yaml_env_var_parser import load

load_dotenv()

app = typer.Typer()

with open("lifecycle.yaml", "r") as file:
    parsed = load(file)
    scripts = parsed


def _container_up(
    container: str, recreate: bool = typer.Option(False, "--recreate", "-r")
):
    if scripts.get(container, {}).get("pre_up"):
        for script in scripts[container]["pre_up"]:
            os.system(script)

    os.system(f"docker compose up -d {container} --force-recreate={recreate}")

    if scripts.get(container, {}).get("post_up"):
        for script in scripts[container]["post_up"]:
            os.system(script)


def _server_up(recreate: bool = typer.Option(False, "--recreate", "-r")):
    pre_up_all = []
    post_up_all = []
    
    for key, value in scripts.items():
        if scripts[key].get("pre_up"):
            for script in scripts[key]["pre_up"]:
                pre_up_all.append(script)
        if scripts[key].get("post_up"):
            for script in scripts[key]["post_up"]:
                post_up_all.append(script)

    for script in pre_up_all:
        os.system(script)

    os.system(f"docker compose up -d")

    for script in post_up_all:
        os.system(script)


def _container_down(container: str):
    if scripts.get(container, {}).get("pre_down"):
        for script in scripts[container]["pre_down"]:
            os.system(script)

    os.system(f"docker compose rm -svf {container}")

    if scripts.get(container, {}).get("post_down"):
        for script in scripts[container]["post_down"]:
            os.system(script)


def _server_down(recreate: bool = typer.Option(False, "--recreate", "-r")):
    pre_down_all = []
    post_down_all = []

    for key, value in scripts.items():
        if scripts[key].get("pre_down"):
            for script in scripts[key]["pre_down"]:
                pre_down_all.append(script)
        if scripts[key].get("post_down"):
            for script in scripts[key]["post_down"]:
                post_down_all.append(script)

    for script in pre_down_all:
        os.system(script)

    os.system(f"docker compose down")

    for script in post_down_all:
        os.system(script)


@app.command()
def up(
    args: Optional[List[str]] = typer.Argument(None),
    recreate: bool = typer.Option(False, "--recreate", "-r"),
):
    """
    Starts up target containers.
    If no target is defined, starts all containers.
    """
    if not args:
        _server_up(recreate)
    for container in args:
        _container_up(container, recreate)


@app.command()
def down(
    args: Optional[List[str]] = typer.Argument(None),
    confirmation=typer.Option(False, "-y"),
):
    """
    Shuts down target containers.
    If no target is defined, shuts down all containers.
    """
    confirmation = typer.confirm(
        f"You're about to shut down {args or 'the entire server'}. Are you sure?",
        abort=True,
    )

    if not args:
        _server_down()
    for container in args:
        _container_down(container)


@app.command()
def logs(
    args: Optional[List[str]] = typer.Argument(None),
    detached: bool = typer.Option(False, "--detached", "-d"),
):
    """
    Prints logs for target containers.
    If no target is defined, prints for all running ones.
    """
    os.system(f"docker compose logs {' '.join(args)} -f={not detached}")


@app.command()
def testando():
    print(scripts)
    print(type(scripts))


if __name__ == "__main__":
    app()

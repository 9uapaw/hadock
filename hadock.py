import enum
import logging
import pathlib
import json
import shutil
import threading
from dataclasses import dataclass, field
from os import mkdir
from typing import List, Dict, Optional

import docker
import typer
import yaml
import sh
from serde import deserialize, serialize
from serde.json import from_json
from serde.yaml import to_yaml

CURRENT_PATH = pathlib.Path(__file__).parent.resolve()
DEFAULT_DIR = pathlib.Path.home() / ".hadock"
DEFAULT_COMPOSE_YML = "docker-compose.yml"

DOCKER_COMPOSE_YML = "docker/" + DEFAULT_COMPOSE_YML
VOLUME_TEMPLATE = "{host_path}:{docker_path}"
CONTAINER_HADOOP_PATH = "/opt/hadoop"
HADOCK_TAG = "hadock/hadoop-{image}:mount"
BASE_IMAGE = HADOCK_TAG.format(image="base")

DOCKER_IMAGES = ["base", "app_historyserver", "datanode", "job_historyserver", "namenode", "nodemanager", "resourcemanager"]

HADOOP_DIRECTORY_FORMAT = {"bin", "etc", "share"}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


@deserialize
@serialize
@dataclass
class ComposeRole:
    image: str = ""
    container_name: str = ""
    restart: str = ""
    ports: Optional[List[str]] = field(default_factory=list)
    volumes: Optional[List[str]] = field(default_factory=list)
    environment: List[str] = field(default_factory=list)
    env_file: List[str] = field(default_factory=list)
    command: List[str] = field(default_factory=list)


@deserialize
@serialize
@dataclass
class DockerCompose:
    version: int
    services: Dict[str, ComposeRole]
    volumes: Dict[str, str or None]


class InstallationMethod(enum.Enum):
    DYNAMIC_MOUNT = "DYNAMIC_MOUNT"


app = typer.Typer()
docker_client = docker.client.from_env()


def get_docker_compose_command():
    """
    Returns the correct Docker Compose command based on the installed version.
    """
    try:
        sh.docker.compose("--version")
        return "docker compose"
    except sh.ErrorReturnCode:
        try:
            sh.docker-compose("--version")
            return "docker-compose"
        except sh.ErrorReturnCode:
            raise RuntimeError("Neither `docker compose` nor `docker-compose` is installed.")


@app.command()
def install(method: InstallationMethod = InstallationMethod.DYNAMIC_MOUNT.value):
    """
    Builds all the docker images.

    :param method: the way Hadoop is distributed to containers
    """
    for image in DOCKER_IMAGES:
        tag = HADOCK_TAG.format(image=image.replace("_", "-"))
        logger.info("Building image %s", tag)
        image = docker_client.images.build(path=str(CURRENT_PATH.absolute()) + "/docker/" + image, tag=tag, quiet=False)


@app.command()
def setup(host_mount_path: pathlib.Path, compose_path: pathlib.Path = pathlib.Path(DEFAULT_DIR, DEFAULT_COMPOSE_YML)):
    """
    Sets up the docker-compose yaml config file.

    :param host_mount_path: path that points to the Hadoop distribution, which is then mounted  to the containers dynamically
    :param compose_path: path for the docker-compose yaml config file
    """
    if not host_mount_path.exists():
        raise ValueError(f"Host mount path {host_mount_path} does not exist. Please use a valid path!")

    subdirs = set(map(lambda p: p.name, host_mount_path.iterdir()))
    for required_dir in HADOOP_DIRECTORY_FORMAT:
        if required_dir not in subdirs:
            raise ValueError(f"Host mount directory format is not satisfied. {required_dir} directory is not present.")

    if not compose_path.parent.exists():
        logger.info("Directory %s does not exist. Creating it.", compose_path.parent)
        mkdir(str(compose_path.parent))

    with open(DOCKER_COMPOSE_YML, 'r') as original_default_yml:
        compose = from_json(DockerCompose, json.dumps(yaml.safe_load(original_default_yml)))

    for service, role_data in compose.services.items():
        if not role_data.volumes:
            role_data.volumes = []

        role_data.volumes.append(VOLUME_TEMPLATE.format(host_path=host_mount_path, docker_path=CONTAINER_HADOOP_PATH))

    with open(str(compose_path), "w") as file:
        file.write(to_yaml(compose))

    shutil.copy2("docker/hadoop.env", DEFAULT_DIR)
    logger.info("Created file %s", str(compose_path))


@app.command()
def run(path: pathlib.Path = pathlib.Path(DEFAULT_DIR, DEFAULT_COMPOSE_YML), log: bool = True):
    """
    Runs Hadock with the given docker-compose yaml config file.

    :param path: path of the docker-compose yaml config file
    """
    docker_compose_cmd = get_docker_compose_command()
    logger.info("Starting Hadock with compose file: %s", path)
    if log:
        res = sh.bash(c=f"{docker_compose_cmd} -f {str(path)} up", _bg=True, _out=lambda line: logger.info(line.replace("\n", "")), _err=lambda line: logger.warning(line.replace("\n", "")))
    else:
        res = sh.bash(c=f"{docker_compose_cmd} -f {str(path)} up", _bg=True)

    res.wait()


@app.command()
def stop():
    """
    Stops all Hadock containers.

    """
    base_image_id = docker_client.images.list(BASE_IMAGE)[0].id
    containers = docker_client.containers.list(filters={"ancestor": base_image_id})
    threads = []

    for container in containers:
        logger.info("Stopping container %s", container)
        t = threading.Thread(target=lambda: container.stop())
        t.start()
        threads.append(t)

    [t.join() for t in threads]


if __name__ == "__main__":
    app()
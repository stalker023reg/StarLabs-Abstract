import json
import yaml
from loguru import logger


def read_txt_file(file_name: str, file_path: str) -> list:
    with open(file_path, "r") as file:
        items = [line.strip() for line in file]

    logger.success(f"Successfully loaded {len(items)} {file_name}.")
    return items


def read_config() -> dict:
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    return config


def split_list(lst, chunk_size=90):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def read_abi(path) -> dict:
    with open(path, "r") as f:
        return json.load(f)
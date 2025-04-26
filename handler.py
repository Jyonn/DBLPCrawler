import json
import yaml

from typing import Protocol, cast


class SupportsWrite(Protocol):
    def write(self, __s: str) -> object:
        ...


def json_load(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def json_loads(s: str):
    return json.loads(s)


def json_dumps(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def json_save(obj, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(obj, cast(SupportsWrite, f), indent=2, ensure_ascii=False)


def yaml_load(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def yaml_loads(s: str):
    return yaml.safe_load(s)


def yaml_dumps(obj) -> str:
    return yaml.dump(obj, indent=2, allow_unicode=True)


def yaml_save(obj, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(obj, cast(SupportsWrite, f), indent=2, allow_unicode=True)


def file_read(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def file_write(filepath: str, content: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

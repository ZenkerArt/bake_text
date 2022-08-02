from dataclasses import dataclass
from os.path import exists, join, split, abspath
from shutil import copy
from os import DirEntry, scandir

import bpy
import os


@dataclass
class File:
    name: str
    path: str


def get_project_folder() -> str:
    return bpy.path.abspath(bpy.context.scene.bt_settings.project_folder)


def get_folder(folder: str):
    path = join(get_project_folder(), folder)
    if exists(path):
        return path
    os.mkdir(path)
    return path


def copy_file_to_project(filepath: str, folder: str, filename: str = None):
    path, n = split(filepath)
    name = filename or n

    path_cache = get_folder(folder)
    new_path = join(path_cache, name)

    if exists(new_path):
        return File(
            name=name,
            path=new_path
        )

    copy(filepath, new_path)

    return File(
        name=name,
        path=new_path
    )


class Folder:
    _folder_name: str

    def __init__(self, folder_name: str):
        self._folder_name = folder_name

    @property
    def path(self):
        return get_folder(self._folder_name)

    def scan(self) -> list[DirEntry]:
        d = scandir(self.path)
        return list(d)

    def relative_path(self, filename: str):
        return join(f'.\\{self._folder_name}', filename)

    def get_file(self, filename: str):
        return join(self.path, filename)

    def save_file(self, filepath: str, filename: str = None):
        return copy_file_to_project(filepath, self._folder_name, filename=filename)

    def remove_file(self, filename: str):
        os.remove(join(self.path, filename))

    def rename_file(self, old_name: str, new_name: str):
        os.rename(self.get_file(old_name), self.get_file(new_name))


class ProjectFolders:
    root = Folder('')
    images = Folder('images')

import json
import logging
import os
from rich.logging import RichHandler
import importlib
import inspect


class BasePlugin:
    name: str

    def entrypoint(self):
        raise NotImplementedError(
            "Entry point method must be implemented in subclasses."
        )


class PluginManager:
    def __init__(self, path: str = ".", plugin_dir: str = "plugins") -> None:
        self.path = os.path.abspath(path) + "\\" + plugin_dir
        self.plugin_dir = plugin_dir
        self.manifest_path = self.path + "/manifest.json"
        logging.basicConfig(
            handlers=[RichHandler(markup=True)],
            format="[%(asctime)s] %(message)s",
            datefmt="%H:%M:%S",
            level=logging.NOTSET,
        )
        self.logger = logging.getLogger("rich")
        self.plugins = []

    def create_plugin_dir(self):
        if not os.path.exists(self.path):
            logging.debug("Folder does not exist. Creating...")
            os.makedirs(self.path)
            with open(self.manifest_path, "w") as f:
                f.write(json.dumps([{"name": "Plugin-Name", "path": "Plugin-Path"}]))

            logging.debug("Created Folder and files!")
            return
        logging.debug("Folders already created!")

    def refresh(self):
        self.plugins = []
        self.load_plugins()

    def get(self, name):
        for plugin in self.plugins:
            if plugin["name"] == name:
                return plugin["obj"]
        self.logger.debug(f"Couldnt find plugin with name: {name}")
        return None

    def add(self, name, plugin_obj):
        function_source = inspect.getsource(plugin_obj)
        print(self.path + f"\\{name}.py")
        with open(self.path + f"\\{name}.py", "w") as f:
            f.write(function_source)

    def load_plugins(self):
        with open(self.manifest_path, "r") as f:
            data = json.loads(f.read())

        for plugin in data:
            plugin_obj = importlib.import_module(
                self.plugin_dir.replace("\\", ".").replace("/", ".")
                + "."
                + plugin["path"]
            )

            self.plugins.append({"name": plugin["name"], "obj": plugin_obj})

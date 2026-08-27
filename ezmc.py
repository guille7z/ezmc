import os
import shutil
import subprocess
import sys
from pathlib import Path
import requests
from pyfiglet import Figlet
from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, OptionList, Input, Select, Button, Label
from textual.widgets.option_list import Option
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from loguru import logger

class EULADisclaimer(ModalScreen[bool]):
    CSS = """
    EULADisclaimer {
        align: center middle;
        text-align: center;
    }

    #box {
        align: center middle;
        height: 32%;
        width: 50%;
        border: thick $border;
        padding: 1 2;
    }

    #box > * {
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="box"):
            yield Label("just accept the eula...")
            yield Button("OK!", id="yes", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

class InitialServerAction(App[None]):
    CSS = """
    Screen {
        align: center middle;
    }

    OptionList {
        width: 70%;
        height: auto;
        text-align: center;
    }

    Label {
        width: 70%;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f.renderText("ezmc"))
        yield OptionList(
            Option("Create a Server", "create"),
            Option("Manage a Server", "manage"),
            Option("Exit"),
        )
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.exit(event.option.id)

class ManageServerList(App[None]):
    CSS = """
    Screen {
        align: center middle;
    }

    OptionList {
        width: 70%;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        servers = [p for p in Path("servers").iterdir() if p.is_dir()]
        yield OptionList(
            *(Option(s.name, s.name) for s in servers),
            Option("Cancel"),
        )
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.exit(event.option.id)

class ManageServer(App[None]):
    CSS = """
    Screen {
        align: center middle;
    }

    OptionList {
        width: 70%;
        height: auto;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield OptionList(
            Option("Start server", "start-server"), # TODO
            Option("Server properties", "server-properties"), # TODO
            Option("Reset world", "reset-world"), # TODO
            Option("Delete world", "delete-world"), # TODO
            Option("Delete server", "delete"),
            Option("Cancel", "cancel"),
        )
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.exit(event.option.id)

def fetch_versions() -> list[tuple[str, str]]:
    manifest = requests.get("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json").json()
    releases = [v["id"] for v in manifest["versions"] if v["type"] == "release"]
    return [(v, v) for v in releases]

def server_jar_url(version: str) -> str:
    manifest = requests.get("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json").json()
    entry = next(v for v in manifest["versions"] if v["id"] == version)
    return requests.get(entry["url"]).json()["downloads"]["server"]["url"]

def download_server_jar(version: str, dest: Path) -> None:
    url = server_jar_url(version)
    logger.info(f"Downloading server.jar ({version}) from {url}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    logger.success(f"Saved server.jar to {dest}")
    subprocess.run(["java", "-Xmx4G", "-Xms4G", "-jar", dest.name, "nogui"], cwd=dest.parent)
    eula = dest.parent / "eula.txt"
    if eula.exists():
        eula.write_text(eula.read_text().replace("eula=false", "eula=true"))
        logger.success("Accepted EULA (eula=true).")

class CreateServer(App):
    CSS = """
    Screen {
        align: center middle;
    }

    #server-setup {
        width: 50;
        height: auto;
        /* border: solid green; */
        padding: 1 2;
    }

    Button {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="server-setup"):
            yield Label("Server name:")
            yield Input(placeholder="Lowvoxel", id="server-name")

            yield Label("What modloader (if any) would you like?")
            yield Select(
                [
                    ("No modloader", "nope"),
                    ("NeoForge", "neo"),
                    ("Forge", "forge"),
                    ("Fabric", "fabric"),
                    ("Quilt", "quilt"),
                    ("LiteLoader", "lite"),
                ],
                id="loader-dropdown",
                allow_blank=False,
            )
            yield Label("Game version")
            yield Select(
                fetch_versions(),
                id="version-dropdown",
                allow_blank=False,
            )

            yield Label("", id="error")
            yield Button("Create", variant="success", id="btn-done")
            yield Button("Cancel", id="btn-cancel", variant="error")
        yield Footer()

# TODO: ManageServer

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.exit(None)
            return
        if event.button.id != "btn-done":
            return
        server_name = self.query_one("#server-name", Input).value.strip()
        error = self.query_one("#error", Label)
        if not server_name:
            error.update("Server name cannot be empty.")
            return
        mod_loader = self.query_one("#loader-dropdown", Select).value
        if mod_loader == Select.NULL:
            error.update("Select a modloader.")
            return
        game_version = self.query_one("#version-dropdown", Select).value
        if game_version == Select.NULL:
            error.update("Select a game version.")
            return
        error.update("")
        self.config = {"server_name": server_name, "mod_loader": mod_loader, "version": game_version}
        self.push_screen(EULADisclaimer(), self.on_disclaimer)

    def on_disclaimer(self, accepted: bool) -> None:
        if not accepted:
            self.exit(None)
            return
        print("OK")
        self.exit(result=self.config)

def create_server():
    return CreateServer().run()

def get_mod(mod):
    print(requests.get(mod).json())

def dl_mod(mod):
    logger.info(f"downloading mod_name from {mod}...")
    logger.error(f"can't download {mod} :(")

f = Figlet(font='slant')


def create_server_flow() -> None:
    while True:
        config = create_server()
        if config is None:
            return
        logger.info(f"Server '{config['server_name']}' configured with modloader '{config['mod_loader']}' on version {config['version']}")
        server_dir = Path("servers") / config["server_name"]
        try:
            server_dir.mkdir(parents=True)
            logger.success(f"Directory '{server_dir}' created successfully.")
        except FileExistsError:
            logger.error(f"Directory '{server_dir}' already exists.")
        except PermissionError:
            logger.error(f"Permission denied: Unable to create '{server_dir}'.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

        loader = config["mod_loader"]
        if loader == "nope":
            logger.info("No modloader selected; installing vanilla server.")
            download_server_jar(config["version"], server_dir / "server.jar")
        elif loader == "neo":
            logger.info("Setting up NeoForge server.")
        elif loader == "forge":
            logger.info("Setting up Forge server.")
        elif loader == "fabric":
            logger.info("Setting up Fabric server.")
        elif loader == "quilt":
            logger.info("Setting up Quilt server.")
        elif loader == "lite":
            logger.info("Setting up LiteLoader server.")
        else:
            logger.error(f"Unknown modloader '{loader}'.")
        return

def manage_server_flow() -> None:
    while True:
        selected = ManageServerList().run()
        if selected is None:
            return
        action = ManageServer().run()
        if action == "cancel":
            continue
        elif action == "delete":
            shutil.rmtree(f"servers/{selected}")
            logger.success(f"Deleted server '{selected}'.")
            continue
        elif action == "start-server":
            server_dir = Path("servers") / selected
            subprocess.run(["java", "-Xmx4G", "-Xms4G", "-jar", "server.jar", "nogui"], cwd=server_dir)
            continue
        elif action == "server-properties":
            print("tbd")
            continue
        else:
            logger.info(f"TODO: '{action}' on '{selected}'")

if __name__ == "__main__":
    logger.info(f"system is running {sys.platform}") # win32 | linux | darwin

    if os.path.isdir('servers'):
        logger.info("servers/ directory exists! :D")
    else:
        logger.warning("servers/ directory not found. Creating...")
        Path("servers").mkdir(parents=True, exist_ok=True)
        logger.success("created servers directory!")

    while True:
        action = InitialServerAction().run()
        if action is None:
            break
        if action == "create":
            create_server_flow()
        elif action == "manage":
            manage_server_flow()
        else:
            logger.error(f"{action} is an invalid option")

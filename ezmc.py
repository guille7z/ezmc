from pathlib import Path
import requests
import shutil
import subprocess
from loguru import logger
from pyfiglet import Figlet
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Input, Label, OptionList, Select
from textual.widgets.option_list import Option

# i <3 TODO's

class MainMenu(App):
    CSS = """
        Screen {
            align: center middle;
        }

        Label {
            width: auto;
            height: auto;
            content-align: center middle;
        }

        OptionList {
            width: auto;
            min-width: 30;
            align-horizontal: center;
            text-align: center;
        }
    """

    def compose(self) -> ComposeResult:
        yield Label(Figlet(font="slant").renderText("ezmc"))
        last_git_commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=".",
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        yield Label(last_git_commit, id="commit-version")
        yield OptionList(
            Option("Create a Server", id="create-server"),
            Option("Manage a Server", id="manage-server"),
            Option("Exit", id="exit"),
        )

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        self.exit(event.option.id)

class CreateServerMenu(App):
    CSS = """
        Screen {
            align: center middle;
            padding: 2 4;
            height: auto;
        }

        Horizontal {
            width: 100%;
            height: auto;
            align: center middle;
        }

        Button {
            margin: 1 1;
        }
    """

    def compose(self) -> ComposeResult:
        manifest = requests.get("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json", timeout=10).json()
        yield Label(Figlet(font="standard").renderText("server setup"))
        with Container():
            yield Label("What will your server be called?", id="server-name-label")
            yield Input("", id="server-name")
            yield Label("What modloader (if any) would you like?")
            yield Select(
                [
                    ("No modloader", "vanilla"),
                    ("NeoForge", "neoforge"),
                    ("Forge", "forge"),             # TODO: https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json
                    ("Fabric", "fabric"),           # TODO: https://meta.fabricmc.net/v2/versions/loader/1.21.1
                    ("Quilt", "quilt"),             # TODO: https://meta.quiltmc.org/v3/versions/loader
                    #("LiteLoader", "liteloader"),
                ],
                id="loader-dropdown",
                allow_blank=False,
            )

            versions = [
                (version["id"], version["id"])
                for version in manifest["versions"]
                if version["type"] == "release"
            ]

            #latest = versions[0][1]
            latest = manifest["latest"]["release"]

            yield Label("Select a Minecraft version:")
            yield Select(
                versions, value=latest,
                id="server-version"
            )

            with Horizontal():
                yield Button("Cancel", id="cancel", variant="error")
                yield Button("Create", id="create-server-btn", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.exit(event.button.id)

class ServerList(App):
    CSS = """
        Screen {
            align: center middle;
        }

        OptionList {
            width: auto;
            min-width: 30;
            align-horizontal: center;
        }
    """

    def compose(self) -> ComposeResult:
        servers = [ p for p in Path("servers").iterdir() ]
        yield OptionList(
            *(Option(f" {s.name}", s.name) for s in servers),
            Option(" Cancel", id="cancel"),
        )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.exit(event.option.id)

class ManageServer(App):
    CSS = """
        Screen {
            align: center middle;
        }

        OptionList {
            width: auto;
            min-width: 30;
            align-horizontal: center;
        }
    """

    def compose(self) -> ComposeResult:
        yield OptionList(
            Option(" Start server", id="server-start"), # TODO
            Option(" Server properties", id="server-properties"), # TODO
            Option(" Delete world", id="world-delete"), # TODO
            Option(" Delete server", id="server-delete"), # TODO
            Option(" Cancel", id="cancel"), # TODO
        )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.exit(event.option.id)

class ServerPropertiesList(App):
    CSS = """
        Screen {
            align: center middle;
        }

        OptionList {
            width: auto;
            min-width: 30;
            align-horizontal: center;
        }
    """

    def compose(self) -> ComposeResult:
        server_properties_path = f"servers/{self.server}/server.properties"

        # TODO: get all server properties as lines

        yield OptionList(
            # TODO: list each server property as an option
        )

def download_server(loader: str, version: str):
    if loader:
        if loader == "vanilla":
            manifest = requests.get(
                "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
            ).json()

            version_data = next(
                v for v in manifest["versions"]
                if v["id"] == version
            )

            data = requests.get(version_data["url"]).json()

            server_url = data["downloads"]["server"]["url"]

            with requests.get(server_url, stream=True) as response:
                response.raise_for_status()

                with open("server.jar", "wb") as file:
                    for chunk in response.iter_content(8192):
                        file.write(chunk)
        elif loader == "neoforge":
            built_link = f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{version}/neoforge-{version}-installer.jar"
            shutil.copyfileobj(
                requests.get(
                    built_link,
                    stream=True).raw,
                open(
                    f"neoforge-{version}-installer.jar",
                    "wb"
                ))
        elif loader == "forge": # TODO
            print("TODO: quilt")
        elif loader == "fabric": # TODO
            print("TODO: fabric") # https://meta.fabricmc.net/v2/versions/loader/{version}/{loader_version}/{installer_version}/server/jar
        elif loader == "quilt": # TODO
            print("TODO: quilt") # no clue

if __name__ == "__main__":
    result = MainMenu().run()

    if result == "create-server":
        result = CreateServerMenu().run() # TODO: actually make it create server: download jar -> eula modal (eula=true) => start server
    elif result == "manage-server":
        ServerList().run() # TODO: make into popup -> select server => THEN go into server management
    elif result == "exit":
        print("\nbye :(")

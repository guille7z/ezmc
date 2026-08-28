from pathlib import Path
import requests
from loguru import logger
from pyfiglet import Figlet
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Input, Label, OptionList, Select
from textual.widgets.option_list import Option

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
                    ("No modloader", "nope"),
                    ("NeoForge", "neoforge"),       # TODO: https://maven.neoforged.net/releases/net/neoforged/neoforge/{version}/neoforge-{version}-installer.jar
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
                yield Button("Cancel", variant="error")
                yield Button("Create", variant="success")

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
            " Start server",        # TODO: id=server-start
            " Server properties",   # TODO: id=server-properties
            " Delete world",        # TODO: id=world-delete
            " Delete server",       # TODO: id=server-delete
            " Cancel",              # TODO: id=cancel
        )

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
        yield OptionList(
            # TODO
        )

if __name__ == "__main__":
    result = MainMenu().run()

    if result == "create-server":
        result = CreateServerMenu().run()
        if result == "cancel":
            print("111")
    elif result == "manage-server":
        ServerList().run() # TODO: make into popup -> select server => THEN go into server management
    elif result == "exit":
        print("\nbye :(")

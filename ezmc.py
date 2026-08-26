import os
from pathlib import Path
import requests
from pyfiglet import Figlet
from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, OptionList, Input, Select, Button, Label
from textual.widgets.option_list import Option
from textual.containers import Container
from loguru import logger

class InitialServerAction(App[None]):
    CSS = """
    Screen {
        align: center middle;
    }

    OptionList {
        width: 70%;
        height: 80%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield OptionList(
            Option("Create a Server", "create"),
            Option("Manage a Server", "manage"),
        )
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.exit(event.option.id)

class CreateServer(App):
    CSS = """
    Screen {
        align: center middle;
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

            yield Label("", id="error")
            yield Button("done!", variant="success", id="btn-done")
        yield Footer()

# TODO: ManageServer

    def on_button_pressed(self, event: Button.Pressed) -> None:
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
        error.update("")
        self.exit(result={"server_name": server_name, "mod_loader": mod_loader})

def create_server():
    return CreateServer().run()

def get_mod(mod):
    print(requests.get(mod).json())

def dl_mod(mod):
    logger.info(f"downloading mod_name from {mod}...")
    logger.error(f"can't download {mod} :(")

f = Figlet(font='slant')

if __name__ == "__main__":
    print(f.renderText('ezmc'))
    print("easy minecraft server manager\n")

    if os.path.isdir('servers'):
        logger.info("servers/ directory exists! :D")
    else:
        logger.warning("servers/ directory not found. Creating...")
        Path("servers").mkdir(parents=True, exist_ok=True)
        logger.success("created servers directory!")

    result = InitialServerAction().run()
    if result == "create":
        logger.success(f"Server '{create_server()['server_name']}' configured with modloader '{create_server()['mod_loader']}'")
    elif result == "manage":
        logger.info(f"{result} TODO")
    else:
        logger.error(f"{result} is an invalid option")

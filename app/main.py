from typer import Typer

from .flows import app

main = Typer(add_completion=False, no_args_is_help=True)
main.add_typer(app, name="update", help="Import new updates from data provider")


if __name__ == "__main__":
    main()

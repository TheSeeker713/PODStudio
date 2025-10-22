"""
CLI Management Tool
Typer-based CLI for maintenance, DB management, etc.

TODO (Step 2+): Add commands for:
- db init (create schema)
- db migrate (future)
- probe (run hardware detection)
- cache clear
- pack validate <pack_id>
"""

import typer

app = typer.Typer(
    name="podstudio-cli",
    help="PODStudio CLI management tool",
    add_completion=False,
)


@app.command()
def version():
    """Show version"""
    typer.echo("PODStudio CLI v0.1.0")


@app.command()
def probe():
    """Run hardware probe"""
    typer.echo("Hardware probe not yet implemented (Step 2+)")


if __name__ == "__main__":
    app()

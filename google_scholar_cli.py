#!/usr/bin/env python3
import click
import logging
import sys
import os

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def main():
    """Google Scholar MCP Server CLI tool"""
    pass

@main.command()
@click.option('--log-level', '-l', default='INFO', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False),
              help='Set the logging level')
def serve(log_level):
    """Start the Google Scholar MCP server"""
    # Set up logging based on the provided log level
    numeric_level = getattr(logging, log_level.upper(), None)
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    from google_scholar_server import mcp
    
    click.echo(f"Starting Google Scholar MCP server")
    mcp.run()

@main.command()
def version():
    """Show the version of the Google Scholar MCP server"""
    try:
        from importlib.metadata import version as get_version
        version = get_version("mcp-server-google-scholar")
        click.echo(f"Google Scholar MCP Server version: {version}")
    except:
        # Fallback to hardcoded version if package isn't installed
        click.echo("Google Scholar MCP Server version: 0.1.0")

if __name__ == "__main__":
    main()
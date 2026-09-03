#!/usr/bin/env python3
"""
Cloudflare Tunnel (cloudflared) Exposer Script for WhatsApp Messenger
=====================================================================
Exposes the local WhatsApp Messenger Flask app (port 5556) to the public internet
using a temporary, free *.trycloudflare.com URL.

Usage:
    python tunnel.py              # Uses default port 5556
    python tunnel.py 5556         # Explicit port
    python tunnel.py 8000         # Custom port
"""

import os
import sys
import urllib.request
import subprocess

# Global directory for cloudflared executable (shared across projects)
GLOBAL_DIR = os.path.join(os.path.expanduser('~'), '.cloudflared')
CLOUDFLARED_PATH = os.path.join(GLOBAL_DIR, 'cloudflared.exe')

# WhatsApp Messenger default port
DEFAULT_PORT = 5556


def download_cloudflared():
    """Downloads cloudflared.exe if it does not already exist."""
    if not os.path.exists(GLOBAL_DIR):
        try:
            os.makedirs(GLOBAL_DIR, exist_ok=True)
            print(f"Created global directory: {GLOBAL_DIR}")
        except Exception as e:
            print(f"Error creating directory {GLOBAL_DIR}: {e}")
            sys.exit(1)

    if not os.path.exists(CLOUDFLARED_PATH):
        print(f"cloudflared.exe not found at {CLOUDFLARED_PATH}")
        print("Downloading the latest official binary from Cloudflare's GitHub releases...")

        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )

            with urllib.request.urlopen(req) as response:
                with open(CLOUDFLARED_PATH, 'wb') as out_file:
                    meta = response.info()
                    file_size = int(meta.get("Content-Length", 0))
                    print(f"File size: {file_size / (1024 * 1024):.2f} MB")

                    downloaded = 0
                    block_size = 8192
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        out_file.write(buffer)
                        status = f"\rDownloading: {downloaded * 100 / file_size:.1f}% ({downloaded / (1024 * 1024):.2f} MB / {file_size / (1024 * 1024):.2f} MB)"
                        sys.stdout.write(status)
                        sys.stdout.flush()
            print("\nDownload completed successfully!")
        except Exception as e:
            print(f"\nError downloading cloudflared: {e}")
            print("Please ensure you have an active internet connection and try again.")
            sys.exit(1)


def run_tunnel(port):
    """Starts the Cloudflare Tunnel pointing to the specified local port."""
    download_cloudflared()

    print("\n" + "=" * 60)
    print(f" Starting Cloudflare Tunnel for WhatsApp Messenger on port {port}")
    print("=" * 60)
    print("INSTRUCTIONS:")
    print("  1. Make sure WhatsApp Messenger app is running (python app.py)")
    print("  2. Look for the 'trycloudflare.com' URL below — that's your public link")
    print("  3. Share that URL with your team")
    print("  4. To STOP the tunnel, press Ctrl+C in this window")
    print("=" * 60 + "\n")

    try:
        subprocess.run([CLOUDFLARED_PATH, "tunnel", "--url", f"http://localhost:{port}"])
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print(" Tunnel stopped. Public URL is no longer accessible.")
        print("=" * 60)
    except FileNotFoundError:
        print(f"Error: cloudflared executable not found at {CLOUDFLARED_PATH}")
    except Exception as e:
        print(f"An unexpected error occurred while running the tunnel: {e}")


if __name__ == "__main__":
    port = DEFAULT_PORT

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            if port < 1 or port > 65535:
                raise ValueError("Port number must be between 1 and 65535.")
        except ValueError as e:
            print(f"Error: {e}")
            print(f"Usage: python tunnel.py [port_number]")
            print(f"Default port: {DEFAULT_PORT} (WhatsApp Messenger)")
            sys.exit(1)

    run_tunnel(port)
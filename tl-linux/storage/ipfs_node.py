#!/usr/bin/env python3
"""
TL Linux - IPFS Node Manager
Decentralized storage using IPFS (InterPlanetary File System)
"""

import subprocess
import json
import requests
import time
from pathlib import Path
import threading

try:
    import ipfshttpclient
    HAS_IPFS_CLIENT = True
except ImportError:
    HAS_IPFS_CLIENT = False

class IPFSNode:
    """Manage IPFS node and operations"""

    def __init__(self, ipfs_path=None):
        self.ipfs_path = ipfs_path or str(Path.home() / '.ipfs')
        self.api_url = 'http://127.0.0.1:5001'
        self.gateway_url = 'http://127.0.0.1:8080'
        self.client = None
        self.daemon_process = None
        self.is_running = False

    def is_ipfs_installed(self):
        """Check if IPFS is installed"""
        try:
            result = subprocess.run(['ipfs', 'version'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def is_initialized(self):
        """Check if IPFS is initialized"""
        ipfs_dir = Path(self.ipfs_path)
        return ipfs_dir.exists() and (ipfs_dir / 'config').exists()

    def initialize(self):
        """Initialize IPFS repository"""
        if self.is_initialized():
            return True, "Already initialized"

        try:
            result = subprocess.run(
                ['ipfs', 'init'],
                capture_output=True,
                text=True,
                timeout=30,
                env={'IPFS_PATH': self.ipfs_path}
            )

            if result.returncode == 0:
                return True, "IPFS initialized successfully"
            else:
                return False, f"Initialization failed: {result.stderr}"

        except Exception as e:
            return False, f"Error initializing IPFS: {e}"

    def start_daemon(self, background=True):
        """Start IPFS daemon"""
        if self.is_running:
            return True, "Daemon already running"

        if not self.is_initialized():
            success, msg = self.initialize()
            if not success:
                return False, msg

        try:
            if background:
                # Start daemon in background
                self.daemon_process = subprocess.Popen(
                    ['ipfs', 'daemon'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env={'IPFS_PATH': self.ipfs_path}
                )

                # Wait for daemon to start
                time.sleep(3)

                # Check if it's running
                if self.check_daemon_status():
                    self.is_running = True
                    self._connect_client()
                    return True, "IPFS daemon started"
                else:
                    return False, "Daemon failed to start"
            else:
                # Start in foreground (blocking)
                subprocess.run(
                    ['ipfs', 'daemon'],
                    env={'IPFS_PATH': self.ipfs_path}
                )

        except Exception as e:
            return False, f"Error starting daemon: {e}"

    def stop_daemon(self):
        """Stop IPFS daemon"""
        if self.daemon_process:
            self.daemon_process.terminate()
            self.daemon_process.wait(timeout=10)
            self.daemon_process = None

        self.is_running = False
        if self.client:
            self.client.close()
            self.client = None

        return True, "Daemon stopped"

    def check_daemon_status(self):
        """Check if daemon is running"""
        try:
            response = requests.get(f"{self.api_url}/api/v0/id", timeout=2)
            return response.status_code == 200
        except:
            return False

    def _connect_client(self):
        """Connect to IPFS client"""
        if HAS_IPFS_CLIENT:
            try:
                self.client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
            except:
                self.client = None

    def get_node_id(self):
        """Get IPFS node ID"""
        try:
            response = requests.post(f"{self.api_url}/api/v0/id", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('ID'), data.get('PublicKey')
            return None, None
        except:
            return None, None

    def add_file(self, file_path):
        """Add file to IPFS"""
        if not self.is_running:
            return None, "Daemon not running"

        try:
            file_path = Path(file_path)

            if HAS_IPFS_CLIENT and self.client:
                # Use Python client
                result = self.client.add(str(file_path))
                return result['Hash'], None
            else:
                # Use command line
                result = subprocess.run(
                    ['ipfs', 'add', '-Q', str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    env={'IPFS_PATH': self.ipfs_path}
                )

                if result.returncode == 0:
                    return result.stdout.strip(), None
                else:
                    return None, result.stderr

        except Exception as e:
            return None, str(e)

    def add_directory(self, dir_path, recursive=True):
        """Add directory to IPFS"""
        if not self.is_running:
            return None, "Daemon not running"

        try:
            dir_path = Path(dir_path)

            cmd = ['ipfs', 'add']
            if recursive:
                cmd.append('-r')
            cmd.extend(['-Q', str(dir_path)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                env={'IPFS_PATH': self.ipfs_path}
            )

            if result.returncode == 0:
                # Last line is the directory hash
                hashes = result.stdout.strip().split('\n')
                return hashes[-1], None
            else:
                return None, result.stderr

        except Exception as e:
            return None, str(e)

    def get_file(self, ipfs_hash, output_path=None):
        """Get file from IPFS"""
        if not self.is_running:
            return False, "Daemon not running"

        try:
            cmd = ['ipfs', 'get', ipfs_hash]
            if output_path:
                cmd.extend(['-o', str(output_path)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                env={'IPFS_PATH': self.ipfs_path}
            )

            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr

        except Exception as e:
            return False, str(e)

    def cat_file(self, ipfs_hash):
        """Read file content from IPFS"""
        if not self.is_running:
            return None, "Daemon not running"

        try:
            result = subprocess.run(
                ['ipfs', 'cat', ipfs_hash],
                capture_output=True,
                timeout=60,
                env={'IPFS_PATH': self.ipfs_path}
            )

            if result.returncode == 0:
                return result.stdout, None
            else:
                return None, result.stderr.decode()

        except Exception as e:
            return None, str(e)

    def pin_file(self, ipfs_hash):
        """Pin file to keep it in local storage"""
        if not self.is_running:
            return False, "Daemon not running"

        try:
            result = subprocess.run(
                ['ipfs', 'pin', 'add', ipfs_hash],
                capture_output=True,
                text=True,
                timeout=60,
                env={'IPFS_PATH': self.ipfs_path}
            )

            return result.returncode == 0, result.stderr if result.returncode != 0 else None

        except Exception as e:
            return False, str(e)

    def unpin_file(self, ipfs_hash):
        """Unpin file from local storage"""
        if not self.is_running:
            return False, "Daemon not running"

        try:
            result = subprocess.run(
                ['ipfs', 'pin', 'rm', ipfs_hash],
                capture_output=True,
                text=True,
                timeout=60,
                env={'IPFS_PATH': self.ipfs_path}
            )

            return result.returncode == 0, result.stderr if result.returncode != 0 else None

        except Exception as e:
            return False, str(e)

    def list_pins(self):
        """List all pinned files"""
        if not self.is_running:
            return [], "Daemon not running"

        try:
            result = subprocess.run(
                ['ipfs', 'pin', 'ls'],
                capture_output=True,
                text=True,
                timeout=30,
                env={'IPFS_PATH': self.ipfs_path}
            )

            if result.returncode == 0:
                pins = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            pins.append({
                                'hash': parts[0],
                                'type': parts[1]
                            })
                return pins, None
            else:
                return [], result.stderr

        except Exception as e:
            return [], str(e)

    def get_stats(self):
        """Get IPFS node statistics"""
        try:
            response = requests.post(f"{self.api_url}/api/v0/stats/repo", timeout=5)
            if response.status_code == 200:
                return response.json(), None
            return None, f"HTTP {response.status_code}"
        except Exception as e:
            return None, str(e)

    def get_peers(self):
        """Get connected peers"""
        try:
            response = requests.post(f"{self.api_url}/api/v0/swarm/peers", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('Peers', []), None
            return [], f"HTTP {response.status_code}"
        except Exception as e:
            return [], str(e)

    def get_gateway_url(self, ipfs_hash):
        """Get gateway URL for accessing file"""
        return f"{self.gateway_url}/ipfs/{ipfs_hash}"

    def publish_to_ipns(self, ipfs_hash, key='self'):
        """Publish hash to IPNS (InterPlanetary Name System)"""
        if not self.is_running:
            return None, "Daemon not running"

        try:
            result = subprocess.run(
                ['ipfs', 'name', 'publish', '--key', key, ipfs_hash],
                capture_output=True,
                text=True,
                timeout=60,
                env={'IPFS_PATH': self.ipfs_path}
            )

            if result.returncode == 0:
                # Extract IPNS name from output
                output = result.stdout.strip()
                return output, None
            else:
                return None, result.stderr

        except Exception as e:
            return None, str(e)

    def resolve_ipns(self, ipns_name):
        """Resolve IPNS name to IPFS hash"""
        if not self.is_running:
            return None, "Daemon not running"

        try:
            result = subprocess.run(
                ['ipfs', 'name', 'resolve', ipns_name],
                capture_output=True,
                text=True,
                timeout=30,
                env={'IPFS_PATH': self.ipfs_path}
            )

            if result.returncode == 0:
                return result.stdout.strip(), None
            else:
                return None, result.stderr

        except Exception as e:
            return None, str(e)

# Global IPFS node instance
_global_node = None

def get_global_node():
    """Get or create global IPFS node instance"""
    global _global_node
    if _global_node is None:
        _global_node = IPFSNode()
    return _global_node

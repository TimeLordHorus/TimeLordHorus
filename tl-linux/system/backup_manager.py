#!/usr/bin/env python3
"""
TL Linux - Backup Manager
User data backup and restore with incremental backups
"""

import os
import json
import shutil
import tarfile
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
import threading

class BackupManager:
    def __init__(self):
        self.config_dir = os.path.expanduser('~/.tl-linux/backup')
        self.config_file = os.path.join(self.config_dir, 'backup_config.json')

        os.makedirs(self.config_dir, exist_ok=True)

        self.config = self.load_config()

        # Backup storage
        self.backup_dir = self.config.get('backup_dir', os.path.expanduser('~/TL-Backups'))
        os.makedirs(self.backup_dir, exist_ok=True)

        # Backup history
        self.history_file = os.path.join(self.config_dir, 'backup_history.json')
        self.history = self.load_history()

    def load_config(self):
        """Load backup configuration"""
        default_config = {
            'backup_dir': os.path.expanduser('~/TL-Backups'),
            'schedule_enabled': True,
            'schedule_frequency': 'daily',  # daily, weekly, monthly
            'schedule_time': '02:00',
            'keep_count': 10,  # number of backups to keep
            'incremental_enabled': True,
            'compression_enabled': True,
            'encryption_enabled': False,
            'backup_locations': [
                {'path': '~/Documents', 'enabled': True},
                {'path': '~/Pictures', 'enabled': True},
                {'path': '~/Music', 'enabled': True},
                {'path': '~/Videos', 'enabled': True},
                {'path': '~/Downloads', 'enabled': False},  # Usually temporary
                {'path': '~/.tl-linux', 'enabled': True},  # Config
                {'path': '~/.local/share', 'enabled': True}  # App data
            ],
            'exclude_patterns': [
                '*.tmp',
                '*.cache',
                '__pycache__',
                '.git',
                'node_modules',
                '.venv'
            ]
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
        except:
            pass

        return default_config

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def load_history(self):
        """Load backup history"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []

    def save_history(self):
        """Save backup history"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def create_backup(self, backup_name=None, full_backup=False, callback=None):
        """
        Create a backup
        Args:
            backup_name: Custom name, or auto-generated
            full_backup: Force full backup instead of incremental
            callback: Progress callback function(current, total, message)
        """
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"📦 Creating backup: {backup_name}")

        backup_info = {
            'name': backup_name,
            'timestamp': datetime.now().isoformat(),
            'type': 'full' if full_backup else 'incremental',
            'size': 0,
            'file_count': 0,
            'locations': [],
            'status': 'in_progress'
        }

        try:
            # Determine if incremental possible
            last_backup = self.get_last_backup()
            is_incremental = (
                not full_backup and
                self.config.get('incremental_enabled') and
                last_backup is not None
            )

            if is_incremental:
                print(f"  📊 Incremental backup based on: {last_backup['name']}")
                backup_info['type'] = 'incremental'
                backup_info['parent'] = last_backup['name']
            else:
                print(f"  📊 Full backup")

            # Create backup directory
            backup_path = os.path.join(self.backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)

            # Backup each location
            total_files = self.count_files_to_backup()
            processed_files = 0

            for location in self.config['backup_locations']:
                if not location['enabled']:
                    continue

                source_path = os.path.expanduser(location['path'])
                if not os.path.exists(source_path):
                    continue

                print(f"  📁 Backing up: {location['path']}")

                # Create tar archive for this location
                location_name = location['path'].replace('~/', '').replace('/', '_')
                archive_name = f"{location_name}.tar.gz"
                archive_path = os.path.join(backup_path, archive_name)

                file_count, size = self.create_archive(
                    source_path,
                    archive_path,
                    is_incremental,
                    last_backup['timestamp'] if is_incremental else None,
                    callback=lambda c, t, m: callback(processed_files + c, total_files, m) if callback else None
                )

                backup_info['locations'].append({
                    'path': location['path'],
                    'archive': archive_name,
                    'file_count': file_count,
                    'size': size
                })

                backup_info['file_count'] += file_count
                backup_info['size'] += size

                processed_files += file_count

            # Save backup metadata
            metadata_path = os.path.join(backup_path, 'metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(backup_info, f, indent=2)

            # Mark complete
            backup_info['status'] = 'completed'

            # Add to history
            self.history.append(backup_info)
            self.save_history()

            # Cleanup old backups
            self.cleanup_old_backups()

            print(f"  ✅ Backup complete!")
            print(f"     Files: {backup_info['file_count']}")
            print(f"     Size: {self.format_size(backup_info['size'])}")

            return backup_info

        except Exception as e:
            print(f"  ❌ Backup failed: {e}")
            backup_info['status'] = 'failed'
            backup_info['error'] = str(e)
            return backup_info

    def count_files_to_backup(self):
        """Count total files that will be backed up"""
        total = 0
        for location in self.config['backup_locations']:
            if location['enabled']:
                path = os.path.expanduser(location['path'])
                if os.path.exists(path):
                    total += sum(1 for _ in Path(path).rglob('*') if _.is_file())
        return total

    def create_archive(self, source_path, archive_path, incremental, since_timestamp, callback=None):
        """Create tar.gz archive of a directory"""
        file_count = 0
        total_size = 0

        # Parse since timestamp for incremental
        since_time = None
        if incremental and since_timestamp:
            since_time = datetime.fromisoformat(since_timestamp).timestamp()

        # Compression mode
        mode = 'w:gz' if self.config.get('compression_enabled') else 'w'

        with tarfile.open(archive_path, mode) as tar:
            for root, dirs, files in os.walk(source_path):
                # Filter excluded patterns
                dirs[:] = [d for d in dirs if not self.should_exclude(d)]

                for file in files:
                    if self.should_exclude(file):
                        continue

                    file_path = os.path.join(root, file)

                    # Skip if incremental and file not modified
                    if incremental and since_time:
                        try:
                            mtime = os.path.getmtime(file_path)
                            if mtime < since_time:
                                continue
                        except:
                            continue

                    try:
                        # Add to archive
                        arcname = os.path.relpath(file_path, source_path)
                        tar.add(file_path, arcname=arcname)

                        file_count += 1
                        total_size += os.path.getsize(file_path)

                        if callback and file_count % 10 == 0:
                            callback(file_count, file_count, f"Archiving {file}")

                    except Exception as e:
                        print(f"     ⚠️ Skipped {file_path}: {e}")

        return file_count, total_size

    def should_exclude(self, name):
        """Check if file/dir should be excluded"""
        import fnmatch

        for pattern in self.config['exclude_patterns']:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False

    def restore_backup(self, backup_name, restore_path=None, callback=None):
        """
        Restore a backup
        Args:
            backup_name: Name of backup to restore
            restore_path: Where to restore (default: original locations)
            callback: Progress callback
        """
        print(f"📂 Restoring backup: {backup_name}")

        # Find backup in history
        backup_info = None
        for b in self.history:
            if b['name'] == backup_name:
                backup_info = b
                break

        if not backup_info:
            print(f"❌ Backup not found: {backup_name}")
            return False

        backup_path = os.path.join(self.backup_dir, backup_name)
        if not os.path.exists(backup_path):
            print(f"❌ Backup files not found: {backup_path}")
            return False

        try:
            # Restore each archive
            for i, location in enumerate(backup_info['locations']):
                archive_path = os.path.join(backup_path, location['archive'])

                if not os.path.exists(archive_path):
                    print(f"  ⚠️ Archive not found: {location['archive']}")
                    continue

                # Determine restore destination
                if restore_path:
                    dest = restore_path
                else:
                    dest = os.path.expanduser(location['path'])

                print(f"  📁 Restoring: {location['path']} → {dest}")

                # Extract archive
                with tarfile.open(archive_path, 'r:*') as tar:
                    tar.extractall(dest)

                if callback:
                    progress = ((i + 1) / len(backup_info['locations'])) * 100
                    callback(i + 1, len(backup_info['locations']), f"Restored {location['path']}")

            print(f"  ✅ Restore complete!")
            return True

        except Exception as e:
            print(f"  ❌ Restore failed: {e}")
            return False

    def get_last_backup(self):
        """Get most recent successful backup"""
        successful_backups = [b for b in self.history if b.get('status') == 'completed']
        if successful_backups:
            return successful_backups[-1]
        return None

    def cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        keep_count = self.config.get('keep_count', 10)

        # Get completed backups
        completed = [b for b in self.history if b.get('status') == 'completed']

        if len(completed) <= keep_count:
            return

        # Remove oldest backups
        to_remove = completed[:-keep_count]

        for backup in to_remove:
            print(f"  🗑️ Removing old backup: {backup['name']}")

            # Delete backup directory
            backup_path = os.path.join(self.backup_dir, backup['name'])
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)

            # Remove from history
            self.history.remove(backup)

        self.save_history()

    def verify_backup(self, backup_name):
        """Verify backup integrity"""
        print(f"🔍 Verifying backup: {backup_name}")

        backup_path = os.path.join(self.backup_dir, backup_name)

        if not os.path.exists(backup_path):
            print(f"  ❌ Backup not found")
            return False

        # Load metadata
        metadata_path = os.path.join(backup_path, 'metadata.json')
        if not os.path.exists(metadata_path):
            print(f"  ❌ Metadata missing")
            return False

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Verify each archive
        all_ok = True
        for location in metadata['locations']:
            archive_path = os.path.join(backup_path, location['archive'])

            if not os.path.exists(archive_path):
                print(f"  ❌ Archive missing: {location['archive']}")
                all_ok = False
                continue

            # Test archive integrity
            try:
                with tarfile.open(archive_path, 'r:*') as tar:
                    # Just opening successfully is a good sign
                    members = tar.getmembers()
                    if len(members) == 0:
                        print(f"  ⚠️ Archive empty: {location['archive']}")
                        all_ok = False
                    else:
                        print(f"  ✅ {location['archive']} - {len(members)} files")
            except Exception as e:
                print(f"  ❌ Archive corrupted: {location['archive']} - {e}")
                all_ok = False

        if all_ok:
            print(f"  ✅ Backup verification passed")
        else:
            print(f"  ⚠️ Backup verification found issues")

        return all_ok

    def get_backups(self):
        """Get list of all backups"""
        return self.history

    def delete_backup(self, backup_name):
        """Delete a specific backup"""
        print(f"🗑️ Deleting backup: {backup_name}")

        # Find in history
        backup_info = None
        for b in self.history:
            if b['name'] == backup_name:
                backup_info = b
                break

        if not backup_info:
            print(f"  ⚠️ Backup not found in history")
            return False

        # Delete files
        backup_path = os.path.join(self.backup_dir, backup_name)
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
            print(f"  ✅ Backup files deleted")

        # Remove from history
        self.history.remove(backup_info)
        self.save_history()

        return True

    def format_size(self, bytes_val):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"


# Global instance
_backup_manager = None

def get_backup_manager():
    """Get or create backup manager"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager

def create_backup(name=None, full=False):
    """Create a backup"""
    manager = get_backup_manager()
    return manager.create_backup(name, full)

def restore_backup(name, restore_path=None):
    """Restore a backup"""
    manager = get_backup_manager()
    return manager.restore_backup(name, restore_path)

def get_backups():
    """Get list of backups"""
    manager = get_backup_manager()
    return manager.get_backups()

def verify_backup(name):
    """Verify backup integrity"""
    manager = get_backup_manager()
    return manager.verify_backup(name)

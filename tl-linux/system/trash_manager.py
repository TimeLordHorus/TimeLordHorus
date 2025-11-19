#!/usr/bin/env python3
"""
TL Linux - Trash Manager
System trash/recycle bin with restore functionality
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class TrashManager:
    def __init__(self):
        # XDG trash specification paths
        self.trash_dir = os.path.expanduser('~/.local/share/Trash')
        self.trash_files = os.path.join(self.trash_dir, 'files')
        self.trash_info = os.path.join(self.trash_dir, 'info')

        # Create trash directories
        os.makedirs(self.trash_files, exist_ok=True)
        os.makedirs(self.trash_info, exist_ok=True)

    def move_to_trash(self, path):
        """Move file or folder to trash"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path does not exist: {path}")

        # Get original path info
        original_path = os.path.abspath(path)
        basename = os.path.basename(path)

        # Handle name conflicts in trash
        trash_path = os.path.join(self.trash_files, basename)
        counter = 1
        while os.path.exists(trash_path):
            name, ext = os.path.splitext(basename)
            trash_path = os.path.join(self.trash_files, f"{name}_{counter}{ext}")
            counter += 1

        trash_basename = os.path.basename(trash_path)

        # Create .trashinfo file
        info_file = os.path.join(self.trash_info, f"{trash_basename}.trashinfo")
        trash_info_content = f"""[Trash Info]
Path={original_path}
DeletionDate={datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}
"""

        try:
            # Move file/folder to trash
            shutil.move(path, trash_path)

            # Write trash info
            with open(info_file, 'w') as f:
                f.write(trash_info_content)

            return trash_basename

        except Exception as e:
            raise Exception(f"Failed to move to trash: {e}")

    def restore(self, trash_name):
        """Restore file from trash"""
        trash_path = os.path.join(self.trash_files, trash_name)
        info_file = os.path.join(self.trash_info, f"{trash_name}.trashinfo")

        if not os.path.exists(trash_path):
            raise FileNotFoundError(f"Item not found in trash: {trash_name}")

        if not os.path.exists(info_file):
            raise FileNotFoundError(f"Trash info not found: {trash_name}")

        # Read original path
        with open(info_file, 'r') as f:
            for line in f:
                if line.startswith('Path='):
                    original_path = line.split('=', 1)[1].strip()
                    break
            else:
                raise ValueError("Invalid trash info file")

        # Check if original location exists
        original_dir = os.path.dirname(original_path)
        if not os.path.exists(original_dir):
            raise FileNotFoundError(f"Original directory no longer exists: {original_dir}")

        # Handle name conflicts at original location
        restore_path = original_path
        counter = 1
        while os.path.exists(restore_path):
            name, ext = os.path.splitext(original_path)
            restore_path = f"{name}_restored_{counter}{ext}"
            counter += 1

        try:
            # Restore file
            shutil.move(trash_path, restore_path)

            # Remove trash info
            os.remove(info_file)

            return restore_path

        except Exception as e:
            raise Exception(f"Failed to restore from trash: {e}")

    def delete_permanently(self, trash_name):
        """Permanently delete item from trash"""
        trash_path = os.path.join(self.trash_files, trash_name)
        info_file = os.path.join(self.trash_info, f"{trash_name}.trashinfo")

        if not os.path.exists(trash_path):
            raise FileNotFoundError(f"Item not found in trash: {trash_name}")

        try:
            # Delete file/folder
            if os.path.isdir(trash_path):
                shutil.rmtree(trash_path)
            else:
                os.remove(trash_path)

            # Delete info file
            if os.path.exists(info_file):
                os.remove(info_file)

        except Exception as e:
            raise Exception(f"Failed to delete permanently: {e}")

    def list_trash(self):
        """List all items in trash"""
        items = []

        for item in os.listdir(self.trash_files):
            trash_path = os.path.join(self.trash_files, item)
            info_file = os.path.join(self.trash_info, f"{item}.trashinfo")

            # Get info
            original_path = None
            deletion_date = None

            if os.path.exists(info_file):
                with open(info_file, 'r') as f:
                    for line in f:
                        if line.startswith('Path='):
                            original_path = line.split('=', 1)[1].strip()
                        elif line.startswith('DeletionDate='):
                            deletion_date = line.split('=', 1)[1].strip()

            # Get size
            if os.path.isdir(trash_path):
                size = self.get_dir_size(trash_path)
            else:
                size = os.path.getsize(trash_path)

            items.append({
                'name': item,
                'original_path': original_path,
                'deletion_date': deletion_date,
                'size': size,
                'is_dir': os.path.isdir(trash_path)
            })

        return items

    def get_dir_size(self, path):
        """Get total size of directory"""
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += self.get_dir_size(entry.path)
        except:
            pass
        return total

    def empty_trash(self):
        """Empty the entire trash"""
        # Delete all files
        for item in os.listdir(self.trash_files):
            trash_path = os.path.join(self.trash_files, item)
            try:
                if os.path.isdir(trash_path):
                    shutil.rmtree(trash_path)
                else:
                    os.remove(trash_path)
            except:
                pass

        # Delete all info files
        for item in os.listdir(self.trash_info):
            info_path = os.path.join(self.trash_info, item)
            try:
                os.remove(info_path)
            except:
                pass

    def get_trash_size(self):
        """Get total size of trash"""
        return self.get_dir_size(self.trash_files)


# Global trash manager instance
_trash_manager = None

def get_trash_manager():
    """Get or create trash manager instance"""
    global _trash_manager
    if _trash_manager is None:
        _trash_manager = TrashManager()
    return _trash_manager

def move_to_trash(path):
    """Move file to trash"""
    manager = get_trash_manager()
    return manager.move_to_trash(path)

def restore_from_trash(trash_name):
    """Restore file from trash"""
    manager = get_trash_manager()
    return manager.restore(trash_name)

def delete_permanently(trash_name):
    """Permanently delete from trash"""
    manager = get_trash_manager()
    manager.delete_permanently(trash_name)

def list_trash():
    """List trash contents"""
    manager = get_trash_manager()
    return manager.list_trash()

def empty_trash():
    """Empty trash"""
    manager = get_trash_manager()
    manager.empty_trash()

def get_trash_size():
    """Get trash size"""
    manager = get_trash_manager()
    return manager.get_trash_size()

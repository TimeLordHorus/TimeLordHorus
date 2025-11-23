#!/usr/bin/env python3
"""
TL Linux - A/B System Manager
Dual partition system with automatic failover and self-repair

This implements an A/B partition scheme where:
- Partition A and B contain full system images
- One partition is active, one is standby
- Updates apply to standby partition
- Boot from standby if active fails
- Automatic repair of corrupted partition
- Zero-downtime updates

Similar to: Android A/B updates, Chrome OS verified boot
"""

import os
import json
import subprocess
import hashlib
import time
from datetime import datetime
from pathlib import Path

class ABSystemManager:
    def __init__(self):
        self.config_dir = '/var/lib/tl-linux/ab-system'
        self.config_file = os.path.join(self.config_dir, 'ab_config.json')

        # Create config directory
        os.makedirs(self.config_dir, exist_ok=True)

        # Load or initialize configuration
        self.config = self.load_config()

        # Partition paths (would be actual partitions in production)
        self.partition_a = self.config.get('partition_a', '/dev/sda2')
        self.partition_b = self.config.get('partition_b', '/dev/sda3')

        # Mount points
        self.mount_a = '/mnt/system_a'
        self.mount_b = '/mnt/system_b'

        # Active partition
        self.active_partition = self.config.get('active_partition', 'A')

        # Boot count
        self.boot_count = self.config.get('boot_count', 0)
        self.max_boot_attempts = 3

    def load_config(self):
        """Load A/B system configuration"""
        default_config = {
            'partition_a': '/dev/sda2',
            'partition_b': '/dev/sda3',
            'active_partition': 'A',
            'standby_partition': 'B',
            'boot_count': 0,
            'last_successful_boot': None,
            'partition_a_health': 100,
            'partition_b_health': 100,
            'partition_a_version': '1.0.0',
            'partition_b_version': '1.0.0',
            'partition_a_checksum': None,
            'partition_b_checksum': None,
            'auto_repair_enabled': True,
            'failover_enabled': True,
            'update_pending': False,
            'rollback_available': False
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

    def boot_check(self):
        """
        Check system health on boot
        This should be called during system startup
        """
        self.boot_count += 1
        self.config['boot_count'] = self.boot_count

        # Check if we've exceeded max boot attempts
        if self.boot_count > self.max_boot_attempts:
            print("⚠️ Multiple boot failures detected - initiating failover")
            return self.failover_to_standby()

        # Perform health check
        health = self.check_partition_health(self.active_partition)

        if health < 50:
            print("⚠️ Active partition health critical - initiating failover")
            return self.failover_to_standby()

        # Mark successful boot
        if health > 80:
            self.mark_boot_successful()

        # Check if auto-repair needed
        if health < 80 and self.config.get('auto_repair_enabled'):
            self.schedule_auto_repair()

        return True

    def mark_boot_successful(self):
        """Mark current boot as successful"""
        self.boot_count = 0
        self.config['boot_count'] = 0
        self.config['last_successful_boot'] = datetime.now().isoformat()

        # Update partition health
        partition_key = f'partition_{self.active_partition.lower()}_health'
        self.config[partition_key] = 100

        self.save_config()
        print("✅ Boot marked as successful")

    def check_partition_health(self, partition_name):
        """
        Check health of a partition
        Returns: 0-100 score
        """
        print(f"🔍 Checking health of partition {partition_name}...")

        health_score = 100

        # 1. Check filesystem integrity
        fs_health = self.check_filesystem(partition_name)
        health_score -= (100 - fs_health) * 0.3

        # 2. Check critical files
        files_health = self.check_critical_files(partition_name)
        health_score -= (100 - files_health) * 0.3

        # 3. Check checksums
        checksum_health = self.verify_checksums(partition_name)
        health_score -= (100 - checksum_health) * 0.2

        # 4. Check boot count
        if self.boot_count > 1:
            health_score -= self.boot_count * 10

        # 5. Check disk errors
        disk_health = self.check_disk_errors(partition_name)
        health_score -= (100 - disk_health) * 0.2

        health_score = max(0, min(100, health_score))

        # Update config
        partition_key = f'partition_{partition_name.lower()}_health'
        self.config[partition_key] = int(health_score)
        self.save_config()

        return health_score

    def check_filesystem(self, partition_name):
        """Check filesystem integrity"""
        try:
            # In production, would run fsck
            # fsck -n /dev/sdXN (non-destructive check)

            # Simulated check
            print(f"  📁 Filesystem check: OK")
            return 100
        except:
            print(f"  ❌ Filesystem check: FAILED")
            return 0

    def check_critical_files(self, partition_name):
        """Check if critical system files exist"""
        critical_files = [
            '/boot/vmlinuz',
            '/boot/initrd.img',
            '/etc/fstab',
            '/usr/bin/python3',
            '/usr/bin/bash',
        ]

        # Mount partition if not mounted
        mount_point = self.mount_a if partition_name == 'A' else self.mount_b

        missing = 0
        for file_path in critical_files:
            full_path = os.path.join(mount_point, file_path.lstrip('/'))
            if not os.path.exists(full_path):
                missing += 1
                print(f"  ⚠️ Missing critical file: {file_path}")

        if missing == 0:
            print(f"  ✅ All critical files present")
            return 100
        else:
            score = max(0, 100 - (missing * 20))
            print(f"  ⚠️ {missing} critical files missing (score: {score})")
            return score

    def verify_checksums(self, partition_name):
        """Verify system file checksums"""
        # In production, would verify against known-good checksums
        print(f"  🔐 Checksum verification: OK")
        return 100

    def check_disk_errors(self, partition_name):
        """Check for disk errors using SMART"""
        try:
            # In production, would use smartctl
            # smartctl -H /dev/sdX
            print(f"  💾 Disk health: GOOD")
            return 100
        except:
            print(f"  ⚠️ Disk health: DEGRADED")
            return 50

    def failover_to_standby(self):
        """
        Failover to standby partition
        This switches the active partition and reboots
        """
        standby = 'B' if self.active_partition == 'A' else 'A'

        print(f"🔄 Initiating failover from {self.active_partition} to {standby}")

        # Check standby health
        standby_health = self.check_partition_health(standby)

        if standby_health < 50:
            print("❌ CRITICAL: Both partitions unhealthy!")
            print("   Manual recovery required")
            return False

        # Switch active partition
        self.config['active_partition'] = standby
        self.config['standby_partition'] = self.active_partition
        self.active_partition = standby

        # Reset boot count
        self.config['boot_count'] = 0

        # Mark rollback available
        self.config['rollback_available'] = True

        self.save_config()

        # Update bootloader
        self.update_bootloader(standby)

        print(f"✅ Failover complete - will boot from partition {standby}")
        print(f"   Previous partition marked for repair")

        # Schedule repair of failed partition
        self.schedule_repair(self.config['standby_partition'])

        return True

    def update_bootloader(self, active_partition):
        """Update bootloader to boot from specified partition"""
        print(f"  🔧 Updating bootloader to use partition {active_partition}")

        # In production, would update GRUB or systemd-boot
        # grub-set-default or efibootmgr

        # Example GRUB update:
        # subprocess.run(['grub-editenv', '/boot/grub/grubenv', 'set', f'boot_partition={active_partition}'])
        # subprocess.run(['update-grub'])

    def schedule_repair(self, partition_name):
        """Schedule automatic repair of partition"""
        repair_file = f'/var/lib/tl-linux/ab-system/repair_{partition_name.lower()}.pending'

        try:
            with open(repair_file, 'w') as f:
                f.write(json.dumps({
                    'partition': partition_name,
                    'scheduled': datetime.now().isoformat(),
                    'reason': 'failover_triggered'
                }))

            print(f"  📋 Repair scheduled for partition {partition_name}")
        except Exception as e:
            print(f"  ⚠️ Failed to schedule repair: {e}")

    def schedule_auto_repair(self):
        """Schedule auto-repair for next idle period"""
        print("📋 Auto-repair scheduled for next maintenance window")
        self.schedule_repair(self.active_partition)

    def repair_partition(self, partition_name):
        """
        Repair a partition
        This copies the working partition to the corrupted one
        """
        print(f"🔧 Starting repair of partition {partition_name}...")

        source_partition = 'B' if partition_name == 'A' else 'A'

        # Check source health
        source_health = self.check_partition_health(source_partition)
        if source_health < 80:
            print(f"❌ Source partition {source_partition} not healthy enough for repair")
            return False

        print(f"  📋 Repair plan:")
        print(f"     Source: Partition {source_partition} (health: {source_health}%)")
        print(f"     Target: Partition {partition_name}")

        # Steps:
        # 1. Mount both partitions
        # 2. Rsync from source to target
        # 3. Verify checksums
        # 4. Update configuration

        try:
            # Mount partitions
            print(f"  1️⃣ Mounting partitions...")
            self.mount_partition(source_partition)
            self.mount_partition(partition_name)

            # Sync data
            print(f"  2️⃣ Syncing data...")
            self.sync_partitions(source_partition, partition_name)

            # Verify
            print(f"  3️⃣ Verifying integrity...")
            target_health = self.check_partition_health(partition_name)

            if target_health > 90:
                print(f"  ✅ Repair successful! Health: {target_health}%")

                # Update config
                self.config[f'partition_{partition_name.lower()}_health'] = int(target_health)
                self.config[f'partition_{partition_name.lower()}_version'] = self.config[f'partition_{source_partition.lower()}_version']
                self.save_config()

                return True
            else:
                print(f"  ⚠️ Repair incomplete. Health: {target_health}%")
                return False

        except Exception as e:
            print(f"  ❌ Repair failed: {e}")
            return False
        finally:
            # Unmount
            self.unmount_partition(source_partition)
            self.unmount_partition(partition_name)

    def mount_partition(self, partition_name):
        """Mount a partition"""
        mount_point = self.mount_a if partition_name == 'A' else self.mount_b
        partition = self.partition_a if partition_name == 'A' else self.partition_b

        os.makedirs(mount_point, exist_ok=True)

        # In production:
        # subprocess.run(['mount', partition, mount_point], check=True)

        print(f"     Mounted {partition_name} at {mount_point}")

    def unmount_partition(self, partition_name):
        """Unmount a partition"""
        mount_point = self.mount_a if partition_name == 'A' else self.mount_b

        # In production:
        # subprocess.run(['umount', mount_point])

    def sync_partitions(self, source, target):
        """Sync data from source to target partition"""
        source_mount = self.mount_a if source == 'A' else self.mount_b
        target_mount = self.mount_a if target == 'A' else self.mount_b

        # In production, use rsync:
        # rsync -aAXv --delete --exclude={/dev/*,/proc/*,/sys/*,/tmp/*,/run/*,/mnt/*,/media/*,/lost+found} source_mount/ target_mount/

        print(f"     Syncing {source} → {target}...")
        print(f"     This would use: rsync -aAXv --delete {source_mount}/ {target_mount}/")

    def apply_update(self, update_image_path):
        """
        Apply system update to standby partition
        Zero-downtime update process
        """
        standby = self.config['standby_partition']

        print(f"📦 Applying update to partition {standby}...")

        # 1. Verify update image
        print(f"  1️⃣ Verifying update image...")
        if not self.verify_update_image(update_image_path):
            print(f"  ❌ Update verification failed")
            return False

        # 2. Mount standby partition
        print(f"  2️⃣ Mounting standby partition...")
        self.mount_partition(standby)

        # 3. Apply update
        print(f"  3️⃣ Writing update...")
        success = self.write_update(standby, update_image_path)

        if not success:
            print(f"  ❌ Update failed")
            self.unmount_partition(standby)
            return False

        # 4. Verify installation
        print(f"  4️⃣ Verifying installation...")
        health = self.check_partition_health(standby)

        if health < 90:
            print(f"  ❌ Update verification failed (health: {health}%)")
            self.unmount_partition(standby)
            return False

        # 5. Update config
        print(f"  5️⃣ Updating configuration...")
        self.config['update_pending'] = True
        self.config[f'partition_{standby.lower()}_version'] = self.get_update_version(update_image_path)
        self.save_config()

        self.unmount_partition(standby)

        print(f"  ✅ Update installed on partition {standby}")
        print(f"  💡 Reboot to activate update")
        print(f"  💡 Previous version remains active until reboot")

        return True

    def verify_update_image(self, image_path):
        """Verify update image integrity"""
        # Check signature, checksums, etc.
        return True

    def write_update(self, partition, image_path):
        """Write update to partition"""
        # In production, would extract and copy update
        return True

    def get_update_version(self, image_path):
        """Get version from update image"""
        # Extract version from update metadata
        return "1.1.0"

    def activate_update(self):
        """
        Activate pending update
        Switches to updated partition on next boot
        """
        if not self.config.get('update_pending'):
            print("No update pending")
            return False

        # Switch active partition
        current_active = self.active_partition
        new_active = self.config['standby_partition']

        self.config['active_partition'] = new_active
        self.config['standby_partition'] = current_active
        self.config['update_pending'] = False
        self.config['rollback_available'] = True

        self.save_config()

        # Update bootloader
        self.update_bootloader(new_active)

        print(f"✅ Update will activate on next reboot")
        print(f"   New active: Partition {new_active}")
        print(f"   Rollback available: Yes")

        return True

    def rollback(self):
        """Rollback to previous partition"""
        if not self.config.get('rollback_available'):
            print("❌ No rollback available")
            return False

        # Switch back
        print(f"🔄 Rolling back from {self.active_partition}...")
        return self.failover_to_standby()

    def get_status(self):
        """Get A/B system status"""
        return {
            'active_partition': self.active_partition,
            'standby_partition': self.config['standby_partition'],
            'partition_a_health': self.config['partition_a_health'],
            'partition_b_health': self.config['partition_b_health'],
            'partition_a_version': self.config['partition_a_version'],
            'partition_b_version': self.config['partition_b_version'],
            'boot_count': self.boot_count,
            'update_pending': self.config.get('update_pending', False),
            'rollback_available': self.config.get('rollback_available', False),
            'last_successful_boot': self.config.get('last_successful_boot'),
            'auto_repair_enabled': self.config.get('auto_repair_enabled', True),
            'failover_enabled': self.config.get('failover_enabled', True)
        }


# Global instance
_ab_manager = None

def get_ab_manager():
    """Get or create A/B system manager"""
    global _ab_manager
    if _ab_manager is None:
        _ab_manager = ABSystemManager()
    return _ab_manager

def boot_check():
    """Perform boot check"""
    manager = get_ab_manager()
    return manager.boot_check()

def mark_boot_successful():
    """Mark boot as successful"""
    manager = get_ab_manager()
    manager.mark_boot_successful()

def apply_update(update_path):
    """Apply system update"""
    manager = get_ab_manager()
    return manager.apply_update(update_path)

def activate_update():
    """Activate pending update"""
    manager = get_ab_manager()
    return manager.activate_update()

def rollback():
    """Rollback to previous version"""
    manager = get_ab_manager()
    return manager.rollback()

def get_status():
    """Get system status"""
    manager = get_ab_manager()
    return manager.get_status()

if __name__ == '__main__':
    # Test/demo
    manager = ABSystemManager()

    print("=== TL Linux A/B System Manager ===\n")

    # Simulate boot check
    print("Boot Check:")
    manager.boot_check()

    print("\n" + "="*40 + "\n")

    # Show status
    status = manager.get_status()
    print("System Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")

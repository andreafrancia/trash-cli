class Partitions:
    def __init__(self, physical_fstypes):
        self.physical_fstypes = physical_fstypes

    def should_used_by_trashcli(self, partition):
        if ((partition.device, partition.mountpoint,
             partition.fstype) ==
                ('tmpfs', '/tmp', 'tmpfs')):
            return True
        return partition.fstype in self.physical_fstypes

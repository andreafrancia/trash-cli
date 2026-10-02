from trashcli.fstab.volumes import Volumes


class FakeVolumes2(Volumes):
    def __init__(self, volume_of_string, volumes_list):
        self.volume_of_string = volume_of_string
        self.volumes_list = volumes_list

    def volume_of(self, path):
        return self.volume_of_string % path

    def set_volumes(self, volumes_list):
        self.volumes_list = volumes_list

    def list_mount_points(self):
        return self.volumes_list

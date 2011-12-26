# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

import unittest
import StringIO
from trashcli.list_mount_points import _mount_points_from_df_output

class MountPointFromDirTest(unittest.TestCase):

    def test_should_skip_the_first_line(self):
	mount_points = _mount_points_from_df_output(StringIO.StringIO(
	'Filesystem         1024-blocks      Used Available Capacity Mounted on\n'
	))

	self.assertEquals([], list(mount_points))

    def test_should_return_the_first_mount_point(self):
	mount_points = _mount_points_from_df_output(StringIO.StringIO(
	'Filesystem         1024-blocks      Used Available Capacity Mounted on\n'
	'/dev/disk0s2         243862672 121934848 121671824      51% /\n'
	))

	self.assertEquals(['/'], list(mount_points))

    def test_should_return_multiple_mount_point(self):
	mount_points = _mount_points_from_df_output(StringIO.StringIO(
	'Filesystem         1024-blocks      Used Available Capacity Mounted on\n'
	'/dev/disk0s2         243862672 121934848 121671824      51% /\n'
	'/dev/disk1s1         156287996 123044260  33243736      79% /Volumes/DISK\n'
	))

	self.assertEquals(['/', '/Volumes/DISK'], list(mount_points))

    def test_should_return_mount_point_with_white_spaces(self):
	mount_points = _mount_points_from_df_output(StringIO.StringIO(
	'Filesystem         1024-blocks      Used Available Capacity Mounted on\n'
	'/dev/disk0s2         243862672 121934848 121671824      51% /\n'
	'/dev/disk1s1         156287996 123044260  33243736      79% /Volumes/with white spaces\n'
	))

	self.assertEquals(['/', '/Volumes/with white spaces'], list(mount_points))


# Copyright (C) 2008-2011 Andrea Francia Trivolzio(PV) Italy

from unittest import TestCase
from trashcli.trash import TrashDirectory
from trashcli.trash import TrashInfo
from integration_tests.files import require_empty_dir

from datetime import datetime
import os
join = os.path.join

class TestTrashDirectory_persit_trash_info(TestCase) :
    def setUp(self):
        self.trashdirectory_base_dir = os.path.realpath("./sandbox/testTrashDirectory")
        require_empty_dir(self.trashdirectory_base_dir)
        
        self.instance=TrashDirectory(self.trashdirectory_base_dir, "/")
        
    def test_persist_trash_info_first_time(self):
        trash_info=TrashInfo("dummy-path", datetime(2007,01,01))

        basename=os.path.basename(trash_info.path)
        content=trash_info.render()
        (trash_info_file,
                trash_info_id)=self.instance.persist_trash_info(basename,content)

        self.assertEquals('dummy-path', trash_info_id)
        self.assertEquals(join(self.trashdirectory_base_dir,'info', 'dummy-path.trashinfo'), trash_info_file)

        self.assertEquals("[Trash Info]\n"
                          "Path=dummy-path\n"
                          "DeletionDate=2007-01-01T00:00:00\n", 
                          read(trash_info_file))

    def test_persist_trash_info_first_100_times(self):
        self.test_persist_trash_info_first_time()
        
        for i in range(1,100) :
            trash_info=TrashInfo("dummy-path", datetime(2007,01,01))
            
            basename=os.path.basename(trash_info.path)
            content=trash_info.render()
            (trash_info_file,
                    trash_info_id)=self.instance.persist_trash_info(basename,content)
    
            self.assertEquals('dummy-path'+"_" + str(i), trash_info_id)
            self.assertEquals("""[Trash Info]
Path=dummy-path
DeletionDate=2007-01-01T00:00:00
""", read(trash_info_file))

    def test_persist_trash_info_other_times(self):
        self.test_persist_trash_info_first_100_times()
        
        for i in range(101,200) :
            trash_info=TrashInfo("dummy-path", datetime(2007,01,01))
            
            basename=os.path.basename(trash_info.path)
            content=trash_info.render()
            (trash_info_file,
                    trash_info_id)=self.instance.persist_trash_info(basename,content)
    
            self.assertTrue(trash_info_id.startswith("dummy-path_"))
            self.assertEquals("""[Trash Info]
Path=dummy-path
DeletionDate=2007-01-01T00:00:00
""", read(trash_info_file))

def read(path):
    return file(path).read()


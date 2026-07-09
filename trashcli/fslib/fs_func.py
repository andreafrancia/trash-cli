from trashcli.fslib.fs_operations import RealMove
from trashcli.fslib.real_fs_operations import RealHasStickyBit, RealIsStickyDir, RealContentsOf, \
    RealRemoveFile, RealRemoveFile2, RealListFilesInDir, RealMkDirs, \
    RealAtomicWrite, RealReadFile, RealWriteFile, RealMakeFileExecutable, \
    RealFileSize

has_sticky_bit = RealHasStickyBit().has_sticky_bit
contents_of = RealContentsOf().contents_of
remove_file = RealRemoveFile().remove_file
move = RealMove().move
list_files_in_dir = RealListFilesInDir().list_files_in_dir
mkdirs = RealMkDirs().mkdirs
atomic_write = RealAtomicWrite().atomic_write
open_for_write_in_exclusive_and_create_mode = RealAtomicWrite().open_for_write_in_exclusive_and_create_mode
read_file = RealReadFile().read_file
write_file = RealWriteFile().write_file
make_file_executable = RealMakeFileExecutable().make_file_executable
file_size = RealFileSize().file_size
remove_file2 = RealRemoveFile2().remove_file2
is_sticky_dir = RealIsStickyDir().is_sticky_dir

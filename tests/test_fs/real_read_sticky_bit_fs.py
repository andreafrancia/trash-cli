from tests.test_fs.read_sticky_bit_fs import ReadStickyBitFs


class RealReadStickyBitFs(ReadStickyBitFs):
    def is_sticky(self,
                  path,  # type: str
                  ):  # type: (...) -> bool
        import os
        import stat
        # get all the stats
        stat_result = os.stat(path)  # type: os.stat_result
        # pick file mode (file type and file mode bits (permissions))
        # see https://docs.python.org/3/library/os.html
        mode = stat_result.st_mode
        # extract stickiness
        sticky_bit = mode & stat.S_ISVTX  # type: int
        return sticky_bit == stat.S_ISVTX

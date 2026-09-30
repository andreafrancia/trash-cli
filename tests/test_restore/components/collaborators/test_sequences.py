from trashcli.restore.restore_asking_the_user import parse_indexes


class TestSequences:
    def test(self):
        sequences = parse_indexes("1-5,7", 10)
        result = [index for index in sequences.all_indexes()]
        assert result == [1, 2, 3, 4, 5, 7]

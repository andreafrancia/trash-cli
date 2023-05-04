from typing import NamedTuple

from trashcli.fs import PathExists


def has_been_restored(fs): # type: (PathExists) -> HasBeenRestored
    return HasBeenRestored(fs)


class ShouldExists(NamedTuple('ShouldExists', [
    ('name', str), ('path', str)])):
    def expectation_as_text(self):
        return "should exists"

    def should_exists(self):
        return True

    def actual(self, actually_exists):
        return {True: "and it does",
                False: "but it does not"}[actually_exists]


class ShouldNotExists(
    NamedTuple('ShouldNotExists', [('name', str), ('path', str)])):
    def expectation_as_text(self):
        return "should not exists"

    def should_exists(self):
        return False

    def actual(self, actually_exists):
        return {False: "and it does not",
                True: "but it does"}[actually_exists]


class Satisfaction:
    def __init__(self, expectation, actually_exists):
        self.expectation = expectation
        self.actually_exists = actually_exists

    def expectations_satisfied(self):
        return self.actually_exists == self.expectation.should_exists()

    def actual_description(self):
        return self.expectation.actual(self.actually_exists)

    def ok_or_fail_text(self):
        return {True: "OK", False: "FAIL"}[
            self.expectations_satisfied()]

    def kind_of_file(self):
        return self.expectation.name

    def satisfaction_description(self):
        return "{0} {1} {2} {3}: '{4}'".format(
            self.ok_or_fail_text(),
            self.kind_of_file(),
            self.expectation.expectation_as_text(),
            self.actual_description(),
            self.expectation.path
        )


class HasBeenRestored:
    def __init__(self, fs): # type: (PathExists) -> None
        self.fs = fs

    def matches(self, a_trashed_file):
        return len(self._expectations_failed(a_trashed_file)) == 0

    def describe_mismatch(self, a_trashed_file, focus_on=None):
        expectations_satisfactions = self._expectations_satisfactions(
            a_trashed_file,
            focus_on)

        return ("Expected file to be restore but it has not:\n" +
                "".join("  - %s\n" % satisfaction.satisfaction_description()
                        for satisfaction in expectations_satisfactions))

    def describe(self, description):
        return "The file has been restored"

    def _expectations_failed(self, a_trashed_file):
        return [
            satisfaction for satisfaction in
            self._expectations_satisfactions(a_trashed_file, focus_on=None)
            if not satisfaction.expectations_satisfied()]

    def _expectations_satisfactions(self, a_trashed_file, focus_on=None):
        return [
            Satisfaction(e, self.fs.exists(e.path)) for e in
            self._expectations_for(a_trashed_file, focus_on)]

    def _expectations_for(self, a_trashed_file, focus_on=None):
        all_expectations = [
            ShouldExists("original_location", a_trashed_file.trashed_from),
            ShouldNotExists("info_file", a_trashed_file.info_file),
            ShouldNotExists("backup_copy", a_trashed_file.backup_copy),
        ]
        if focus_on is None:
            return all_expectations
        else:
            return [e for e in all_expectations if e.name == focus_on]

from unipath import Path

def create_cmdenv(default_cwd="./sandbox", home_env=Path("./sandbox/home").absolute()):
    import trashcli
    from unipath import Path
    from cmd import CommandEnviroment
    from nose import SkipTest

    cmds_aliases={}
    scripts_dir=Path(trashcli.__file__).parent.parent.child("scripts")
    for i in ["trash-list", "trash-put", "trash-empty", "restore-trash"]:
        command=scripts_dir.child(i)
        if not command.exists():
            raise SkipTest("Script not found: `%s'.\nPlease run 'python setup.py develop -s scripts' before." % command)
        else:
            cmds_aliases[i]=command

    return CommandEnviroment(cmds_aliases, default_cwd, {'HOME':home_env})


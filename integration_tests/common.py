import os
def create_cmdenv(default_cwd="./sandbox", home_env=os.path.abspath("./sandbox/home")):
    import trashcli
    from cmd import CommandEnviroment
    from nose import SkipTest
    parent_of = os.path.dirname
    join = os.path.join

    cmds_aliases={}
    scripts_dir=join(parent_of(parent_of(trashcli.__file__)), 'scripts')
    for i in ["trash-list", "trash-put", "trash-empty", "restore-trash"]:
        command=join(scripts_dir,i)
        if not os.path.exists(command):
            raise SkipTest("Script not found: `%s'.\nPlease run 'python setup.py develop -s scripts' before." % command)
        else:
            cmds_aliases[i]=command

    return CommandEnviroment(cmds_aliases, default_cwd, {'HOME':home_env})


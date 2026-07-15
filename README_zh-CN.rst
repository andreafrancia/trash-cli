trash-cli——FreeDesktop.org 回收站的命令行界面
=============================================

|Donate|_

`English`_

trash-cli
用于移动文件到回收站，同时会记录文件的原地址、删除日期和权限。trash-cli
和 KDE、GNOME、XFCE 使用同一个回收站，你可以在命令行或脚本运行
trash-cli。

trash-cli 提供以下命令：

::

   trash-put           把文件或目录移动到回收站
   trash-empty         清空回收站
   trash-list          列出回收站文件
   trash-restore       恢复回收站文件
   trash-rm            删除回收站文件

用法
----

移动文件到回收站：

::

   $ trash-put foo

列出回收站文件：

::

   $ trash-list
   2008-06-01 10:30:48 /home/andrea/bar
   2008-06-02 21:50:41 /home/andrea/bar
   2008-06-23 21:50:49 /home/andrea/foo

搜索回收站文件：

::

   $ trash-list | grep foo
   2007-08-30 12:36:00 /home/andrea/foo
   2007-08-30 12:39:41 /home/andrea/foo

恢复一个回收站文件：

::

   $ trash-restore
   0 2007-08-30 12:36:00 /home/andrea/foo
   1 2007-08-30 12:39:41 /home/andrea/bar
   2 2007-08-30 12:39:41 /home/andrea/bar2
   3 2007-08-30 12:39:41 /home/andrea/foo2
   4 2007-08-30 12:39:41 /home/andrea/foo
   What file to restore [0..4]: 4
   $ ls foo
   foo

恢复一个回收站文件并且覆盖已存在的文件：

::

    $ echo "original">foo
    $ ls
    foo
    $ trash-put foo
    $ echo "new">foo
    $ trash-restore --overwrite
    0 2022-11-01 22:15:00 /home/andrea/foo
    What file to restore [0..0]: 0
    $ cat foo
    original

通过','（逗号）分隔文件以恢复多个回收站文件。也支持范围：

::

   $ trash-restore
   0 2007-08-30 12:36:00 /home/andrea/foo
   1 2007-08-30 12:39:41 /home/andrea/bar
   2 2007-08-30 12:39:41 /home/andrea/bar2
   3 2007-08-30 12:39:41 /home/andrea/foo2
   What file to restore [0..3]: 0-2, 3
   $ ls foo bar bar2 foo2
   foo bar bar2 foo2

删除所有回收站文件：

::

   $ trash-empty

删除回收站中 <n> 天前被回收的文件：

::

   $ trash-empty <n>

示例：

::

   $ date
   Tue Feb 19 20:26:52 CET 2008
   $ trash-list
   2008-02-19 20:11:34 /home/einar/today
   2008-02-18 20:11:34 /home/einar/yesterday
   2008-02-10 20:11:34 /home/einar/last_week
   $ trash-empty 7
   $ trash-list
   2008-02-19 20:11:34 /home/einar/today
   2008-02-18 20:11:34 /home/einar/yesterday
   $ trash-empty 1
   $ trash-list
   2008-02-19 20:11:34 /home/einar/today

只删除符合某种模式的文件：

::

   $ trash-rm \*.o

注意：要用双引号圈住模式来避免 shell 拓展。

常见问题
--------

如何创建顶级 .Trash 目录？
~~~~~~~~~~~~~~~~~~~~~~~~~~

步骤：

::

   sudo mkdir --parent /.Trash
   sudo chmod a+rw /.Trash
   sudo chmod +t /.Trash

我能把 `rm` 的别名设置为 `trash-put` 吗？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

可以，但不应该这样做。以前我觉得这是个好主意，但现在我不觉得。

虽然 `trash-put` 的界面看起来与 `rm`
兼容，但它们有不同的语法，这些差异会导致一些问题。比如，用 `rm`
删除目录时需要 `-R`\ ，\ `trash-put` 则不需要。

但有时候我忘记用 `trash-put` 了，真的不能给 `rm` 设置别名吗？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

你可以给 `rm` 设置一个别名来提醒你不要使用它：

::

   alias rm='echo "This is not the command you are looking for."; false'

如果你真的要用 `rm`\ ，那就在 `rm` 前加上斜杠来取消别名：

::

   \rm file-without-hope

注意，Bash 别名是有在交互式界面才有效，所以使用这个别名不会影响使用 `rm`
的脚本。

被移动到回收站的文件在哪？
~~~~~~~~~~~~~~~~~~~~~~~~~~

从 home 分区移动到回收站的文件在这：

::

   ~/.local/share/Trash/

怎么自动删除回收站30天前的文件？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

运行以下命令：

::

   (crontab -l ; echo "@daily $(which trash-empty) 30") | crontab -

这会更新你的 crontab 文件，添加一个每天运行的 `trash-empty` 命令来删除30天前的文件。要查看你的 crontab，请使用：`crontab -l`

安装
----

简单方法
~~~~~~~~

要求：

   -  Python 3 (Python 2.7 也可以)
   -  pipx_ (可选，为了在干净的环境中安装)

如果 pipx 可用:

::

    pipx install trash-cli

此外, 用原版 pip 安装

::

    pip install trash-cli

注意：你可能想添加 ~/.local/bin 到你的 PATH 环境变量中：

::

   echo 'export PATH="$PATH":~/.local/bin' >> ~/.bashrc
   source ~/.bashrc # reload .bashrc

卸载命令：

::
   
   pipx uninstall trash-cli
   # 或者
   pip uninstall trash-cli

最新版本（源码安装）
~~~~~~~~~~~~~~~~~~
首先你要卸载任何之前安装的 trash-cli 版本

::

    $ [sudo] pip uninstall trash-cli # remove the previous version (with pip)
    $ [sudo] apt-get remove trash-cli # remove the previous version (with apt)
    $ [sudo] yum uninstall trash-cli # remove the previous version (with yum)
    $ ... # 取决于你使用的发行版的包管理器

然后从 git 安装最新版本

::

    $ [sudo] pip install git+https://github.com/andreafrancia/trash-cli

在用户安装后，你可能想把以下代码添加到 .bashrc/.zshrc：

::

    export PATH=~/.local/bin:"$PATH"

从包管理器安装
~~~~~~~~~~~~~~~~~~~~

Debian/Ubuntu (apt)::

    sudo apt install trash-cli

Arch Linux (pacman)::

    sudo pacman -S trash-cli

Fedora (dnf)::

    sudo dnf install trash-cli

MacOS (Homebrew)::

    brew install trash-cli
    echo 'export PATH="~/homebrew/opt/trash-cli/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc

安装 shell 补全
~~~~~~~~~~~~~~~~~~~~~~~~~

你需要通过以下命令安装

::

    pipx install 'trash-cli[completion]'

或者

::

    pip install 'trash-cli[completion]'

然后

::

    cmds=(trash-empty trash-list trash-restore trash-put trash)
    for cmd in ${cmds[@]}; do
      $cmd --print-completion bash | sudo tee /usr/share/bash-completion/completions/$cmd
      $cmd --print-completion zsh | sudo tee /usr/share/zsh/site-functions/_$cmd
      $cmd --print-completion tcsh | sudo tee /etc/profile.d/$cmd.completion.csh
    done

缺乏对 Btrfs 卷的支持
---------------------------------
trash-cli 不支持 Btrfs 卷。
我没有相关系统，时间和/或知识来实现这样的支持。

如果你需要一个回收站实现，请查看 `rmw`_ 项目。

.. _rmw: https://github.com/theimpossibleastronaut/rmw

如果你想、可以并且知道如何添加对 Btrfs 的支持，并且有合理的自动化测试，请发送一个 pull request。

Bugs
----

如果你发现一个 bug 请在这里报告:

    https://github.com/andreafrancia/trash-cli/issues

反馈
--------

你可以通过 andrea@andreafrancia.it 发给我邮件.

开发
----

环境设置：

::

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt -r requirements.txt

运行测试：

::

   pytest -m 'not slow'        # 只运行快测试
   pytest -m 'slow'            # 运行慢测试
   pytest                      # 运行所有测试

感谢
------
感谢通过 Paypal 捐献的捐赠者.

感谢 `项目贡献者`_.

感谢 `JetBrains`_  为开源开发提供的许可证。

.. |Donate| image:: https://www.paypalobjects.com/en_GB/i/btn/btn_donate_SM.gif
.. _Donate: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=93L6PYT4WBN5A
.. _English: https://github.com/andreafrancia/trash-cli/blob/master/README.rst
.. _pipx: https://pypa.github.io/pipx
.. _项目贡献者: https://github.com/andreafrancia/trash-cli/graphs/contributors
.. _JetBrains: https://jb.gg/OpenSource

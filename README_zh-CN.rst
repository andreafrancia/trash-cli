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

   $ trash-put

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

恢复回收站文件：

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

删除所有回收站文件：

::

   $ trash-empty

删除回收站中 n 天前被回收的文件：

::

   $ trash-empty <days>

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

安装
----

简单方法
~~~~~~~~

要求：

   -  Python 3 (Python 2.7 也可以)
   -  pip (在 Debian 上用 `apt-get install python-pip` 来安装 pip)

安装命令:

::

   pip install trash-cli

源码安装
~~~~~~~~

为所有用户安装：

::

   git clone https://github.com/andreafrancia/trash-cli.git
   cd trash-cli
   sudo pip install .

为当前用户安装：

::

   git clone https://github.com/andreafrancia/trash-cli.git
   cd trash-cli
   pip install .

为当前用户安装后你可能需要把以下代码添加到 .bashrc：

::

   export PATH=~/.local/bin:"$PATH"

卸载命令：

::

   pip uninstall trash-cli

反馈与 Bug 报告
---------------

如果你发现了 bug，请在这里报告：

   https://github.com/andreafrancia/trash-cli/issues

你也可以给我发邮件 andrea@andreafrancia.it\ 。我的推特帐号是
@andreafrancia。

开发
----

环境设置：

::

   virtualenv env --no-site-packages
   source env/bin/activate
   pip install -r requirements-dev.txt

运行测试：

::

   pytest unit_tests           # 只运行单元测试
   pytest integration_tests    # 运行所有集成测试
   pytest                      # 运行所有测试

发布前检测安装进程：

::

   python check_release_installation.py

.. |Donate| image:: https://www.paypalobjects.com/en_GB/i/btn/btn_donate_SM.gif
.. _Donate: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=93L6PYT4WBN5A
.. _English: https://github.com/andreafrancia/trash-cli/blob/master/README.rst

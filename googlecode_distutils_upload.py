# Copyright 2007 Google Inc. All Rights Reserved.
#
# Licensed under the terms of the Apache Software License 2.0:
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Questions, comments, feature requests and patches are most welcome.
# Please direct all of these to the Google Code users group:
#  http://groups.google.com/group/google-code-hosting

'''distutils command class for uploading to Google Code

Add this command to your setup.py script for automatic uploading of
source and Windows binary distributions.  For example:

try:
  from googlecode_distutils_upload import upload
except ImportError:
  class upload(distutils.core.Command):
    user_options = []
    def __init__(self, *args, **kwargs):
      sys.stderr.write("""\
error: Install this module in site-packages to upload:
 http://support.googlecode.com/svn/trunk/scripts/googlecode_distutils_upload.py
""")
      sys.exit(3)

setup(...,
      cmdclass={'upload': upload},
      )
'''



import distutils
import distutils.command.bdist_wininst
import os
import sys

import googlecode_upload


SOURCE_LABELS = ['Type-Source']
WINDOWS_LABELS = ['OpSys-Windows', 'Type-Installer']


class upload(distutils.core.Command):
  description = 'upload source or Windows distribution to Google Code'
  user_options = [('src', None,
                   'upload source distribution'),
                  ('windows', None,
                   'upload Windows distribution'),
                  ('dist-dir=', 'd',
                   'directory to find distribution archive in'
                   ' [default: dist]'),
                  ('config-dir=', None,
                   'read svn auth data from DIR'
                   ' ("none" means not to use svn auth data)'),
                  ('user=', 'u',
                   'Google Code username'),
                  ]
  boolean_options = ['src', 'windows']

  def initialize_options(self):
    self.src = False
    self.windows = False
    self.dist_dir = None
    self.config_dir = None
    self.user = None

  def finalize_options(self):
    # Validate src and windows options.
    if (not self.src and not self.windows) or (self.src and self.windows):
      sys.stderr.write('error: Use exactly one of --src or --windows\n')
      sys.exit(2)

    # Get dist-dir default from sdist or bdist_wininst.
    if self.src:
      self.set_undefined_options('sdist', ('dist_dir', 'dist_dir'))
    else:
      self.set_undefined_options('bdist_wininst', ('dist_dir', 'dist_dir'))

    # Do nothing for config-dir and user; upload_find_auth does the
    # right thing when they're None.

  def run(self):
    name = self.distribution.get_name()
    version = self.distribution.get_version()

    if self.src:
      # TODO(epg): sdist is more flexible with formats...
      fn = os.path.join(self.dist_dir, self.distribution.get_fullname())
      if sys.platform == 'win32':
        fn += '.zip'
      else:
        fn += '.tar.gz'
      summary = ' '.join([name, version, 'source distribution'])
      labels = SOURCE_LABELS
    else:
      # Get filename from bdist_wininst.
      bd = distutils.command.bdist_wininst.bdist_wininst(self.distribution)
      bd.initialize_options()
      bd.dist_dir = self.dist_dir
      bd.finalize_options()
      fn = bd.get_installer_filename(self.distribution.get_fullname())
      summary = ' '.join([name, version, 'for Windows'])
      labels = WINDOWS_LABELS

    (status, reason,
     file_url) = googlecode_upload.upload_find_auth(fn, name, summary,
                                                    labels, self.config_dir,
                                                    self.user)

    if file_url is None:
      sys.stderr.write('error: %s (%d)\n' % (reason, status))
      sys.exit(2)

    sys.stdout.write('Uploaded %s\n' % (file_url,))

# -*- coding: utf-8 -*-

if __name__ == '__main__':
    exit(1)

import os
import subprocess
import logging
import hashlib
import stat

logger = logging.getLogger(__name__)

class Bootstrap(object):
    working_dir = None
    bootstrap_dir = None
    virtualenv_dir = None


    def __init__(self, working_dir=None):
        self.working_dir = working_dir or os.getcwd()
        self.bootstrap_dir = self._config_dot_dir('BOOTSTRAP_DIR', '.bootstrap')
        self.virtualenv_dir = self._config_dot_dir('VIRTUALENV_DIR', '.virtualenv')

        if not os.path.isdir(self.bootstrap_dir):
            os.makedirs(self.bootstrap_dir)

        logger.debug('working_dir: %s', self.working_dir)
        logger.debug('bootstrap_dir: %s', self.bootstrap_dir)
        logger.debug('virtualenv_dir: %s', self.virtualenv_dir)

        self.install_virtualenv()
        self.install_ve()


    def _config_dot_dir(self, env_name, default_value=None):
        value = os.environ.get(env_name)
        if not value:
            return '%s/%s' % (self.working_dir, default_value)

        logger.debug('config %s from envron', env_name)
        if os.path.isabs(value):
            return value
        else:
            return '%s/%s' % (self.working_dir, value)


    def install_virtualenv(self):
        if os.path.isfile('%s/%s' % (self.virtualenv_dir, 'bin/activate')):
            return

        executable = None
        try:
            executable = subprocess.check_output(['command', '-v', 'virtualenv-1.11.4/virtualenv.py'])
            if not type(executable) is str:
                # convert from bytes to str (unicode) under python3
                executable = executable.decode()
            executable = executable.strip()
        except:
            pass

        if not executable:
            virtualenv_tar = '%s/%s' % (self.bootstrap_dir, 'virtualenv.tar.gz')
            executable = '%s/%s' % (self.bootstrap_dir, 'virtualenv-1.11.4/virtualenv.py')
            self.download('https://github.com/pypa/virtualenv/archive/1.11.4.tar.gz', 
                         virtualenv_tar, '6dc938b8a5c818f773e09049469bba05')
            os.system('tar -zxvf "%s" -C "%s"' % (virtualenv_tar, self.bootstrap_dir))

        os.chdir(self.bootstrap_dir)
        try:
            os.system('%s --distribute --no-site-packages "%s"' % (executable, self.virtualenv_dir))
        finally:
            os.chdir(self.working_dir)


    def download(self, source, target, hashing=None):
        if hashing and os.path.isfile(target) and hashing == self.md5sum(target):
            return
        if os.system('wget "%s" -O "%s"' % (source, target)) == 0:
            return
        if os.system('curl "%s" -o "%s"' % (source, target)) == 0:
            return

        logger.error('Unable to download "%s"' % source)
        raise RuntimeError


    def mark_executable(self, path):
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


    def md5sum(self, filename):
        return hashlib.md5(open(filename, 'rb').read()).hexdigest()


    def install_ve(self):
        executable = '%s/%s' % (self.bootstrap_dir, 've')
        self.download('https://raw.github.com/erning/ve/v1.1/ve',
                      executable, 'fd0f0601c6732ca9a5b3b62e691d68cb')
        self.mark_executable(executable)


    def ve(self, cmd):
        os.system('%s/%s %s' % (self.bootstrap_dir, 've', cmd))


_bootstrap = None

__all_ = ['bootstrap', 've']

def bootstrap(working_dir=None):
    global _bootstrap
    _bootstrap = Bootstrap(working_dir)

def ve(cmd):
    global _bootstrap
    if not _bootstrap:
        bootstrap()
    _bootstrap.ve(cmd)

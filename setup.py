from setuptools import setup
from setuptools.command.install import install as DistutilsInstall
from setuptools.command.egg_info import egg_info as EggInfo

class MyInstall(DistutilsInstall):
    def run(self):
        DistutilsInstall.run(self)

class MyEgg(EggInfo):
    def run(self):
        EggInfo.run(self)

setup(name='box2dsim',
        version='0.1',
        cmdclass = {
            'install': MyInstall,
            'egg_info': MyEgg
            },
        install_requires=['gym', 'box2d', 'numpy', 
            'matplotlib','scikit-image']
        )

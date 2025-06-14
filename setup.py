import sys
import os.path

from setuptools import setup
from setuptools import find_packages

import shutil
from setuptools import setup, Command

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        shutil.rmtree('build', ignore_errors=True)
        shutil.rmtree('dist', ignore_errors=True)
        shutil.rmtree('pcgrl.egg-info', ignore_errors=True)


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pcgrl"))

setup(
    cmdclass={'clean': CleanCommand},
    name='pcgrl',
    version='0.0.0.1',
    install_requires=['gym'],
    author="Paulo Vinícius Moreira Dutra",
    author_email="paulo.dutra@ifsudestemg.edu.br",
    description="A package for \"Procedural Content Generation via Reinforcement Learning\" OpenAI Gym interface.",
    url="https://github.com/dutrapaulovm/pcgrl-puzzle",
    keywords=' '.join([
        'OpenAI-Gym',       
        'Procedural-Content-Generation',        
        'Reinforcement-Learning-Environment',
    ]),    
    project_urls={
        "Bug Tracker": "https://github.com/dutrapaulovm/pcgrl-puzzle/issues",
    },
    packages=[package for package in find_packages() if package.startswith("pcgrl")],    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',        
        "Programming Language :: Python :: 3",        
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Games/Entertainment',   
        'Topic :: Software Development :: Libraries :: Python Modules',             
    ],
    python_requires=">=3.7"       
)
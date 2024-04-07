# -*- coding: utf-8 -*-
from setuptools import setup
import time

setup(
	name='irc3-twitch',
	description='Some plugins for irc3',
	version='0.0.%s.dev0' % time.time(),

	packages=['plugins'],
	install_requires=['irc3', 'aiocron', 'feedparser', 'requests', 'tzlocal'],
	entry_points={
		'console_scripts': ['irc3 = irc3:run']
	},

	license='MIT',
	author='Lee Williams',
	author_email='git@mentalfs.de',
	url='https://github.com/MentalFS/irc3-twitch',
)

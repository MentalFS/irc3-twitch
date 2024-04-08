# -*- coding: utf-8 -*-
from setuptools import setup

setup(
	name='irc3-twitch',
	description='Some plugins for irc3',
	version='0.0.0.0.dev0',

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

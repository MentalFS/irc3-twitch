# -*- coding: utf-8 -*-
from setuptools import setup
from datetime import datetime

setup(
	name='irc3-twitch',
	description='Some plugins for irc3',
	version=datetime.today().strftime('%Y.%m.%d.%H%M'),

	packages=['plugins'],
	install_requires=['irc3==1.1.12', 'aiocron', 'feedparser', 'requests', 'tzlocal'],
	entry_points={
		'console_scripts': ['irc3 = irc3:run']
	},

	license='MIT',
	author='Lee Williams',
	author_email='git@mentalfs.de',
	url='https://github.com/MentalFS/irc3-twitch',
)

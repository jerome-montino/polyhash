from setuptools import setup

install_requires = ['shapely', 'python-geohash', 'georaptor']

setup(
    name='polyhash',
	version='1.0.0',
	description='Python library for converting polygons to geohashes and vice versa.',
	author='Jerome Montino',
    author_email='jerome.montino@gmail.com',
    url='https://github.com/jerome-montino/polyhash',
    license='MIT',
    install_requires=install_requires
)
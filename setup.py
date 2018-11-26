from setuptools import setup, find_packages

install_requires = ['Shapely', 'python-geohash', 'georaptor']

setup(
    name='python-polyhash',
	version='0.3.0',
	description='Python library for converting polygons to geohashes and vice versa.',
	author='Jerome Montino',
    author_email='jerome.montino@gmail.com',
    url='https://github.com/jerome-montino/polyhash',
    license='MIT',
    py_modules=['polyhash'],
    install_requires=install_requires
)
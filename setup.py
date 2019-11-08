from setuptools import setup

setup(
    name='bitmap2ttf',
    version='1.0.0',
    author='Alistair Buxton',
    author_email='a.j.buxton@gmail.com',
    url='http://github.com/ali1234/bitmap2ttf',
    packages=['bitmap2ttf'],
    entry_points={
        'console_scripts': [
            'pcftottf = bitmap2ttf.pcftottf:pcftottf',
            'amigatottf = bitmap2ttf.amigatottf:amigatottf',
        ],
    },
    install_requires=[
        'pillow', 'click', 'tqdm',
    ],
)

from setuptools import setup
import versioneer

requirements = [
    # package requirements go here
]

setup(
    name='pianoman',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="ey/value configuration parser/manager considering input form",
    license="Apache",
    author="Kevin German",
    author_email='kevin.german@gmail.com',
    url='https://github.com/kevingerman/pianoman',
    packages=['pianoman'],
    
    install_requires=requirements,
    keywords='pianoman',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)

from setuptools import setup, find_packages

setup(
    name='icc.contentstorage',
    version='0.0.1',
    long_description=__doc__,
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'kyotocabinet',
        'zope.interface',
        'zope.component [zcml]',
    ]
)
quit()

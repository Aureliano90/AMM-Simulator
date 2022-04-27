from setuptools import setup, find_packages

setup(
    name='AMM-Simulator',
    version='0.2.0',
    packages=find_packages(),
    url='https://github.com/Aureliano90/AMM-Simulator',
    license='GNU Affero General Public License v3.0',
    author='Aureliano',
    author_email='shuhui.1990+@gmail.com',
    description='',
    python_requires=">=3.8",
    install_requires=['requests~=2.27.1',
                      'httpcore~=0.14.7',
                      'httpx[http2]~=0.22.0',
                      'pymongo~=4.1.1',
                      'matplotlib~=3.5.1',
                      'numpy~=1.22.3',
                      'websockets~=10.3'],
    entry_points={
            'console_scripts':
                'ok = main:main'
            },
)

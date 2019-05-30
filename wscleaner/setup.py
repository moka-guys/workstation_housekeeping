from setuptools import setup, find_packages

setup(name='wscleaner',
      version='1.0',
      description='Package to remove uploaded runfolders from \
          the Viapath Genome Informatics NGS workstation',
      url='https://github.com/NMNS93/wscleaner',
      author='Nana Mensah',
      author_email='gst-tr.MokaGuys@nhs.net',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      
      python_requires = '>=3.6.8',
      install_requires = ['docutils>=0.3', 'dxpy==0.279.0', 'pytest==4.4.0', 'pytest-cov==2.6.1',
        'Sphinx==2.0.1', 'psutil==5.6.1'],

      package_data = {},

      entry_points={
          'console_scripts': 'wscleaner = wscleaner.main:main'
      }
       
      )

from setuptools import setup, find_namespace_packages

setup(name='fish_reg',
      packages=find_namespace_packages(include=["fish_reg/*"]),
      version='0.0.1',
      description='fish video registration software',
      url='https://github.com/meglaficus/fish_reg',
      author='Jakob Meglič',
      author_email='jakobmeglic123@gmail.com',
      license='Apache License Version 2.0, January 2004',
      install_requires=[
          "tqdm",
          "SimpleITK",
          "SimpleITK-SimpleElastix",
          "numpy",
      ],
      entry_points={
          'console_scripts': [
              'fish_reg_execute = fish_reg.run:main',
          ]
      },
      keywords=['elastix', 'zebrafish', 'video', 'registration']
      )

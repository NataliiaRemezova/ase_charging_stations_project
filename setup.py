from setuptools import setup, find_packages

setup(
    name='ase_charging_stations_project',
    version='0.1',
    packages=find_packages(),  # Automatically find all packages (folders with __init__.py)
    install_requires=[  # Add runtime dependencies here
        # For example, 'numpy>=1.21.0',
    ],
    entry_points={
        # Optional: Add console scripts for easy command-line use
        # 'console_scripts': [
        #     'my_command = my_project.some_module:main_function',
        # ],
    },
)

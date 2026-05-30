from setuptools import find_packages, setup

package_name = 'pseudo_rgbd_slam'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/pipeline.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu2204',
    maintainer_email='“sourabha.lolage@gmail.com”',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'node_a_broadcaster = pseudo_rgbd_slam.node_a_broadcaster:main',
            'node_b_depth_estimator = pseudo_rgbd_slam.node_b_depth_estimator:main',
        ],
    },
)

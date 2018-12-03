from setuptools import find_packages, setup

setup(
    name='step',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask','flask-sqlalchemy','pymysql','flask-restful','passlib','flask_jwt_extended'#,'flask-marshmallow'
    ],
)
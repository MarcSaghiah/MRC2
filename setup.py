from setuptools import setup, find_packages

setup(
    name="MRC2",  # Remplacez par le nom de votre projet
    version="0.1.0",  # Version initiale
    author="MarcSag",  # Votre nom ou pseudonyme
    author_email="votre_email@example.com",  # Remplacez par votre adresse email
    description="Description courte de votre projet",
    long_description=open("README.md").read(),  # Longue description lue dans un fichier README.md
    long_description_content_type="text/markdown",
    url="https://github.com/MarcSag/MRC2",  # Remplacez par l'URL de votre dépôt GitHub
    packages=find_packages(),  # Recherche automatiquement les modules Python dans votre projet
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Remplacez par la licence réelle de votre projet
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # Version minimale requise de Python
    install_requires=[
        # Ajoutez ici vos dépendances du projet, par exemple :
        # "numpy>=1.21.0",
        # "requests>=2.26.0",
    ],
)
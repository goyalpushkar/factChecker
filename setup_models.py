import spacy
import nltk

MODELS_TO_DOWNLOAD = ["en_core_web_sm"]
NLTK_PACKAGES = ["punkt", "wordnet", "stopwords", "averaged_perceptron_tagger"]

def download_spacy_models():
    """Downloads all specified spaCy models."""
    for model in MODELS_TO_DOWNLOAD:
        try:
            spacy.load(model)
            print(f"Model '{model}' already installed.")
        except OSError:
            print(f"Downloading spaCy model: {model}")
            spacy.cli.download(model)
            print(f"Spacy model '{model}' downloaded and loaded successfully.")

def download_nltk_packages():
    """Downloads all specified NLTK packages."""
    for package in NLTK_PACKAGES:
        try:
            # Check if the package is already available
            nltk.data.find(f'tokenizers/{package}' if package == 'punkt' else f'corpora/{package}' if package in ['wordnet', 'stopwords'] else f'taggers/{package}')
            print(f"NLTK package '{package}' already installed.")
        except LookupError:
            print(f"Downloading NLTK package: {package}")
            nltk.download(package)
            print(f"NLTK package '{package}' downloaded successfully.")

if __name__ == "__main__":
    print("--- Setting up NLP models ---")
    download_spacy_models()
    print("\n--- Setting up NLTK packages ---")
    download_nltk_packages()
    print("\n--- Model setup complete! ---")

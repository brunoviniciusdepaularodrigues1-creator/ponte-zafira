def extract_features(text):
    words = text.split()
    
    length = len(text)
    word_count = len(words)
    unique_words = len(set(words))

    complexity = unique_words / (word_count + 1)

    return {
        "length": length,
        "word_count": word_count,
        "complexity": complexity
    }

import nltk
import sys
import os
import string
import numpy

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    result = dict()
    files = os.listdir(directory)
    for file in files:
        with open(os.path.join(directory, file), 'r', encoding='utf8') as f:
            result.update({file: f.read()})
    return result


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    interim = []
    for char in document:
        if char not in string.punctuation and nltk.corpus.stopwords.words("english"):
            interim.append(char.lower())
    # remove the first entry which is the url
    result = nltk.tokenize.word_tokenize(''.join(interim))
    return result

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    document_count = dict()
    # calculate total number of documents through len()
    total_documents = len(documents)
    for document in documents:
        for word in documents[document]:
            # use add filename to document_count to
            # calculate number of documents word is in through
            # len()
            if word not in document_count:
                document_count[word] = {document}
            else:
                document_count[word].add(document)
    idf = dict()
    for word in document_count:
        idf.update({word: numpy.log(total_documents / len(document_count[word]))})
    return idf


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    words = []
    # remove stopwords in query
    for word in query:
        if word not in nltk.corpus.stopwords.words('english'):
            words.append(word)
    # dict that handles tf_idf values
    tf_idf = dict()
    for keyword in words:
        for file in files:
            count = 0
            for word in files[file]:
                if word == keyword:
                    count += 1
            if file not in tf_idf:
                tf_idf[file] = count * idfs[keyword]
            else:
                tf_idf[file] += count * idfs[keyword]
    interim = []
    for key in tf_idf:
        interim.append((key, tf_idf[key]))
    # sort by tf-idf score
    interim.sort(key=lambda tup: tup[1], reverse=True)
    if len(interim) != n:
        interim = interim[:n]
    result = []
    for combo in interim:
        result.append(combo[0])
    return result


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    words = []
    idf_values = dict()
    matches = dict()
    # remove stopwords in query
    for word in query:
        if word not in nltk.corpus.stopwords.words('english'):
            words.append(word)
    for keyword in words:
        for sentence in sentences:
            if keyword in sentences[sentence]:
                if sentence not in idf_values:
                    idf_values[sentence] = idfs[keyword]
                else:
                    idf_values[sentence] += idfs[keyword]
                if sentence not in matches:
                    matches[sentence] = 1
                else:
                    matches[sentence] += 1
    interim = []
    for key in idf_values:
        length = len(sentences[key])
        interim.append((key, idf_values[key], matches[key] / length))
    interim.sort(key=lambda tup: (tup[1], tup[2]), reverse=True)
    result = []
    for i in range(n):
        result.append(interim[i][0])
    return result


if __name__ == "__main__":
    main()

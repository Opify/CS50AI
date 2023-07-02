import os
import random
import re
import sys
import numpy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    n = 0
    ITERATIONS = 100
    result = dict()
    for entry in corpus:
        result.update({entry: 0})
    for i in range(ITERATIONS):
        rand = random.random()
        # rand <= damping_factor to access another page connected 
        # to current page
        if rand <= damping_factor:
            # if page has no outgoing links, assume it has links to all
            # pages including itself and randomly select one
            if not corpus[page]:
                visit = random.choice(list(corpus))
                result[visit] += 1
            else:
                # randomly select a page it is connected to 
                visit = random.choice(list(corpus[page]))
                result[visit] += 1
        # rand > damping_factor to access random page in corpus
        else:
            visit = random.choice(list(corpus))
            result[visit] += 1
        n += 1
    # convert raw count to probability
    for key, value in result.items():
        result[key] = value / ITERATIONS
    return result
    


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # for 1st iteration, set up model
    page = random.choice(list(corpus))
    result = dict()
    for entry in corpus:
        result.update({entry: 0})
    result[page] += 1
    model = transition_model(corpus, page, damping_factor)
    probabilites = []
    for entry in model:
        probabilites.append(model[entry])
    # for subsequent iterations, use page selected from previous
    # transition model, then update transition model
    for i in range(n - 1):
        page = numpy.random.choice(list(corpus), p=probabilites)
        result[page] += 1
        results = transition_model(corpus, page, damping_factor)
        probabilites = []
        for entry in results:
            probabilites.append(results[entry])
    for key, value in result.items():
        result[key] = value / n
    return result


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    result = dict()
    # initialise result with 1 / N where N is len(corpus)
    for entry in corpus:
        result.update({entry: (1 / N)})
    # loop until all pagerank values stay constant
    constant = 0
    while (constant != N):
        constant = 0
        for entry in corpus:
            old = result[entry]
            sum = 0
            # check if other pages link to selected page
            for other in corpus:
                if entry in corpus[other] and entry != other:
                    # using given pagerank equation
                    pr = result[other]
                    numlinks = len(corpus[other])
                    sum += (pr / numlinks)
            new = ((1 - DAMPING) / N) + (DAMPING * sum)
            # if values fluctuate by 0.001 or less, flag as constant
            # if all pagerank values are constant, constant = N and
            # so the loop will stop
            if abs(new - old) <= 0.001:
                constant += 1
            result[entry] = new
    return result



if __name__ == "__main__":
    main()

import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    def has_genes(person, one_gene, two_genes):
        if person in one_gene:
            return 1
        elif person in two_genes:
            return 2
        else:
            return 0

    def inheritance(person, one_gene, two_genes):
        if person in one_gene:
            return 0.5
        elif person in two_genes:
            return 1 - PROBS["mutation"]
        else:
            return 0 + PROBS["mutation"]
    
    result = 1
    for person in people.items():
        # main dict is in index 1 of the tuple from items()
        # check if person has trait
        if person[1]["name"] in have_trait:
            has_trait = True
        else:
            has_trait = False
        # check if person has 0, 1 or 2 genes
        gene = has_genes(person[1]["name"], one_gene, two_genes)
        # if person has no parents, use unconditional probability of
        # having genes
        if person[1]["mother"] is None and person[1]["father"] is None:
            result *= PROBS["gene"][gene] * PROBS["trait"][gene][has_trait]
        # if person has parents, give (100 - mutation)% chance of getting 
        # gene from a parent if they have 2 genes, (50 -  mutation)% 
        # chance of getting gene from a parent if they have 1 gene and
        # mutatuon% chance of getting gene from a parent if they have 
        # no genes
        else:
            father = person[1]["father"]
            mother = person[1]["mother"]
            # get likelihood of getting gene from parents
            father_gene = inheritance(father, one_gene, two_genes)
            mother_gene = inheritance(mother, one_gene, two_genes)
            # P(genes from both father and mother) * P(has_trait)
            if gene == 2:
                result *= father_gene * mother_gene * PROBS["trait"][gene][has_trait]
            #P(gene from father or mother) * P(has_trait)
            elif gene == 1:
                result *= ((father_gene * (1 - mother_gene)) + ((1 - father_gene) * mother_gene)) * PROBS["trait"][gene][has_trait]
            # P(no gene from father and mother) * P(has_trait)
            else:
                result *= (1 - father_gene) * (1 - mother_gene) * PROBS["trait"][gene][has_trait]
    return result

            
def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    def has_genes(person, one_gene, two_genes):
        if person in one_gene:
            return 1
        elif person in two_genes:
            return 2
        else:
            return 0

    def has_trait(person, have_trait):
        if person in have_trait:
            return True
        else:
            return False

    for person in probabilities.items():
        # index 0 is where the name resides
        gene = has_genes(person[0], one_gene, two_genes)
        trait = has_trait(person[0], have_trait)
        probabilities[person[0]]["gene"][gene] += p
        probabilities[person[0]]["trait"][trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # since all probabilities for each person have a similar base, 
    # we can simply use the first person's gene and trait probability
    # to rebase all records
    gene_base = 0
    trait_base = 0
    for entry in probabilities.items():
        gene_base += entry[1]["gene"][2] + entry[1]["gene"][1] + entry[1]["gene"][0]
        trait_base += entry[1]["trait"][True] + entry[1]["trait"][False]
        break
    for key in probabilities:
        for num in probabilities[key]["gene"]:
            probabilities[key]["gene"][num] /= gene_base
        for bool in probabilities[key]["trait"]:
            probabilities[key]["trait"][bool] /= trait_base


if __name__ == "__main__":
    main()

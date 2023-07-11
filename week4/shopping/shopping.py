import csv
import sys
import datetime

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    # Indexes to convert non-numerical values to numerical values:
    # 10 (Month), 15 (VisitorType), 16 (Weekend), 17 (Revenue)
    # Indexes to convert str to int:
    # 0, 2, 4, 11 to 14
    # Indexes to convert str to float:
    # 1, 3, 5 to 9
    with open(filename) as file:
        reader = csv.reader(file)
        evidence = []
        labels = []
        # ignore header
        next(reader)
        for row in reader:
            # manipulate read data to fit to model
            for i in range(len(row) - 1):
                if i in [0, 2, 4, 11, 12, 13, 14]:
                    row[i] = int(row[i])
                elif i in [1, 3, 5, 6, 7, 8, 9]:
                    row[i] = float(row[i])
                elif i == 10:
                    # Use strptime to convert shortform month name
                    # to int (str must first be converted to datetime)
                    if row[i] == "June":
                        # June is a full month name so %B must be 
                        # used instead of %b (why is there June 
                        # and not Jun)
                        row[i] = int(datetime.datetime.strptime(row[i], "%B").strftime("%m")) - 1
                    else:
                        row[i] = int(datetime.datetime.strptime(row[i], "%b").strftime("%m")) - 1
                elif i == 15:
                    # Convert "Returning_Visitor" to 1 and all
                    # other visitors to 0
                    if row[i] == "Returning_Visitor":
                        row[i] = 1
                    else:
                        row[i] = 0
                elif i == 16:
                    # convert string boolean to int
                    if row[i] == "TRUE":
                        row[i] = 1
                    else:
                        row[i] = 0
            if row[17] == "TRUE":
                # convert string boolean to int
                row[17] = 1
            else:
                row[17] = 0
            evidence.append(row[:17])
            labels.append(row[17])
    return (evidence, labels)
                


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    label_true = 0
    label_false = 0
    predict_true = 0
    predict_false = 0
    for i in range(len(labels)):
        if labels[i] == 1:
            label_true += 1
            if predictions[i] == 1:
                predict_true += 1
        elif labels[i] == 0:
            label_false += 1
            if predictions[i] == 0:
                predict_false += 1

    sensitivity = predict_true / label_true
    specificity = predict_false / label_false
    return (sensitivity, specificity)



if __name__ == "__main__":
    main()

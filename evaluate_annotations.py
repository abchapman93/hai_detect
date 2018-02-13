"""
This script takes as an argument the path to a directory which contains
saved human annotations in datadir/saved/Annotations.xlsx. It then applies `hai_detect`
to annotate the reports found in datadir/corpus.
"""
import os, sys
from annotations.Annotation import Annotation
from annotations.ClinicalTextDocument import  ClinicalTextDocument
from models.mention_level_models import MentionLevelModel
from openpyxl import load_workbook

def import_from_xlsx(corpus_dir, file_name):

    print(corpus_dir)
    assert os.path.exists(corpus_dir)
    print(file_name)
    wb = load_workbook(filename=file_name, read_only=False)
    ws=wb.active # just getting the first worksheet regardless of its name

    row = list(ws)[0]
    col_size = len(row)
    if (col_size != 11): #no more no less
        raise ValueError("MalformedHostExcelRow") #MalformedeHostExcelRow

    documents = dict()
    row_cnt = len(list(ws))
    print("{} rows".format(row_cnt))

    for i in range(1, row_cnt):
        #if i == 10:
        #    break
        row = list(ws)[i]
        full_file_name = row[1].value #second column
        full_file_path = os.path.join(corpus_dir, full_file_name)
        if not os.path.exists(full_file_path):
            continue

        anno = Annotation()
        anno.from_ehost_xlsx(row)
        doc = documents.setdefault(full_file_name,ClinicalTextDocument())
        doc.annotations['gold_standard'].append(anno)
        doc.filepath = full_file_name
        doc.rpt_id = os.path.splitext(os.path.basename(doc.filepath))[0]
        doc.processText(filepath=full_file_path, rpt_id=os.path.splitext(os.path.basename(doc.filepath))[0])


    return documents


def compute_metrics(comparisons, categories):
    """
    Takes a list of AnnotationComparison objects.
    For each class name in categories, computes
    the true and false counts of each.
    Returns a dictionary.
    """
    metrics = {}
    for cat in categories:
        metrics[cat] = {'true_count': 0,
                        'pred_count': 0,
                        'tp': 0,
                        'fp': 0,
                        'fn': 0,
                        'precision': 0,
                        'recall': 0,
                        'f1': 0}
    for c in comparisons:
        anno_type = c.annotation_type
        # If there is a gold annotation
        if c.has_a:
            metrics[anno_type]['true_count'] += 1
        # If there is a comparing annotation
        if c.has_b:
            metrics[anno_type]['pred_count'] += 1

        # If they are a correct match
        if c.is_match:
            metrics[anno_type]['tp'] += 1
        # If they're not, figure out what kind of error
        # If there's a gold but not system annotation -> false negative
        elif c.has_a and not c.has_b:
            metrics[anno_type]['fn'] += 1
        # If there's a system annotation but no gold -> false positive
        elif not c.has_a and c.has_b:
            metrics[anno_type]['fp'] += 1
        # If there's one of each, but it's not a match -> false negative
        elif c.has_a and c.has_b:
            metrics[anno_type]['fn'] += 1
       # if not c.is_match:
       #     print(c)
       #     print(c.has_a)
       #     print(c.has_b)
    # Now compute precision, recall, F1
    for cat in categories:
        try:
            p = metrics[cat]['tp']/metrics[cat]['pred_count']
        except ZeroDivisionError:
            p = 0
        try:
            r = metrics[cat]['tp']/metrics[cat]['true_count']
        except ZeroDivisionError:
            r = 0
        try:
            f1 = (2 * p * r)/(p + r)
        except ZeroDivisionError:
            f1 = 0
        metrics[cat]['precision'] = p
        metrics[cat]['recall'] = r
        metrics[cat]['f1'] = f1
    return metrics









def main():
    saved_annotations = os.path.join(datadir, rel_path)
    try:
        assert os.path.exists(saved_annotations)
    except AssertionError as e:
        print("Make sure {} exists".format(saved_annotations))
        exit()
    documents = import_from_xlsx(os.path.join(datadir, "corpus"), saved_annotations)
    print("{} Documents".format(len(documents)))

    targets = os.path.abspath('lexicon/targets.tsv')
    modifiers = os.path.abspath('lexicon/modifiers.tsv')
    model = MentionLevelModel(targets, modifiers)

    results = [] # This will contain a list of dicts with counts and results
    comparisons = [] # List of AnnotationComparisons
    # Specify which categories to look at
    categories = ['Evidence of SSI', 'Evidence of UTI', 'Evidence of Pneumonia']
    for name, document in documents.items():
        document.annotate(model)
        comparisons.extend(document.compare_annotations(categories=categories))
    metrics = compute_metrics(comparisons, categories)
    with open('test.txt', 'w') as f:
        f.write('\n\n'.join([str(c) for c in comparisons]))
    print(metrics); exit()
    for cat in categories:
        print(cat)
        out = "Recall: {recall}\nPrecision: {precision}\nF1: {f1}\nTrue Count: {true_count}\n Predicted Count: {pred_count}\n".format(**metrics[cat])
        out += "True Positives: {tp}\nFalse Positives: {fp}\nFalse Negatives: {fn}\n\n\n\n".format(**metrics[cat])
        with open('hai_results.txt', 'w') as f:
            f.write(out)
        print(out)

    matched = [c for c in comparisons if c.is_match]
    unmatched = [c for c in comparisons if not c.is_match]


    # Finally, save the comparisons
    joiner = '-' * 20 + '\n\n\n'
    with open('matched_annotations.txt', 'w') as f:
        f.write(joiner.join([str(c) for c in matched]))
    with open('unmatched_annotations.txt', 'w') as f:
        f.write(joiner.join([str(c) for c in unmatched]))
    print("Saved results")

    exit()




if __name__ == '__main__':
    datadir = sys.argv[1] # Folder contianing /corpus/, /saved/,
    rel_path = sys.argv[2] # path from datadir to Excel file
    main()

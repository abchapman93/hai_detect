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

def import_from_xlsx(file_name):

    corpus_dir = os.path.abspath(os.path.join(file_name, '..', '..', 'corpus'))
    print(corpus_dir)
    assert os.path.exists(corpus_dir)
    wb = load_workbook(filename=file_name, read_only=False)
    ws=wb.active # just getting the first worksheet regardless of its name

    row = list(ws)[0]
    col_size = len(row)
    if (col_size != 11): #no more no less
        raise MalformedeHostExcelRow

    documents = dict()
    row_cnt = len(list(ws))

    for i in range(1, row_cnt):
        row = list(ws)[i]
        full_file_name = row[1].value #second column
        full_file_path = os.path.join(corpus_dir, full_file_name)

        anno = Annotation()
        anno.from_ehost_xlsx(row)
        doc = documents.setdefault(full_file_name,ClinicalTextDocument())
        doc.annotations['gold_standard'].append(anno)
        doc.filepath = full_file_name
        doc.rpt_id = os.path.splitext(os.path.basename(doc.filepath))[0]
        doc.processText(filepath=full_file_path, rpt_id=os.path.splitext(os.path.basename(doc.filepath))[0])


    return documents


def main():
    saved_annotations = os.path.join(datadir, 'saved', 'Annotations.xlsx')
    assert os.path.exists(saved_annotations)
    documents = import_from_xlsx(saved_annotations)

    targets = os.path.abspath('lexicon/targets.tsv')
    modifiers = os.path.abspath('lexicon/modifiers.tsv')
    model = MentionLevelModel(targets, modifiers)

    results = [] # This will contain a list of dicts with counts and results
    categories = ['Evidence of SSI', 'Evidence of UTI', 'Evidence of Pneumonia']
    for name, document in documents.items():
        document.annotate(model)
        results.append(document.compare_annotations(categories=categories))

    # Now iterate through results and compute final results
    aggr_results = {}
    for r in results:
        print(r)
        for annotation_type in r.keys():
            if annotation_type not in aggr_results:
                aggr_results[annotation_type] = r[annotation_type]
            else:
                for metr, num in r[annotation_type].items():
                    aggr_results[annotation_type][metr] += num

    print(aggr_results.keys())
    print(aggr_results.items())


    metrics = {}
    for annotation_type, nums in aggr_results.items():
        print(annotation_type, nums)
        metrics[annotation_type] = {'precision': 0, 'recall': 0}

        try:
            metrics[annotation_type]['precision'] = nums['tp']/nums['pred_count']
        except ZeroDivisionError as e:
            metrics[annotation_type]['precision'] = 0
            #raise e
        try:
            metrics[annotation_type]['recall'] = nums['tp']/nums['count']
        except ZeroDivisionError:
            metrics[annotation_type]['recall'] = 0


    print(metrics)






if __name__ == '__main__':
    datadir = sys.argv[1]
    main()

"""
This script offers a simple demo of how to run hai_detect on all files found in `corpus_dir`.
Usage: python main.py /path/to/batch/folder
It will read in all .txt files found in /folder/corpus
and will save annotations in /folder/hai_detect
"""
import glob, os
import argparse



from annotations.Annotation import Annotation
from annotations.ClinicalTextDocument import ClinicalTextDocument
from models.mention_level_models import MentionLevelModel
from hai_exceptions.exceptions import MalformedeHostExcelRow, MalformedSpanValue



def main():
    print(args.datadir)
    assert os.path.exists(args.datadir)
    # This is the folder that will contain all saved annotations from hai_detect
    outdir = os.path.join(args.datadir, 'hai_detect')
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    reports = glob.glob(os.path.join(args.datadir, 'corpus', '*.txt'))

    # Create a model that we will use
    # This is defined in models.mention_level_models.py
    # All it requires is the filepaths to the targets and modifiers
    # With either https:// or file://
    targets = os.path.abspath('lexicon/targets.tsv')
    modifiers = os.path.abspath('lexicon/modifiers.tsv')
    #targets = 'https://raw.githubusercontent.com/abchapman93/hai_detect/master/lexicon/targets.tsv'
    #modifiers = 'https://raw.githubusercontent.com/abchapman93/hai_detect/master/lexicon/modifiers.tsv'
    model = MentionLevelModel(targets, modifiers)

    # Now iterate through each report and annotate using `model`
    # Save findings in `outdir`
    for i, report in enumerate(reports):
        if i % 10 == 0:
            print("{}/{}".format(i, len(reports)))
        document = ClinicalTextDocument(filepath=report)
        document.annotate(model)
        for annotation in document.get_annotations():
            print(annotation)
            print()
        document.to_knowtator(outdir)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('datadir', help="the directory containing subdirectories 'corpus' and 'saved'")
    args = parser.parse_args()
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
from optparse import OptionParser

from krnnt.keras_models import BEST
from krnnt.new import results_to_plain, results_to_xces, results_to_conll, results_to_conllu, \
    Lemmatisation, Lemmatisation2, get_morfeusz, analyze_tokenized, results_to_jsonl
from krnnt.readers import read_xces, read_jsonl
from krnnt.pipeline import KRNNTSingle

usage = """%prog MODEL LEMMATISATION_MODEL DICTIONARY < CORPUS_PATH



E.g. %prog
"""

if __name__ == '__main__':
    parser = OptionParser(usage=usage)
    parser.add_option('-p', '--preanalyzed', action='store_false',
                      default=True, dest='reanalyzed',
                      help='training data have not been reanalyzed')
    parser.add_option('-i', '--input-format', action='store',
                      default='xces', dest='input_format',
                      help='input format of preanalyzed data: xces, jsonl')
    parser.add_option('-o', '--output-format', action='store',
                      default='xces', dest='output_format',
                      help='output format: xces, plain, conll, conllu')
    parser.add_option('--maca_config', action='store',
                      default='morfeusz-nkjp-official', dest='maca_config',
                      help='Maca config')
    parser.add_option('--toki_config_path', action='store',
                      default='', dest='toki_config_path',
                      help='Toki config path (directory)')
    parser.add_option('--lemmatisation', action='store',
                      default='sgjp', dest='lemmatisation',
                      help='lemmatization mode (sgjp, simple)')
    parser.add_option('-g', '--debug', action='store_true', dest='debug_mode')  # TODO
    parser.add_option('--tokenized', action='store_true',
                      dest='tokenized',
                      help='input data are tokenized, but not analyzed')
    (options, args) = parser.parse_args()

    pref = {'keras_batch_size': 32, 'internal_neurons': 256, 'feature_name': 'tags4e3', 'label_name': 'label',
            'keras_model_class': BEST, 'maca_config':options.maca_config, 'toki_config_path':options.toki_config_path}

    if len(args) != 3:
        print('Provide paths to weights, lemmatisation data and dictionary.')
        sys.exit(1)

    if options.lemmatisation=='simple':
        pref['lemmatisation_class'] = Lemmatisation2
    else:
        pref['lemmatisation_class'] = Lemmatisation

    pref['reanalyze'] = options.reanalyzed
    # pref['input_format'] = options.input_format
    pref['output_format'] = options.output_format

    pref['weight_path'] = args[0]
    pref['lemmatisation_path'] = args[1]
    pref['UniqueFeaturesValues'] = args[2]

    krnnt = KRNNTSingle(pref)


    if options.tokenized:
        if options.input_format == 'jsonl':
            corpus = read_jsonl(sys.stdin)
        else:
            print('Wrong input format.')
            sys.exit(1)

        morf=get_morfeusz()
        corpus = analyze_tokenized(morf, corpus)
        results = krnnt.tag_sentences(corpus, preana=True)
    elif options.reanalyzed:
        results = krnnt.tag_sentences(sys.stdin.read().split('\n\n')) # ['Ala ma kota.', 'Ale nie ma psa.']
    else:
        #f = io.StringIO(sys.stdin.read())
        if options.input_format=='xces':
            corpus = read_xces(sys.stdin)
        elif options.input_format=='jsonl':
            corpus = read_jsonl(sys.stdin)
        else:
            print('Wrong input format.')
            sys.exit(1)

        results = krnnt.tag_sentences(corpus, preana=True)

    #print(results)

    if options.output_format == 'xces':
        conversion = results_to_xces
    elif options.output_format == 'plain':
        conversion = results_to_plain
    elif options.output_format == 'conll':
        conversion = results_to_conll
    elif options.output_format == 'conllu':
        conversion = results_to_conllu
    elif options.output_format == 'jsonl':
        conversion = results_to_jsonl
    else:
        print('Wrong output format.')
        sys.exit(1)

    conversion(results)

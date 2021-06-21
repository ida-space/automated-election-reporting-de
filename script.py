from wahlbot.Page import Page
from wahlbot.BackgroundInfo import BackgroundInfo
from wahlbot.Template import load_yaml
from wahlbot.Template import Template
from wahlbot.validity import validity_check
import wahlbot.results as results
from typing import List
import pandas as pd
import argparse
import sys
import os
import logging

pd.set_option('mode.chained_assignment', None)


def main(init: bool):

    # skip consituencies if needed
    blacklist: List = []

    res_path = os.getenv('RES_PATH', '/results/')
    os.makedirs(res_path, exist_ok=True)

    logger.info('script.py started')
    logger.info('Option: init: {}'.format(init))

    logger.info('load data')

    # Simulated data at different states
    data = pd.read_csv('./data/sample/counting.csv', sep=',', encoding='utf8')
    #data = pd.read_csv('./data/sample/final.csv', sep=',', encoding='latin')

    # Load column names
    cfg = load_yaml('./cfg.yaml')

    background_info = BackgroundInfo()

    # STATE RESULTS
    logger.info('Compute State Results')

    state_data = data[data[cfg['CONSTITUENCY']] == cfg['STATE']]

    # if no state results are present stop the script
    if state_data[cfg['PERCENT']].isnull().all():
        logger.error('State data is empty - constituency script is stopped!')
        sys.exit()
    state_parameter = results.get_state_results(state_data, prefix='state_')

    # PROGRESS
    logger.info('Load previous progress')
    progress_path = './data/progress.csv'
    try:
        progress_df = pd.read_csv(progress_path, index_col=0)
        prev_progress = progress_df.squeeze().to_dict()
    except FileNotFoundError:
        prev_progress = {elem: 0 for elem in data[cfg['CONSTITUENCY']].unique()}

    target = data.groupby(cfg['CONSTITUENCY']).first()[cfg['NUMBER_OF_DISTRICTS']]
    progress = data.groupby(cfg['CONSTITUENCY']).first()[cfg['DISTRICTS_COUNTED']]
    progress = progress.fillna(0).astype(int)

    # count status for logging
    counts = {'preelection': 0, 'counting': 0, 'final': 0, 'skipped': 0, 'no_data': 0}

    # GENERATE ARTICLES FOR EACH CONSTITUENCY
    for constituency in data[cfg['CONSTITUENCY']].unique():

        # skip election results on federal level
        if constituency == cfg['STATE'] or constituency in blacklist:
            continue

        logger.info(constituency)
        data_constituency = data[data[cfg['CONSTITUENCY']] == constituency]

        if data_constituency[cfg['PERCENT']].isnull().all():
            counts['no_data'] = counts['no_data'] + 1
            logger.info('data is empty - skip processing\n')
            continue

        # DETERMINE STATUS
        if init:
            status = 'preelection'
            progress[constituency] = 0
            counts[status] = counts[status] + 1
            logger.info('status: {}'.format(status))
            logger.info('progress: {}/{} ({})'.format(progress[constituency],
                                                      target[constituency],
                                                      prev_progress[constituency]))
        else:
            count_status = data_constituency[cfg['STATUS']].values[0]
            if count_status == 'Vorläufiges Ergebnis':
                status = 'final'
                progress[constituency] = 100
            else:
                status = 'counting'
            counts[status] = counts[status] + 1
            logger.info('status: {}'.format(status))
            logger.info('progress: {}/{} ({})'.format(progress[constituency],
                                                      target[constituency],
                                                      prev_progress[constituency]))

            # skip next steps if article in this state is already published
            if prev_progress[constituency] == progress[constituency]:
                counts['skipped'] = counts['skipped'] + 1
                logger.info('skip: article is already published\n')
                continue

        # PROCESSING
        logger.info('Processing...')
        page = Page(constituency, data_constituency, background_info, 'constituency')
        page.add_state_parameter(state_parameter)
        page.update_parameter(vote_type='listShare', prefix='list_')
        page.update_parameter(vote_type='directShare', prefix='direct_')
        page.update_candidate_results(background_info)
        page.assessment(level='constituency', prefix='list_', status=status)
        page.format_parameter()

        text_module_path = './templates/text_modules/{}.yaml'.format(status)
        path = './templates/article.txt'
        if status == 'preelection':
            path = './templates/preelection.txt'
        template = Template().load_page(path)
        template = template.safe_substitute({})

        xml_article = page.write(text_module_path, template)

        validity = validity_check(constituency, page.page_parameter)
        if validity == 'critical':
            logger.error('validity check not passed - article is not updated\n')
            continue

        # WRITE ARTICLE
        logger.info('save article\n')
        with open(res_path + constituency + '.txt', 'w') as writer:
            writer.write(xml_article)

    logger.info('Overview: {}'.format(counts))

    # STORE PROGRESS
    pd.DataFrame(progress).to_csv(progress_path)

    logger.info('script.py finished')


if __name__ == '__main__':

    # PARSE ARGUMENTS
    parser = argparse.ArgumentParser()

    parser.add_argument("--dry", "-d", action='store_true', help="dry run")
    parser.add_argument("--init", "-i", action='store_true', help="initialize articles")

    args = parser.parse_args()

    # SETUP LOGGING
    logger = logging.getLogger('wahlbot')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # START SCRIPT
    main(init=args.init)

import argparse
import os

import handler
import parser
import utils


class KeywordType:
    AND = '+'
    OR = '|'

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--venues', type=str, required=True, help='Avenue names')
arg_parser.add_argument('--keywords', type=str, help='Keywords list')
args = arg_parser.parse_args()

venues = handler.yaml_load('venue.yaml')
venues = {venue.upper(): link for venue, link in venues.items()}

if KeywordType.AND in args.keywords:
    keywords = args.keywords.split(KeywordType.AND)
    keyword_type = KeywordType.AND
else:
    keywords = args.keywords.split(KeywordType.OR)
    keyword_type = KeywordType.OR
keywords = list(map(lambda x: x.lower(), keywords))


for venue in args.venues.split('+'):
    link = venues[venue.upper()]
    venue_type, venue_name, _ = parser.parse_link(link)

    venue_dir = os.path.join(utils.root_dir, f'{venue_type}-{venue_name}')
    meta_parse_path = os.path.join(venue_dir, '.meta.parse.yaml')
    meta_parse = handler.yaml_load(meta_parse_path)

    print('\n' * 3)
    print('Venue:', venue)
    print()

    for page_link in meta_parse:

        selected_papers = []

        if not meta_parse[page_link]:
            continue

        venue_type, venue_name, page_name = parser.parse_link(page_link)
        page_yaml = os.path.join(utils.root_dir, f'{venue_type}-{venue_name}', page_name + '.yaml')
        tracks: dict = handler.yaml_load(page_yaml)

        print('Page:', page_name)

        for track, papers in tracks.items():
            for paper in papers:
                title = paper['title'].lower()

                if keyword_type == KeywordType.AND:
                    if all(keyword in title for keyword in keywords):
                        selected_papers.append(paper)
                else:
                    if any(keyword in title for keyword in keywords):
                        selected_papers.append(paper)

        for paper in selected_papers:
            print(paper['title'])
            print('Authors:', ', '.join([author['name'] for author in paper['authors']]))
            print()

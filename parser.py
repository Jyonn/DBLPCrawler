from argparse import ArgumentParser

import handler


def parse(soup):
    tracks = {}
    current_track = "Default"

    # Traverse through all elements under id="main"
    main_content = soup.find(id='main')
    if not main_content:
        return {}

    for child in main_content.children:
        if child.name == 'header' and child.get('class') == ['h2']:
            # New track starts here
            track_name = child.find('h2').get_text(strip=True)
            current_track = track_name
        elif child.name == 'ul' and 'publ-list' in (child.get('class') or []):
            for li in child.find_all('li'):
                cite = li.find('cite')
                if cite:
                    # Extract author and title information
                    title = cite.find_all('span', itemprop='name')[-1].get_text(strip=True)
                    authors = extract_authors(cite)
                    if current_track not in tracks:
                        tracks[current_track] = []
                    tracks[current_track].append({
                        'title': title,
                        'authors': authors,
                    })

    return tracks


def extract_authors(cite):
    authors = []
    author_elements = cite.find_all('span', itemprop='author')
    for author_element in author_elements:
        author_name = author_element.find('span', itemprop='name').get_text(strip=True)
        author_link = author_element.find('a', itemprop='url')['href'] \
            if author_element.find('a', itemprop='url') else None
        author_pid = extract_pid(author_link)
        authors.append({
            'name': author_name,
            'pid': author_pid,
        })
    return authors


def extract_pid(author_link):
    if author_link:
        pid_parts = author_link.split('/pid/')[1].split('.html')[0].split('/')
        return f'{pid_parts[0]}-{pid_parts[1]}'
    else:
        return None  # If no PID is found, return None


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--filepath', '-f', type=str, required=True)
    args = parser.parse_args()

    tracks = parse(handler.file_read(args.filepath))
    for track, papers in tracks.items():
        print(track)
        for paper in papers:
            print(f"  Title: {paper['title']}")
            print(f"  Authors: {', '.join([author['name'] for author in paper['authors']])}")
            print()

'''Adds summary and descriptions to One Pace on a Plex Server.'''
from plexapi.server import PlexServer
from dotenv import load_dotenv
import requests
import os
# Load plex host & token
load_dotenv()

res = requests.get('https://api.onepace.net//list_progress_episodes.php').json()

arcs = [
    {
        **arc,
        'anime_episodes': arc['episodes'],
        'episodes': [e for e in res['episodes'] if e['arc_id'] == arc['id']]
    } for arc in res['arcs']
]


PLEX_HOST = os.environ['PLEX_HOST']
PLEX_TOKEN = os.environ['PLEX_TOKEN']
plex = PlexServer(PLEX_HOST, PLEX_TOKEN)

one_pace = plex.library.section('Anime').get(title='One Pace')
seasons = one_pace.seasons()

for i, arc in enumerate(arcs):
    try:
        season = list(filter(lambda s: s.index == i, seasons))[0]
    except IndexError:
        print(f'Season {i} is not in Plex')
        continue

    season.edit(**{
        'title.value': arc['title'],
        'summary.value': (
            f'Chapters: {arc["chapters"]}\n'
            f'Episodes: {arc["anime_episodes"]}'
        )
    })
    if not season.posters():
        season.uploadPoster(
            url=f'https://onepace.net/assets/arc_{arc["id"]}.png')
        season.setPoster(season.posters()[-1])

    for plex_episode in season.episodes():
        episode = [
            e for e in arc['episodes'] if e['part'] == plex_episode.index][0]

        plex_episode.edit(**{
            'title.value': (
                episode['title'] if episode['title'] else '%s %02d' % (
                    arc['title'], episode['part']
                )
            ),
            'summary.value': (
                f'Chapters: {episode["chapters"]}\n'
                f'Episodes: {episode["episodes"]}'
            ),
        })

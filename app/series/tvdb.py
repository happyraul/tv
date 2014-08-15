import requests
import os
import datetime
import decimal
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from flask import current_app
from .. import models, db
import zipfile

DATA_DIR = '/home/raul/source/tv/shows/data/'
IMAGE_DIR = '/home/raul/source/tv/shows/static/img/'


class TvParser():
    @staticmethod
    def get_field(dom, field):
        return unicode(dom.getElementsByTagName(field)[0].firstChild.data)

    @staticmethod
    def get_optional_field(dom, field):
        field_list = dom.getElementsByTagName(field)
        if len(field_list) > 0 and field_list[0].hasChildNodes():
            return unicode(field_list[0].firstChild.data)
        else:
            return ""


class TvSeries():

    @staticmethod
    def get_id(series_dom):
        return int(TvParser.get_field(series_dom, 'id'))

    @staticmethod
    def get_seriesid(series_dom):
        return TvParser.get_field(series_dom, 'seriesid')

    @staticmethod
    def get_name(series_dom):
        return TvParser.get_field(series_dom, 'SeriesName')

    @staticmethod
    def get_status(series_dom):
        status = TvParser.get_optional_field(series_dom, 'Status')
        if status:
            return models.STATUSES[status]
        else:
            return None

    @staticmethod
    def get_air_day(series_dom):
        day = TvParser.get_optional_field(series_dom, 'Airs_DayOfWeek')
        if day:
            try:
                return models.DAYS_OF_WEEK[day.capitalize()]
            except KeyError:
                return None
        else:
            return None

    @staticmethod
    def get_air_time(series_dom):
        time = TvParser.get_optional_field(series_dom, 'Airs_Time')
        if time:
            current_app.logger.debug("Time: %s" % time)
            try:
                date = datetime.datetime.strptime(time, "%I:%M %p")
                return date.time()
            except ValueError:
                pass
            #if not date:
            try:
                date = datetime.datetime.strptime(time, "%I:%M%p")
                return date.time()
            except ValueError:
                pass
            #if not date:
            try:
                date = datetime.datetime.strptime(time, "%H.%M")
                return date.time()
            except ValueError:
                pass
            try:
                date = datetime.datetime.strptime(time, "%H:%M")
                return date.time()
            except ValueError:
                pass
            return None
        else:
            return None

    @staticmethod
    def get_banner(series_dom):
        return TvParser.get_optional_field(series_dom, 'banner')

    @staticmethod
    def get_fanart(series_dom):
        return TvParser.get_optional_field(series_dom, 'fanart')

    @staticmethod
    def get_poster(series_dom):
        return TvParser.get_optional_field(series_dom, 'poster')

    @staticmethod
    def get_overview(series_dom):
        return TvParser.get_optional_field(series_dom, 'Overview')[:1000]

    @staticmethod
    def get_first_aired(series_dom):
        date_string = TvParser.get_optional_field(series_dom, 'FirstAired')
        if date_string:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
            return date.date()
        else:
            return None

    @staticmethod
    def get_network(series_dom):
        return TvParser.get_optional_field(series_dom, 'Network')

    @staticmethod
    def get_rating(series_dom):
        rating = TvParser.get_optional_field(series_dom, 'Rating')
        if rating:
            return decimal.Decimal(rating)
        else:
            return None

    @staticmethod
    def get_rating_count(series_dom):
        return int(TvParser.get_optional_field(series_dom, 'RatingCount'))

    @staticmethod
    def get_runtime(series_dom):
        return int(TvParser.get_optional_field(series_dom, 'Runtime'))

    @staticmethod
    def get_last_updated(series_dom):
        return TvParser.get_field(series_dom, 'lastupdated')

    @staticmethod
    def get_base_series(series_id):

        series = models.Series.query.get(int(series_id))
        one_day = datetime.timedelta(days=1)
        now = datetime.datetime.utcnow()

        # Check how old our data is
        if series is None or series.last_updated < now - one_day:
            # Need to fetch a new series record because we don't have it in our
            # database, or it is stale
            current_app.logger.debug("Fetching series and episodes from tvdb.")
            #app.logger.debug(series)
            #app.logger.debug(series.last_updated)
            #app.logger.debug(now - one_day)
            API_KEY = '70E022FEB8032C20'
            SEARCH_URL = 'http://www.thetvdb.com/api/%s/series/%s/all/en.zip'
            ZIP_FILE_PATH = '%s%s/%s.zip' % (DATA_DIR, series_id, series_id)
            XML_FILE_PATH = '%s%s/en.xml' % (DATA_DIR, series_id)

            url = SEARCH_URL % (API_KEY, series_id)
            r = requests.get(url)
            r.raise_for_status()

            # create directory for this series data
            if not os.path.exists(DATA_DIR + str(series_id)):
                os.makedirs(DATA_DIR + str(series_id))

            with open(ZIP_FILE_PATH, "wb") as series_zip:
                series_zip.write(r.content)

            # unzip the data file
            with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as series_zip:
                series_zip.extractall(DATA_DIR + str(series_id))

            try:
                dom = minidom.parse(XML_FILE_PATH)
            except ExpatError:
                return {'response': False}

            series_dom = dom.getElementsByTagName("Series")[0]
            episode_doms = [episode for episode in
                            dom.getElementsByTagName("Episode") if
                            int(TvEpisode.get_season(episode)) > 0]

            # save the series banner
            banner_url = ("http://www.thetvdb.com/banners/%s" %
                          TvSeries.get_banner(series_dom))
            banner_dir = (IMAGE_DIR + '%s/' % series_id) + 'series/'
            TvBanner.save_image(banner_url, banner_dir)

            new_series = models.Series(
                id=TvSeries.get_id(series_dom),
                air_day=TvSeries.get_air_day(series_dom),
                air_time=TvSeries.get_air_time(series_dom),
                first_aired=TvSeries.get_first_aired(series_dom),
                network=TvSeries.get_network(series_dom),
                overview=TvSeries.get_overview(series_dom),
                rating=TvSeries.get_rating(series_dom),
                rating_count=TvSeries.get_rating_count(series_dom),
                runtime=TvSeries.get_runtime(series_dom),
                name=TvSeries.get_name(series_dom),
                status=TvSeries.get_status(series_dom),
                last_updated=datetime.datetime.utcnow())

            if series is None:
                db.session.add(new_series)
                for episode in episode_doms:
                    banner_url = ("http://www.thetvdb.com/banners/%s" %
                                  TvEpisode.get_banner(episode))
                    banner_dir = (IMAGE_DIR + '%s/%s/' %
                                 (series_id, TvEpisode.get_id(episode)))
                    current_app.logger.debug("Saving episode image: %s" %
                                             banner_url)
                    TvBanner.save_image(banner_url, banner_dir)
                    db.session.add(models.Episode(
                        id=TvEpisode.get_id(episode),
                        series_id=TvSeries.get_id(series_dom),
                        season=TvEpisode.get_season(episode),
                        episode_number=TvEpisode.get_episode_number(episode),
                        name=TvEpisode.get_name(episode),
                        overview=TvEpisode.get_overview(episode),
                        rating=TvEpisode.get_rating(episode),
                        rating_count=TvEpisode.get_rating_count(episode),
                        air_date=TvEpisode.get_air_date(episode)))
            else:
                db.session.merge(new_series)
                for episode in episode_doms:
                    banner_url = ("http://www.thetvdb.com/banners/%s" %
                                  TvEpisode.get_banner(episode))
                    banner_dir = (IMAGE_DIR + '%s/%s/' %
                                 (series_id, TvEpisode.get_id(episode)))
                    current_app.logger.debug("Saving episode image: %s" %
                                             banner_url)
                    TvBanner.save_image(banner_url, banner_dir)
                    db.session.merge(models.Episode(
                        id=TvEpisode.get_id(episode),
                        series_id=TvSeries.get_id(series_dom),
                        season=TvEpisode.get_season(episode),
                        episode_number=TvEpisode.get_episode_number(episode),
                        name=TvEpisode.get_name(episode),
                        overview=TvEpisode.get_overview(episode),
                        rating=TvEpisode.get_rating(episode),
                        rating_count=TvEpisode.get_rating_count(episode),
                        air_date=TvEpisode.get_air_date(episode)))

            db.session.commit()
        series = models.Series.query.get(series_id)

        return {'series': series,
                'episodes': [e for e in series.episodes if
                             e.air_date is not None],
                'response': True}

    @staticmethod
    def search_by_name(search_series):
        series_list = []
        SEARCH_URL = u'http://www.thetvdb.com/api/GetSeries.php?seriesname=%s'

        url = SEARCH_URL % search_series
        try:
            dom = minidom.parseString(requests.get(url).content)
        except ExpatError:
            return {'response': False}

        results_list = [series for series in
                        dom.getElementsByTagName("Series")]

        if results_list:
            for series in results_list:
                series_list.append({'id': TvSeries.get_seriesid(series),
                                    'name': TvSeries.get_name(series),
                                    'banner': TvSeries.get_banner(series),
                                    'overview': TvSeries.get_overview(series),
                                    'first_aired': TvSeries
                                    .get_first_aired(series)})

            return {'response': True, 'series_list': series_list}
        else:
            return {'response': False, 'series_list': []}


class TvEpisode():

    @staticmethod
    def get_id(episode_dom):
        return int(TvParser.get_field(episode_dom, 'id'))

    @staticmethod
    def get_season(episode_dom):
        return int(TvParser.get_field(episode_dom, 'SeasonNumber'))

    @staticmethod
    def get_episode_number(episode_dom):
        return int(TvParser.get_field(episode_dom, 'EpisodeNumber'))

    @staticmethod
    def get_name(episode_dom):
        return TvParser.get_optional_field(episode_dom, 'EpisodeName')

    @staticmethod
    def get_overview(episode_dom):
        return TvParser.get_optional_field(episode_dom, 'Overview')[:1000]

    @staticmethod
    def get_rating(episode_dom):
        rating = TvParser.get_optional_field(episode_dom, 'Rating')
        if rating:
            return decimal.Decimal(rating)
        else:
            return None

    @staticmethod
    def get_rating_count(episode_dom):
        return int(TvParser.get_field(episode_dom, 'RatingCount'))

    @staticmethod
    def get_last_updated(episode_dom):
        return TvParser.get_field(episode_dom, 'lastupdated')

    @staticmethod
    def get_air_date(episode_dom):
        date_string = TvParser.get_optional_field(episode_dom, 'FirstAired')
        if date_string:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
            return date.date()
        else:
            return None

    @staticmethod
    def get_banner(episode_dom):
        # app.logger.debug("Returning image: %s" %
        #                 TvParser.get_optional_field(episode_dom, 'filename'))
        return TvParser.get_optional_field(episode_dom, 'filename')


class TvBanner():

    @staticmethod
    def get_banner_url(banner_dom):
        return TvParser.get_field(banner_dom, 'BannerPath')

    @staticmethod
    def get_banner_type(banner_dom):
        return TvParser.get_field(banner_dom, 'BannerType')

    @staticmethod
    def get_language(banner_dom):
        return TvParser.get_optional_field(banner_dom, 'Language')

    @staticmethod
    def delete_image(user_id, series_id, type, file):
        path = (IMAGE_DIR + '%s/%s/' % ("user-" + user_id, series_id)) +\
            type + '/' + file
        if os.path.exists(path):
            current_app.logger.debug("Deleting image: %s" % path)
            os.remove(path)

    @staticmethod
    def save_image(url, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

        path = dir + os.path.basename(url)

        if not os.path.exists(path):
            current_app.logger.debug("Saving banner: %s" % url)

            r = requests.get(url)
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)

        else:
            current_app.logger.debug("Banner: " + path + " already saved.")

    @staticmethod
    def download_images(series_id):
        XML_FILE_PATH = DATA_DIR + '%s/banners.xml'

        if not os.path.exists(XML_FILE_PATH % series_id):
            TvSeries.get_base_series(series_id)

        try:
            dom = minidom.parse(XML_FILE_PATH % series_id)
        except ExpatError:
            return {'response': False}

        banners = dom.getElementsByTagName("Banner")

        for banner in banners:
            if TvBanner.get_language(banner) == "en":
                url = ("http://www.thetvdb.com/banners/%s" %
                       TvBanner.get_banner_url(banner))
                type = TvBanner.get_banner_type(banner)
                dir = (IMAGE_DIR + '%s/' % series_id) + type + '/'

                TvBanner.save_image(url, dir)

from flask import flash, redirect, url_for, request, render_template,\
    current_app
from flask.ext.login import login_required, current_user
from ..models import STATUSES, DAYS_OF_WEEK
from tvdb import TvSeries
from . import series
import operator


@series.route('/result')
@login_required
def result():
    if current_user is None:
        flash('Must be logged in to see this page.')
        return redirect(url_for('auth.login'))
    search_series = request.args.get('seriesname').strip()
    if len(search_series) < 1 or \
            search_series == "Enter all or part of a series name":
        flash('You did not enter a search term.')
        return redirect(url_for('main.user'))
    else:
        response = TvSeries.search_by_name(search_series)
        if response['response']:
            results_list = response['series_list']
            if len(results_list) == 1:
                return redirect(url_for('series.detail',
                                series_id=results_list[0]['id']))
            else:
                return render_template('series/result.html',
                                       search_series=search_series,
                                       series_list=results_list,
                                       title='Results',
                                       user=current_user)
        else:
            flash('Your search term "%s" did not yield any results.' %
                  search_series)
            return redirect(url_for('main.user'))


@series.route('/detail/<int:series_id>')
@login_required
def detail(series_id):
    base_series = TvSeries.get_series(series_id,
                                      current_app.config['TVDB_API_KEY'])
    if base_series['response']:
        for e in base_series['episodes']:
            if e.air_date is None:
                current_app.logger.debug(str(e.id) + " has no air date.")
        episodes = sorted(base_series['episodes'],
                          key=operator.attrgetter("air_date"))
        return render_template('series/detail.html',
                               series=base_series['series'],
                               episodes=episodes, title='Detail',
                               user=current_user, statuses=STATUSES,
                               days=DAYS_OF_WEEK,)
    else:
        flash("Series detail not found.")
        return redirect(url_for('user'))

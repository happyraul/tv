from flask import current_app, flash, redirect, url_for, request,\
    render_template
from flask.ext.login import login_required, current_user
from tvdb import TvSeries
from . import series


@series.route('/result')
@login_required
def result():
    current_app.logger.debug('reached search page')
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
                return redirect(url_for('detail',
                                series_id=results_list[0]['id']))
            else:
                return render_template('result.html',
                                       search_series=search_series,
                                       series_list=results_list,
                                       title='Results',
                                       user=current_user)
        else:
            flash('Your search term "%s" did not yield any results.' %
                  search_series)
            return redirect(url_for('main.user'))

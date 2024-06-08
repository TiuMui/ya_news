import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('many_news')
def test_news_count(client, url_calculation):
    url = url_calculation['news:home']
    response = client.get(url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('many_news')
def test_news_order(client, url_calculation):
    url = url_calculation['news:home']
    response = client.get(url)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('many_comments')
def test_comments_order(client, url_calculation):
    url = url_calculation['news:detail_news.id']
    response = client.get(url)
    assert 'news' in response.context
    news_from_context = response.context['news']
    all_comments = news_from_context.comment_set.all()
    all_timestamps = [_.created for _ in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, form_in_page',
    (
        (pytest.lazy_fixture('reader_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_form_for_different_users(
        url_calculation, parametrized_client, form_in_page
):
    url = url_calculation['news:detail_news.id']
    response = parametrized_client.get(url)
    context = response.context
    assert ('form' in context) is form_in_page
    assert (isinstance(context.get('form'), CommentForm)) is form_in_page

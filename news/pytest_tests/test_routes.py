from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

anonymous = pytest.lazy_fixture('client')
reader = pytest.lazy_fixture('reader_client')
author = pytest.lazy_fixture('author_client')
status_ok = HTTPStatus.OK
status_not_found = HTTPStatus.NOT_FOUND

@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_key, parametrized_client, status',
    (
        ('news:home', anonymous, status_ok),
        ('news:detail_news.id', anonymous, status_ok),
        ('users:login', anonymous, status_ok),
        ('users:logout', anonymous, status_ok),
        ('users:signup', anonymous, status_ok),
        ('news:edit_comment_id', reader, status_not_found),
        ('news:delete_comment_id', reader, status_not_found),
        ('news:edit_comment_id', author, status_ok),
        ('news:delete_comment_id', author, status_ok),
    )
)
def test_availability_pages(
        url_calculation, url_key, parametrized_client, status
):
    url = url_calculation[url_key]
    response = parametrized_client.get(url)
    assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_key',
    ('news:edit_comment_id', 'news:delete_comment_id')
)
def test_redirect_for_anonymous_client(client, url_calculation, url_key):
    login_url = url_calculation['users:login']
    url = url_calculation[url_key]
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)

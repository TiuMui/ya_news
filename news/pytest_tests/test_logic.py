from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

form_data = {'text': 'Текст комментария', }


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, url_calculation):
    before_count = Comment.objects.count()
    url = url_calculation['news:detail_news.id']
    response = client.post(url, data=form_data)
    login_url = url_calculation['users:login']
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    after_count = Comment.objects.count()
    assert before_count == after_count


def test_user_can_create_comment(reader_client, reader, url_calculation, news):
    Comment.objects.all().delete()
    before_count = Comment.objects.count()
    url = url_calculation['news:detail_news.id']
    response = reader_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    after_count = Comment.objects.count()
    assert before_count + 1 == after_count
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == reader
    assert new_comment.news == news


def test_user_cant_use_bad_words(reader_client, url_calculation):
    before_count = Comment.objects.count()
    bad_words_data = {'text': f'{choice(BAD_WORDS)}'}
    url = url_calculation['news:detail_news.id']
    response = reader_client.post(url, data=bad_words_data)
    after_count = Comment.objects.count()
    assert before_count == after_count
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


def test_author_can_delete_comment(
        author_client,
        url_calculation
):
    before_count = Comment.objects.count()
    news_url = url_calculation['news:detail_news.id']
    url_to_comments = news_url + '#comments'
    url = url_calculation['news:delete_comment_id']
    response = author_client.post(url)
    after_count = Comment.objects.count()
    assertRedirects(response, url_to_comments)
    assert before_count - 1 == after_count


def test_user_cant_delete_comment_of_another_user(
    reader_client,
    url_calculation
):
    before_count = Comment.objects.count()
    url = url_calculation['news:delete_comment_id']
    response = reader_client.post(url)
    after_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert before_count == after_count


def test_author_can_edit_comment(
        author,
        author_client,
        comment,
        url_calculation,
        news
):
    news_url = url_calculation['news:detail_news.id']
    url_to_comments = news_url + '#comments'
    url = url_calculation['news:edit_comment_id']
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_edit_comment_of_another_user(
        reader_client,
        comment,
        url_calculation,
        news,
        author
):
    true_text_comment = comment.text
    url = url_calculation['news:edit_comment_id']
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    from_db_comment = Comment.objects.get(id=comment.id)
    assert from_db_comment.text == true_text_comment
    assert from_db_comment.author == author
    assert from_db_comment.news == news

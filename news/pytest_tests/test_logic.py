from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, news_id_for_args, form_data
):
    url = reverse('news:detail', args=news_id_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        reader_client, reader, form_data, news_id_for_args
):
    url = reverse('news:detail', args=news_id_for_args)
    response = reader_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == reader


def test_user_cant_use_bad_words(reader_client, news_id_for_args):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=news_id_for_args)
    response = reader_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
        author_client,
        comment_id_for_args,
        news_id_for_args
):
    news_url = reverse('news:detail', args=news_id_for_args)
    url_to_comments = news_url + '#comments'
    url = reverse('news:delete', args=comment_id_for_args)
    response = author_client.post(url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    reader_client,
    comment_id_for_args
):
    url = reverse('news:delete', args=comment_id_for_args)
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        author_client,
        comment,
        comment_id_for_args,
        news_id_for_args,
        form_data
):
    news_url = reverse('news:detail', args=news_id_for_args)
    url_to_comments = news_url + '#comments'
    url = reverse('news:edit', args=comment_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        reader_client,
        comment,
        comment_id_for_args,
        form_data
):
    true_text_comment = comment.text
    url = reverse('news:edit', args=comment_id_for_args)
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    from_db_comment = Comment.objects.get(id=comment.id)
    assert true_text_comment == from_db_comment.text

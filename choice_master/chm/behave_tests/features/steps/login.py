"""
Implement log in steps
"""

from behave import when, then

URLS = {
    'login': 'http://localhost:8000/account/login/',
    'home': 'http://localhost:8000',
}

@when(u'I go to the "{page}" page')
def step_impl(context, page):
    context.browser.get(URLS[page])

@then(u'I am redirected to the "{page}" page')
def step_impl(context, page):
    msg = '{} != {}'.format(context.browser.current_url, URLS[page])
    assert context.browser.current_url == URLS[page], msg

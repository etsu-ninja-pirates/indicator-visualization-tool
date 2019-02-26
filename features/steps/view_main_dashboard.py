from behave import given, when, then
from features.framework.environment import cph_ivt_app


@given('I am on public user home page')
def step_implement(context):
	cph_ivt_app.load_website()

@when(u'I go to the "{page}" page')
def setp_implement(context, page):
	cph_ivt_app.goto_page(page)

# Verify the find a location is on the
# Main dashboard when a user first
# Accesses the CPH-IVT web application
@then(u'I see content "{component}"')
def setp_implement(context, component):
	cph_ivt_app.verify_component_exists(component)

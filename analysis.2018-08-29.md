# State of the Project

2018-08-29

## Organization

Directories:

- health_data_project - Django project configuration directory
- hda_public - Django "app" for publicly-accessible pages
- hda_privileged - Django "app" for pages requiring authentication (e.g. for uploading data)
- static - static assets e.g. css

## Working URLs

| URL | View | Template | Link |
|-----|------|----------|------|
| `/` | `hda_public.views.dashboard` | hda_public\dashboard.html | [link](http://localhost:8000/) |
| `priv/login` | `hda_privileged.views.user_login` | hda_privileged\login.html | [link](http://localhost:8000/priv/login) |
| `priv/metric` | `hda_privileged.views.manage_metrics` | hda_privileged\manage_metrics.html | [link](http://localhost:8000/priv/metric) |
| `priv/metric/create` | `hda_privileged.views.create_metric` | hda_privileged\create_metric.html | [link](http://localhost:8000/priv/metric/create) |
| `/admin/**` | Django's builtin admin interface | | [link](http://localhost:8000/admin/) |

## Interactivity

- login - works if user is created beforehand through admin interface, but logging in changes nothing
- admin - django's admin interface can be used to create users, if `python manage.py createsuperuser` has been used to add an admin

No other templates are interactive - HTML is _not_ generated from data e.g. for chart form or health metric pages. The pages for creating and managing metrics are mocked and do not process any form POST data.

## Data models

- ERD for data model exists
- _No model classes in project_
- Need way to populate static data like states and counties - was in progress at end of last semester

## Data processing

None to speak of.

## Theme/Styles

Current theme (adapted from 3rd party) is complicated and difficult to maintain. Buggy with our current modifications. Kim has found a simpler, easier theme over the summer, but it has not been integrated into the project yet.

Static asset directories likely contain many unused files.

## Misc. Issues

- UI of "manage metrics" includes controls for adding a new metric, while "create metric" provides an entire page for this.
- HTML for selecting data is not generated from a Django form and is included in the base template, making it difficult to decouple
- No URL or GET parameter scheme for specifying what data to display
- Need decision on what logic to put client-side vs server-side

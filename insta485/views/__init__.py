"""Views, one for each Insta485 page."""
from insta485.views.index import show_index, upload_file
from insta485.views.login import log_in_page, log_out_page
from insta485.views.users import user_page
from insta485.views.followers import followers_page
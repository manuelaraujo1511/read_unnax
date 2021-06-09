from __future__ import absolute_import

from celery import shared_task, states
from celery.utils.log import get_task_logger
from celery.exceptions import Ignore
import traceback
from .db_con import *
from .scraping import *

logger = get_task_logger(__name__)

@shared_task(bind=True, track_started=True)
def t_startProcess(self, username, password, code):
  msg_e = ''
  try:
    self.update_state(state='PROGRESS', meta={'code': code})
    sp = ScrapingUnnax(username, password)
    session  = sp.login_page()
    data_finaly = sp.get_all_data(session)
    return data_finaly
  except Exception as e:
    msg_e = str(e)
    # Save Exception into db task rabbitMQ
    self.update_state(
      state=states.FAILURE,
      meta={
        'exc_type': type(e).__name__,
        'exc_message': traceback.format_exc().split('\n'),
        'custom': msg_e
        }
      )
    logger.error(msg_e)
    raise Ignore()

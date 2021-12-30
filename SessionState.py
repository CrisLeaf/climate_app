"""
Hack to add per-session state to Streamlit.
"""
import streamlit.report_thread as ReportThread
from streamlit.server.server import Server


class SessionState(object):
	def __init__(self, **kwargs):
		for key, val in kwargs.items():
			setattr(self, key, val)

def get(**kwargs):
	ctx = ReportThread.get_report_ctx()
	this_session = None
	current_server = Server.get_current()
	session_infos = Server.get_current()._session_info_by_id.values()
	
	for session_info in session_infos:
		s = session_info.session
		if not hasattr(s, '_main_dg') and s._uploaded_file_mgr == ctx.uploaded_file_mgr:
			this_session = s
	
	if this_session is None:
		raise RuntimeError("Couldn't get your Streamlit Session object.")

	if not hasattr(this_session, '_custom_session_state'):
		this_session._custom_session_state = SessionState(**kwargs)
	
	return this_session._custom_session_state
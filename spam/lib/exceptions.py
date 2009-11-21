from tg.exceptions import HTTPClientError

class SPAMProjectNotFound(HTTPClientError):
    code = 400
    title = 'Project Not Found'
    explanation = ''



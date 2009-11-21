from tg.exceptions import HTTPClientError

class SPAMProjectNotFound(HTTPClientError):
    code = 400
    title = 'Project Not Found'
    explanation = ''


class SPAMRepoNotFound(HTTPClientError):
    code = 400
    title = 'Repository Not Found'
    explanation = ''



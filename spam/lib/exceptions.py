from tg.exceptions import HTTPClientError

class SPAMDBError(HTTPClientError):
    code = 400
    title = 'Database Error'
    explanation = ''


class SPAMDBNotFound(HTTPClientError):
    code = 400
    title = 'DB Element Not Found'
    explanation = ''


class SPAMRepoError(HTTPClientError):
    code = 400
    title = 'Repository Error'
    explanation = ''


class SPAMRepoNotFound(HTTPClientError):
    code = 400
    title = 'Repository Not Found'
    explanation = ''



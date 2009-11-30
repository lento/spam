from tg.exceptions import HTTPClientError

class SPAMError(HTTPClientError):
    code = 400
    title = 'SPAM Error'
    explanation = ''


class SPAMDBError(SPAMError):
    code = 400
    title = 'Database Error'
    explanation = ''


class SPAMDBNotFound(SPAMError):
    code = 400
    title = 'DB Element Not Found'
    explanation = ''


class SPAMRepoError(SPAMError):
    code = 400
    title = 'Repository Error'
    explanation = ''


class SPAMRepoNotFound(SPAMError):
    code = 400
    title = 'Repository Not Found'
    explanation = ''



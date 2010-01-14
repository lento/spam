<%inherit file="spam.templates.master"/>

<div class="content">
    <h1>${_('Journal')}</h1>
    ${_('page')}: ${c.paginators.journal.pager()}
    ${c.t_journal(id='journal', items=list(journal), curpage=c.paginators.journal.page) | n}
</div>


<%inherit file="spam.templates.master"/>

<div class="content">
    <a href="${tg.url('./new')}" rel="#overlay" class="overlay button">new category</a>
    <br/>
    <br/>
    <h1>${_('Categories')}</h1>
    ${c.t_categories(id='categories', items=list(categories)) | n}
</div>


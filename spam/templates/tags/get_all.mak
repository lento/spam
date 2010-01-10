<div class="tags">
    <a href="${tg.url('/tag/' % ())}"
       rel="#overlay" class="overlay button">add tag</a>
    ${c.l_tags(id="taglist", items=tags) | n}
</div>


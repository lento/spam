<div class="tags">
    <a href="${tg.url('/tag/' % ())}"
       rel="#overlay" class="overlay button">add tag</a>
    ${c.b_tags(id="taglist", items=tags) | n}
</div>


<div class="notes">
    <a href="${tg.url('/note/' % ())}"
       rel="#overlay" class="overlay button">add note</a>
    ${c.l_notes(id="taglist", items=notes) | n}
</div>


<div class="notes">
    <a href="${tg.url('/note/' % ())}"
       rel="#overlay" class="overlay button">add note</a>
    ${c.t_notes(id="taglist", items=notes, annotable_id=annotable_idf) | n}
</div>


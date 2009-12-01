<%inherit file="spam.templates.master"/>

<div id="tabbed_content_wrapper"> 
    <!-- the tabs --> 
    <ul class="tabs">
        % for name, dest in tabs:
            <li><a href="${dest}">${name}</a></li>
        % endfor
    </ul> 
     
    <!-- tab "panes" --> 
    <div class="content"> 
        <div class="pane ajax"></div> 
    </div>
</div>


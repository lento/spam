## the following line is just to have the file sintax-highlighted in gedit ;)
##<script type="text/javascript">

var upload = new Object;
upload.target = "${tg.url('/upload')}";

upload.queue = {length: 0, files: {},
                add_file: function(file) {
                    this.length += 1;
                    this.files[this.length] = file;
                    return this.length;
                },
                find: function(filename) {
                    var found = false;
                    $.each(this.files, function(key, file) {
                        if (file.name == filename)
                            found = true;
                    });
                    return found;
                }
               };

upload.file_read = function(queue_id, file) {
    var reader = new FileReader();
    reader.onloadend = function(e) {
        upload.file_upload(queue_id, e.target.result);
    };
    reader.readAsBinaryString(file);
}

upload.handle_files = function(files) {
    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        
        if (!upload.queue.find(file.name)) {
            var n = upload.queue.add_file(file);
            var filediv = $('<div class="queue_item">' +
                            '<div id="progress_' + n + '" class="progress"></div>' +
                            '<div class="obj">' + file.name + '</div>' +
                            '<input type="hidden" name="uploaded" value="' + file.name + '"></input>' +
                            '</div>');
            $("#upload_queue").append(filediv);
            var progress = $("#progress_" + n);
            progress.progressbar();
            upload.file_read(n, file);
        }
    }
}

upload.file_upload = function(queue_id, fileData) {
    var progress = $("#progress_" + queue_id);
    var file = upload.queue.files[queue_id];
    var xhr = new XMLHttpRequest();
    
    $(xhr.upload).bind("progress", function(e) {
        var oe = e.originalEvent;
        //console.log('progress event', oe);
        if (oe.lengthComputable) {
            var percentage = Math.round((oe.loaded * 100) / oe.total);
            progress.progressbar('option', 'value', percentage);
        }
        return false;
    });
  
    $(xhr.upload).bind("load", function(e){
        //console.log('FileUpload: load event', e, xhr);
        progress.progressbar('option', 'value', 100);
        if (xhr.status != 200) {
            progress.addClass("error");
        }
    });
  
    $(xhr.upload).bind("error", function(e){
        //console.log('FileUpload: error event');
        progress.progressbar('option', 'value', 100);
        progress.addClass("error");
    });
  
    var boundaryString = "S-P-A-M----u-p-l-o-a-d--X30";
    var boundary = "--"+boundaryString;

    var fileData = file.getAsBinary();

    var postContent = 
        '\r\n' + boundary + '\r\n' +
        'Content-Disposition: file; name="uploadedfile"; filename="' + file.name + '"\r\n'+
        'Content-Type: ' + file.type + '\r\n'+
        "\r\n"+
        fileData + "\r\n";
    
    xhr.open("POST", upload.target);
    xhr.setRequestHeader('Content-Type', 'multipart/form-data; boundary=' + boundaryString);
    xhr.setRequestHeader('Content-Length', postContent.length);
    xhr.sendAsBinary(postContent);
    
}

$(function(){
    $(".uploader").bind("dragenter", function(e) {
        return false;  
    }).bind("dragover", function(e) {
        return false;  
    }).bind("drop", function(e) {
        var dt = e.originalEvent.dataTransfer;
        //console.log("dropped!", dt, e);
        upload.handle_files(dt.files);
        return false;
    });
    
    $("input.uploader").bind("change", function(e) {
        //console.log("changed!", e);
        upload.handle_files(e.target.files);
        return false;
    });
    
});

##</script>

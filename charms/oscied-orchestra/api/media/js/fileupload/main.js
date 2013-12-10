/*
 * jQuery File Upload Plugin JS Example 6.7
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/*jslint nomen: true, unparam: true, regexp: true */
/*global $, window, document */

$(function () {
    'use strict';

    // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload();

    // Enable iframe cross-domain access via redirect option:
    $('#fileupload').fileupload(
        'option',
        'redirect',
        window.location.href.replace(
            /\/[^\/]*$/,
            '/cors/result.html?%s'
        )
    );

     $('#fileupload').fileupload('option', {
         /*url: '//jquery-file-upload.appspot.com/',*/
         maxFileSize: 5000000,
         acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i,
         previewSourceFileTypes: /^image\/(gif|jpeg|png)$/,
         // The maximum file size of images that are to be displayed as preview:
         previewSourceMaxFileSize: 5000000, // 5MB
         // The maximum width of the preview images:
         previewMaxWidth: 80,
         // The maximum height of the preview images:
         previewMaxHeight: 80,
         // By default, preview images are displayed as canvas elements
         // if supported by the browser. Set the following option to false
         // to always display preview images as img elements:
         previewAsCanvas: true,
         process: [
             {
                 action: 'load',
                 fileTypes: /^image\/(gif|jpe?g|png)$/,
                 maxFileSize: 20000000 // 20MB
             },
             {
                 action: 'resize',
                 maxWidth: 1440,
                 maxHeight: 900
             },
             {
                 action: 'save'
             }
         ]
     });

});

// static/admin/js/code-highlighting.js

(function($) {
    $(document).ready(function() {

        // Initialize code highlighting in admin
        if (typeof hljs !== 'undefined') {
            hljs.highlightAll();
        }

        // Auto-format pasted code in Summernote
        $(document).on('summernote.paste', function(we, e) {
            var clipboardData = e.originalEvent.clipboardData;
            if (clipboardData) {
                var pastedText = clipboardData.getData('text/plain');

                // Simple detection of code patterns
                var isCode = false;
                var language = 'text';

                if (pastedText.includes('def ') || pastedText.includes('import ') || pastedText.includes('print(')) {
                    isCode = true;
                    language = 'python';
                } else if (pastedText.includes('function ') || pastedText.includes('const ') || pastedText.includes('let ')) {
                    isCode = true;
                    language = 'javascript';
                } else if (pastedText.includes('SELECT ') || pastedText.includes('FROM ') || pastedText.includes('WHERE ')) {
                    isCode = true;
                    language = 'sql';
                } else if (pastedText.includes('<html>') || pastedText.includes('<!DOCTYPE')) {
                    isCode = true;
                    language = 'html';
                } else if (pastedText.includes('{') && pastedText.includes('}') && pastedText.includes(':')) {
                    // Could be CSS or JSON
                    if (pastedText.includes('color:') || pastedText.includes('margin:') || pastedText.includes('padding:')) {
                        isCode = true;
                        language = 'css';
                    } else {
                        isCode = true;
                        language = 'json';
                    }
                }

                // If it looks like code and has multiple lines, wrap it in a code block
                if (isCode && pastedText.split('\n').length > 2) {
                    e.preventDefault();

                    var codeHtml = [
                        '<pre class="code-block" data-language="' + language + '">',
                        '<code class="language-' + language + '">',
                        pastedText.replace(/</g, '&lt;').replace(/>/g, '&gt;'),
                        '</code>',
                        '</pre>',
                        '<p><br></p>'
                    ].join('');

                    $(e.target).summernote('pasteHTML', codeHtml);
                }
            }
        });

        // Style improvements for Summernote
        $('.django-summernote-widget').css({
            'border': '1px solid #ddd',
            'border-radius': '4px'
        });

        // Add helpful tooltips
        $('.note-btn[data-original-title*="Code"]').attr('title', 'Insert Code Block - Select language and add your code!');

        console.log('✅ Code highlighting admin enhancements loaded');
    });
})(django.jQuery);
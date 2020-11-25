$(document).ready(function () {
    let terminator = $('#terminal').get(0)
    let sock = new window.WebSocket(url)
    let url_opts_data = {},
        term = new window.Terminal({
            cursorBlink: true,
            theme: {
                background: url_opts_data.bgcolor || 'black'
            }
        }),
        style = {},
        custom_font = document.fonts ? document.fonts.values().next().value : undefined,
        title_element = document.querySelector('title'),
        default_title = 'AutoOps-WebSSH',
        encoding = 'utf-8',
        decoder = window.TextDecoder ? new window.TextDecoder(encoding) : encoding,
        default_fonts;
    term.fitAddon = new window.FitAddon.FitAddon();
    term.loadAddon(term.fitAddon);
    term.on_resize = function (cols, rows) {
        if (cols !== this.cols || rows !== this.rows) {
            console.log('Resizing terminal to geometry: ' + format_geometry(cols, rows));
            this.resize(cols, rows);
            sock.send(JSON.stringify({'resize': [cols, rows]}));
        }
    };

    term.onData(function (data) {
        console.log(data);
        sock.send(JSON.stringify({'data': data}));
    });
    sock.onopen = function () {
        term.open(terminator);
        toggle_fullscreen(term);
        update_font_family(term);
        term.focus();
        title_element.text = url_opts_data.title || default_title;
        // if (url_opts_data.command) {
        //     setTimeout(function () {
        //         sock.send(JSON.stringify({'data': url_opts_data.command + '\r'}));
        //     }, 500);
        // }
    };

    sock.onmessage = function (msg) {
        console.log('sock on message!')
        read_file_as_text(msg.data, term_write, decoder);
    };

    sock.onerror = function (e) {
        console.error(e);
    };

    sock.onclose = function (e) {
        term.dispose();
        term = undefined;
        sock = undefined;
        title_element.text = default_title;
        console.log('connection closed!')
        window.close()
    };

    function format_geometry(cols, rows) {
        return JSON.stringify({'cols': cols, 'rows': rows});
    }

    function custom_font_is_loaded() {
        if (!custom_font) {
            console.log('No custom font specified.');
        } else {
            console.log('Status of custom font ' + custom_font.family + ': ' + custom_font.status);
            if (custom_font.status === 'loaded') {
                return true;
            }
            if (custom_font.status === 'unloaded') {
                return false;
            }
        }
    }

    function update_font_family(term) {
        if (term.font_family_updated) {
            console.log('Already using custom font family');
            return;
        }

        if (!default_fonts) {
            default_fonts = term.getOption('fontFamily');
        }

        if (custom_font_is_loaded()) {
            var new_fonts = custom_font.family + ', ' + default_fonts;
            term.setOption('fontFamily', new_fonts);
            term.font_family_updated = true;
            console.log('Using custom font family ' + new_fonts);
        }
    }


    function read_as_text_with_decoder(file, callback, decoder) {
        var reader = new window.FileReader();

        if (decoder === undefined) {
            decoder = new window.TextDecoder('utf-8', {'fatal': true});
        }

        reader.onload = function () {
            var text;
            try {
                text = decoder.decode(reader.result);
            } catch (TypeError) {
                console.log('Decoding error happened.');
            } finally {
                if (callback) {
                    callback(text);
                }
            }
        };

        reader.onerror = function (e) {
            console.error(e);
        };

        reader.readAsArrayBuffer(file);
    }

    function read_as_text_with_encoding(file, callback, encoding) {
        var reader = new window.FileReader();

        if (encoding === undefined) {
            encoding = 'utf-8';
        }

        reader.onload = function () {
            if (callback) {
                callback(reader.result);
            }
        };

        reader.onerror = function (e) {
            console.error(e);
        };

        reader.readAsText(file, encoding);
    }

    function read_file_as_text(file, callback, decoder) {
        if (!window.TextDecoder) {
            read_as_text_with_encoding(file, callback, decoder);
        } else {
            read_as_text_with_decoder(file, callback, decoder);
        }
    }

    function term_write(text) {
        if (term) {
            term.write(text)
            if (!term.resized) {
                resize_terminal(term);
                term.resized = true;
            }
        }
    }

    function parse_xterm_style() {
        var text = $('.xterm-helpers style').text();
        var arr = text.split('xterm-normal-char{width:');
        style.width = parseFloat(arr[1]);
        arr = text.split('div{height:');
        style.height = parseFloat(arr[1]);
    }


    function get_cell_size(term) {
        style.width = term._core._renderService._renderer.dimensions.actualCellWidth;
        style.height = term._core._renderService._renderer.dimensions.actualCellHeight;
    }

    function toggle_fullscreen(term) {
        $('#terminal .terminal').toggleClass('fullscreen');
        term.fitAddon.fit();
    }

    function current_geometry(term) {
        if (!style.width || !style.height) {
            try {
                get_cell_size(term);
            } catch (TypeError) {
                parse_xterm_style();
            }
        }

        var cols = parseInt(window.innerWidth / style.width, 10) - 1;
        var rows = parseInt(window.innerHeight / style.height, 10);
        return {'cols': cols, 'rows': rows};
    }


    function resize_terminal(term) {
        var geometry = current_geometry(term);
        term.on_resize(geometry.cols, geometry.rows);
    }


});


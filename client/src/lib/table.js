import { Matrix } from "./matrix.js";
import {
    enumerate,
    strip,
    strip_whitespace,
    split,
    pad_center,
    len,
    range,
    zip,
} from "./utils.js";

const strip_beginning_whitespace_pipe_and_dash = strip(
    { characters: " \t\n-|", from_end: false });

const strip_pipe_from_end = strip({ characters: " \n|", from_start: false });

Array.prototype.max = function () {
    let winner = -Infinity;
    for (let i = 0; i < this.length; i++) {
        if (this[i] > winner) winner = this[i];
    }
    return winner;
}

Array.prototype.max_or = function (value) {
    if (this.length === 0) return value;
    return this.max();
}

// what does this function take in? What is 'span'?
export function reverse_spans(spans) {
    // [
    //   [ 1, 1, 1 ],
    //   [ 2, 2, 1 ],
    //   ...
    //   .
    //   .
    // ]
    // TODO solve this in general
    if (spans.length === 1) return 1;

    if (spans[0] === 1 && spans[1] === 1) {
        // [1, 1] -> [1, 1]
        return [1, 1];
    } else if (spans[0] === 1 && spans[1] === 2) {
        // [1, 2] -> [2, 1]
        return [2, 1];
    } else if (spans[0] === 2 && spans[1] === 1) {
        // [2, 1] -> [1, 2]
        return [1, 2];
    } else {
        throw Error("unhandled case");
    }
}

class MisalignedError extends Error {
    constructor(row, column, char, ...params) {
        super(...params);
        this.name = this.constructor.name;
        this.message = `Mis-aligned column in row ${row}. `
            + `Because "|" was found in this column on line 1, expected `
            + `"|" to be found in column ${column} but, but found '${char}'.`;
    }
}

function find_all_indexes(ch) {
    return s => Array.from(s)
        .map((char, i) => [char === ch, i])
        .filter(([keep, idx]) => keep)
        .map(([_keep, idx]) => idx);
}

function align_and_nullfill(arrays) {
    // given
    //   [
    //     [ 0, 5, 9, 13],
    //     [ 1, 5, 9, 13],
    //   ]
    // produce
    //   [
    //     [   0, null, 5, 9, 13],
    //     [null,    1  5, 9, 13],
    //   ]

    // first find length (which is number of unique numbers)
    const s = new Set;
    for (let array of arrays) for (let number of array) s.add(number);
    const numbers = ([...s]).sort((a, b) => a < b ? -1 : 1);
    const length = s.size;

    const out = Array(arrays.length).fill(0).map(_0 => []);

    const next_indexes = Array(arrays.length).fill(0);

    for (const n of numbers) {
        const to_add = [];
        for (let arr of arrays) {
            if (arr.includes(n)) {
                to_add.push(n);
            } else {
                to_add.push(null);
            }
        }
        for (let i = 0; i < out.length; i++) {
            out[i].push(to_add[i]);
        }
    }

    return out;
}

/* group_by_length(lines)
 *   takes a multiline string `lines`,
 *   trims all lines, filters away empty ones,
 *   and groups the remaining ones by their length,
 *   so that e.g. the string
 *     abcd
 *     efgh
 *     xx
 *     yy
 *   will return
 *     [ ["abcd", "efgh"], ["xx", "yy"] ]
 */
export function group_by_length(lines) {
    lines = lines.split("\n").map(line => line.trimEnd()).filter(line => line.length > 0);

    let current_len = lines[0].length;
    let current_group = [lines[0]];
    const groups = [];
    for (let line of lines.slice(1)) {
        if (line.length !== current_len) {
            // this line's length is different, so make next group
            current_len = line.length;
            groups.push(current_group);
            current_group = [];
        }
        current_group.push(line);
    }
    if (current_group.length > 0) {
        groups.push(current_group);
    }
    return groups;
}

export class Table {
    #data;

    constructor(caption, data, row_headers, column_headers) {
        this.caption = caption;
        this.data = data;
        this.row_headers = row_headers;
        this.column_headers = column_headers;
    }

    [Symbol.toPrimitive]() {
        const x = this.data.width;
        const y = this.data.height;
        const caption = this.caption ? `("${this.caption}")` : "";
        return `Table<${y}, ${x}>${caption}`;
    }

    without_empty_columns_and_rows() {
        const data_without = this.data.without_empty_columns_and_rows();
        const { matrix: new_data, kept_cols, kept_rows } = data_without;

        const kept_columns = Object.entries(kept_cols)
            .map(([x, y]) => [Number(x), Number(y)])
            .sort(([x1, x2], [y1, y2]) => x1 - y1);

        const new_row_headers = [];
        if (this.row_headers.length > 0) {
            for (let key of Object.keys(kept_rows).sort()) {
                new_row_headers.push(this.row_headers[key]);
            }
        }
        
        const new_column_headers = Array(this.column_headers.length)
            .fill(null).map(_ => []);
        const span_adjustments = Array(this.column_headers.length).fill(0);

        for (let [_old, _new] of kept_columns) {
            for (let i = 0; i < new_column_headers.length; i++) {
                const { text, span } = this.column_headers[i][_old - span_adjustments[i]];

                // TODO how do I know what the new span really should be?
                new_column_headers[i].push({ text, span: 1 });

                // adjust spans
                if (span > 1) {
                    span_adjustments[i] += (span - 1);
                }
            }
        }

        return new Table(this.caption, new_data, new_row_headers, new_column_headers);
    }

    static from_format(format, caption = null) {
        const groups = group_by_length(format);
        let row_headers, column_headers;

        if (groups.length === 1) {
            const first_line = groups[0][0];
            const splits = first_line.split("|").map(s => s.trim()).filter(s => s.length > 0);
            
            let data;

            if (splits.length === 1) {
                row_headers = groups[0].map(strip_pipe_from_end);
                column_headers = [];
                data = new Matrix(row_headers.length, 1);
            } else {
                row_headers = [];
                column_headers = [
                    groups[0][0].split("|")
                        .map(strip_whitespace)
                        .map(ch => ({ text: ch, span: 1 }))
                ];
                data = new Matrix(1, column_headers[0].length);
            }

            return new Table(caption, data, row_headers, column_headers);
        }

        if (groups.length !== 2) {
            // XXX handle other lengths? Does other lengths even make sense?
            throw new Error("Table.from_format(): malformed format");
        }

        [column_header_lines, row_headers] = group_by_length(format);
        row_headers = row_headers
            .map(s => s.trim().replaceAll("|", ""))
            .filter(s => s.length > 0);

        const column_header_text_length = column_header_lines[0].length;
        const separator_indexes = column_header_lines
            .map(find_all_indexes("|"));
        const aligned = align_and_nullfill(separator_indexes);
        column_headers = column_header_lines
            .map(strip_pipe_from_end).map(line =>
                line.split("|").map(strip_whitespace)
                    .filter(s => (s !== "-") && (s !== ""))
                    .map(s => ({ text: s, span: 1 })));
        
        for (let [slots, obj] of zip(aligned, column_headers)) {
            for (let i = 1; i < slots.length; i++) {
                if (slots[i] === null) {
                    if (obj[i - 1]) {
                        obj[i - 1].span++;
                    }
                }
            }
        }

        // trim empty column_headers from the start
        const col_header_width = column_headers.map(len).max();
        const data = new Matrix(row_headers.length, col_header_width);

        return new Table(caption, data, row_headers, column_headers);
    }

    as_console_str({
        show_caption = true,
        caption_format = "{caption}",
        caption_placement = "top",
        empty_indicator = "-",
    } = {}) {
        // retrieve the lines of data from the underying matrix
        const data_lines = this.data.as_console_str({ empty_indicator }).split("\n");

        // find the widest entry out of all the fields
        const widest_data_field = data_lines[0].split("|").map(len).max();
        const widest_row_header = this.row_headers.map(len).max_or(0);
        const widest_column_header =
            this.column_headers
                .map(arr =>
                    arr.map(obj => obj.text)
                    .map(len)
                    .max()
                )
                .max_or(1);

        const num_columns = this.column_headers.map(len).max_or(1);
        const entry_width = 2 + [widest_column_header, widest_row_header, widest_data_field].max();

        // pad out the data to the new width
        const padded_data_lines = data_lines.map(line =>
            line.split("|")
                 .map(strip_whitespace)
                 .map(text => pad_center(text, entry_width))
                 .join("|"));

        const lines = [];

        // add the lines of matrix data, with the row header included
        if (this.row_headers.length > 0) {
            for (const [row_header, data_line] of zip(this.row_headers, padded_data_lines)) {
                lines.push(`${row_header} | ${data_line}`);
            }
        } else {
            // no row headers
            for (const data_line of padded_data_lines) {
                lines.push(data_line);
            }
        }

        // add the column headers
        const column_header_rows = [];
        for (let i = 0; i < this.column_headers.length; i++) {
            let line = [];
            if (this.row_headers.length > 0) {
                line.push(" ".repeat(widest_row_header - 1) + "- ");
            }

            for (let j = 0; j < this.column_headers[i].length; j++) {
                const { text, span } = this.column_headers[i][j];
                // TODO the width is incorrect either here or above, figure it out for perfect alignment
                const width = entry_width + ((span - 1) * (entry_width + 1));
                line.push(pad_center(text, width));
            }

            column_header_rows.push(line.join("|"));
        }

        // add a dotted line between the column headers and the rest
        column_header_rows.push("-".repeat(entry_width * num_columns + widest_row_header + 1));

        // finally actually append them, using unshift() because the order is reversed
        for (let i = column_header_rows.length - 1; i >= 0; i--) {
            lines.unshift(column_header_rows[i]);
        }

        if (show_caption) {
            const max_line_length = lines.map(len).max();
            let caption = caption_format.replaceAll("{caption}", this.caption);
            caption = pad_center(caption, max_line_length - caption.length);

            if (caption_placement === "top") {
                lines.unshift("");
                lines.unshift(caption);
            } else if (caption_placement === "bottom") {
                lines.push("");
                lines.push(caption);
            }
        }

        return lines.join("\n");
    }
}


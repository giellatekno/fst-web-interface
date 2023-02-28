import { Matrix } from "./matrix.js";
import {
    enumerate,
    strip,
    strip_whitespace,
    pad_center,
    len,
    range,
    zip,
} from "./utils.js";

const strip_beginning_whitespace_pipe_and_dash = strip(
    { characters: " \t\n-|", from_end: false });

const strip_pipe_from_end = strip({ characters: " \n|", from_start: false });

Array.prototype.max = function () {
    return Math.max(...this);
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
            .map(([x, y]) => ([Number(x), Number(y)]))
            .sort(([x1, x2], [y1, y2]) => x1 < y1 ? -1 : 1);
        // [ [0, 0]  [2, 1] ]

        const new_row_headers = [];
        for (let key of Object.keys(kept_rows).sort()) {
            new_row_headers.push(this.row_headers[key]);
        }
        
        const new_column_headers = Array(this.column_headers.length).fill(null).map(_ => []);
        const indexes = Array(this.column_headers.length).fill(0);
        
        for (let [old_col, new_col] of kept_columns) {
            // [ [0, 0], [2, 1] ]
            for (let column_row = 0; column_row < this.column_headers.length; column_row++) {
                const { text, span } = this.column_headers[column_row][new_col + indexes[column_row]];

                new_column_headers[column_row].push({ text, span });
            }
            
            for (let aa = 0; aa < indexes.length; aa++) {
                for (let bb = 0; bb < indexes.length; bb++) {
                    if (aa === bb) continue;
                    const other_span = this.column_headers[aa][bb].span;
                    indexes[bb] += other_span;
                }
            }
        }

        /*
        for (let column_row = 0; column_row < new_column_headers.length; column_row++) {
            const row = new_column_headers[column_row];
            row.unshift({ text: "-", span: 1 });
        }
        */

        //console.log("new table has these column headers");
        //console.log(new_column_headers);

        return new Table(this.caption, new_data, new_row_headers, new_column_headers);
    }

    static from_format(format, caption = null) {
        const groups = group_by_length(format);
        if (groups.length === 1) {
            // no column headers, OR no row headers!
        }
        if (groups.length == 2) {
            // 
        }

        // TODO this assumtion doesn't always hold, figure out a better way to do this
        let [column_header_lines, row_headers] = group_by_length(format);
        row_headers = row_headers
            .map(s => s.trim().replaceAll("|", ""))
            .filter(s => s.length > 0);

        const column_header_text_length = column_header_lines[0].length;
        const separator_indexes = column_header_lines
            .map(find_all_indexes("|"));
        const aligned = align_and_nullfill(separator_indexes);
        const column_headers = column_header_lines
            .map(strip_pipe_from_end).map(line =>
                line.split("|")
                    .map(s => s.trim())
                    .filter(s => (s !== "-") && (s !== ""))
                    .map(s => ({ text: s, span: 1 }))
            );
        
        for (let [slots, obj] of zip(aligned, column_headers)) {
            for (let i = 1; i < slots.length; i++) {
                if (slots[i] === null) {
                    if (obj[i - 1]) {
                        obj[i - 1].span++;
                    }
                }
            }
        }

        /*
        const column_header_height = column_header_lines.length;
        const column_headers = Array(column_header_height).fill(0).map(_0 => []);

        const next_objects = Array(column_header_height).fill(0).map(_0 => ({ text: "", span: 1 }));

        // indexes into separator_indexes
        const indexes_indexes = Array(column_header_lines.length).fill(0);

        for (let top_index = 0; top_index < separator_indexes[0].length; top_index++) {
            const top = separator_indexes[0][top_index];
            // 1, 5, 9, 13
        }

        for (let char = 0; char < column_header_text_length; char++) {
            for (let ch = 0; ch < column_header_height; ch++) {
                const character = column_header_lines[ch][char];
                if (character === "|") {
                    // if we're on the non-first row, and the character above
                    // is _not_ a "|", then we need to increase the above slot's
                    // span
                    if (ch > 0) {
                        const character_above = column_header_lines[ch - 1][char];
                        if (character_above !== "|") {
                            next_objects[ch - 1].span++;
                        }
                    }

                    column_headers[ch].push(next_objects[ch]);
                    next_objects[ch] = { text: "", span: 1 };
                } else if (character === " ") {
                    // do nothing
                } else {
                    // text here
                    next_objects[ch].text += character;
                }
            }
        }
        */

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
        const widest_row_header = this.row_headers.map(len).max();
        const widest_column_header = this.column_headers
                .map(arr => arr.map(obj => obj.text).map(len).max()).max();
        const num_columns = this.column_headers.map(len).max();
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


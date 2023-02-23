import { Matrix } from "./matrix.js";
import { enumerate, strip_whitespace, pad_center, len } from "./utils.js";

Array.prototype.max = function () {
    return Math.max(...this);
}

// what does this function take in?
// what is `span`?
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
    lines = lines.split("\n").map(line => line.trim()).filter(line => line.length > 0);

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

/*
  make_table()
    take string format input (as shown below), and turn it into a structure
    like this:
let table = {
    caption: "caption",
    row_headers: ["1", "2"],
    columns: [
        [{text: "A", span: 1}, { text: "B", span: 2}, {text: "C", span: 1}],
        [{text: "_a", span: 1}, { text: "_b1", span: 1 }, {text: "_b2", span:1}, {text: "c", span:1}],
    ],
    data: [
        ["a", "b"],
        ["c", "d"],
    ],
};
*/

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

        const new_row_headers = [];
        for (let key of Object.keys(kept_rows).sort()) {
            new_row_headers.push(this.row_headers[key]);
        }
        
        const new_column_headers = Array(this.column_headers.length).fill(null).map(_ => []);

        /*  this.columns =
        [
          [ { text: '-', span: 1 }, { text: 'A', span: 2 }, { text: 'B', span: 1 }, { text: 'C', span: 1 } ],
          [ { text: '-', span: 1 }, { text: 'x', span: 1 }, { text: 'y', span: 1 }, { text: 'D', span: 1 }, { text: 'E', span: 1 }
          ]
        ]
        */
        // gitt også kept_columns = [ [0, 0], [2, 1] ]
        // fill with 1 instead of 0 because of the implicit first "-" column
        const indexes = Array(this.column_headers.length).fill(1);
        // [ 0, 0 ]
        
        for (let [old_col, new_col] of kept_columns) {
            for (let column_row = 0; column_row < this.column_headers.length; column_row++) {
                const i = column_row + indexes[column_row];
                const row = this.column_headers[column_row][new_col + indexes[column_row]];

                //indexes[column_row] += (row.span - 1);

                new_column_headers[column_row].push({ text: row.text, span: 1 });
            }
            
            for (let aa = 0; aa < indexes.length; aa++) {
                for (let bb = 0; bb < indexes.length; bb++) {
                    if (aa === bb) continue;
                    const other_span = this.column_headers[aa][bb].span;
                    indexes[bb] += other_span - 1;
                }
            }
        }

        for (let column_row = 0; column_row < new_column_headers.length; column_row++) {
            const row = new_column_headers[column_row];
            row.unshift({ text: "-", span: 1 });
        }
        // skal hit:
        // [
        //   [ { text: "A", span: 1 }, { text: "B", span: 1 } ],
        //   [ { text: "x", span: 1 }, { text: "D", span: 1 } ],
        // ]
        
        return new Table(this.caption, new_data, new_row_headers, new_column_headers);
    }

    static from_format(format, caption = null) {
        let [column_header_lines, row_headers] = group_by_length(format);
        row_headers = row_headers
            .map(s => s.trim().replaceAll("|", ""))
            .filter(s => s.length > 0);

        // looks like: [ [], [], [], ... ]  (one subarray for each column header row)
        const column_header_height = column_header_lines.length;
        const column_headers = Array(column_header_height).fill(0).map(_0 => []);

        const next_objects = Array(column_header_height).fill(0).map(_0 => ({ text: "", span: 1 }));

        // how many characters the column header lines are. this is the same for all column headers
        const column_header_text_length = column_header_lines[0].length;

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
        let lines = [];

        const data_lines = this.data.as_console_str({ empty_indicator }).split("\n");
        const column_width = data_lines[0].split("|").map(len)
            .reduce((prev, cur) => Math.max(prev, cur));

        for (let i = 0; i < this.row_headers.length; i++) {
            const header = this.row_headers[i];
            const data_line = data_lines[i];
            const line = `${header} | ${data_line}`;
            lines.push(line);
        }

        // prepend the column headers
        const column_header_rows = [];
        for (let i = 0; i < this.column_headers.length; i++) {
            for (let x = 0; x < this.column_headers[i].length; x++) {
                const ch = this.column_headers[i][x];
            }
            let line = "";

            let first_column = true;
            for (let j = 0; j < this.column_headers[i].length; j++) {
                const o = this.column_headers[i][j];
                if (first_column) {
                    first_column = false;
                    line += o.text + " |";
                } else {
                    if (o.span > 1) {
                        line += pad_center(o.text, column_width * 2) + "|";
                    } else {
                        line += pad_center(o.text, column_width) + " |";
                    }
                }
            }

            column_header_rows.push(line);
        }
        column_header_rows.push("-".repeat(data_lines[0].length + 3));
        for (let i = column_header_rows.length - 1; i >= 0; i--) {
            lines.unshift(column_header_rows[i]);
        }

        if (show_caption) {
            const max_line_length = Math.max(...lines.map(line => line.length));
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


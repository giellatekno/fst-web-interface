import { Matrix } from "./matrix.js";
import { enumerate, trim, pad_center, len } from "./utils.js";

Array.prototype.max = function () {
    return Math.max(...this);
}

function reverse_spans(spans) {
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
            + `"|" to be found in column ${column} but, but found ${char}.`;
    }
}

function group_by_length(lines) {
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
        const {
            matrix: new_data,
            kept_rows,
            kept_cols,
        } = this.data.without_empty_columns_and_rows();

        this.data = new_data;

        const new_row_headers = [];
        for (let key of Object.keys(kept_rows).sort()) {
            new_row_headers.push(this.row_headers[key]);
        }
        
        // columns:
        // [
        //   [{..}, {..}, {..}],
        //   [{..}, {..}, {..}],    in my example: this is the longest
        // ]
        const new_column_headers = Array(this.column_headers.length).fill(null).map(_ => []);

        // "pointers" into how far we currently are in the
        // `this.columns` array of arrays
        const indexes = Array(this.column_headers.length).fill(0);

        // kept_cols = { 0: 0, 1: 1 }
        for (let [new_col, old_col] of Object.entries(kept_cols)) {
            // this loop: [0, 0], [1, 1]
            // TODO but will it be in rising order? that is from index 0 first,
            // then index 1, then the next, etc..

            const to_push = [];
            for (let i = 0; i < this.column_headers.length; i++) {
                let found = 0;
                for (let x = 0; x < this.column_headers[i].length; x++) {
                    found += this.column_headers[i][x].span;
                    if (found === old_col) {
                    }
                }
                // this.columns[i][old_col]
                // THAT'S NOT NECESSARILY TRUE
            }

            const __ = {
                    text: "...",
                    span: -1,
            }

            for (let i = 0; i < to_push.length; i++) {
                new_column_headers[i].push(to_push);
            }
        }
        
        return new Table(this.caption, new_data, new_row_headers, new_column_headers);
    }

    static from_format(format, caption = null) {
        const lines = format.split("\n").filter(line => line.trim().length > 0);

        let [col_header_lines, row_headers] = group_by_length(lines);
        row_headers = row_headers
            .map(s => s.trim().replaceAll("|", ""))
            .filter(s => s.length > 0);

        const col_headers = col_header_lines
            .map(col_header_line =>
                col_header_line
                    .split("|")
                    .map(ch => trim(ch, "- "))
                    .filter(ch => ch.length > 0)
                );

        const col_header_height = col_headers.length;
        const col_header_width = col_headers.map(len).max();
        const data = new Matrix(row_headers.length, col_header_width);
        const column_headers = Array(col_header_height).fill(0).map(_0 => []);

        let last_index = 0;
        const first_col_row = col_headers[0];
        for (let [i, ch] of enumerate(first_col_row)) {
            // (0, A)  (1, B)  (2, C)
            const first_col = first_col_row.slice(last_index, i + 1);
            const to_be_pushed = [first_col];

            console.log("first_col:", first_col);

            // find the other headers - there may not be any
            for (let j = 1; j < col_headers.length; j++) {
                console.log("???");
                const ch_other = col_headers[j][i];
                if (ch_other !== ch) {
                    throw new MisalignedError(j + 1, i, ch_other);
                }

                let other_col = col_headers[j].slice(last_index, i);
                to_be_pushed.push(other_col);
            }

            console.log("to_be_pushed:", to_be_pushed);
            const to_be_pushed_splits = to_be_pushed.map(s => s.split("|"));
            const spans = to_be_pushed_splits.map(arr => arr.length);
            console.log("to_be_pushed_splits:", to_be_pushed_splits);
            console.log("spans:", spans);

            const rev_spans = reverse_spans(spans);

            for (let [t, arr] of enumerate(to_be_pushed_splits)) {
                console.log("X");
                for (let inner_idx = 0; inner_idx < arr.length; inner_idx++) {
                    console.log("Y");
                    column_headers[t].push({
                        text: arr[inner_idx],
                        span: rev_spans[t],
                    });
                }
            }

            last_index = i + 1;
        }

        console.log("!!!");
        console.log(column_headers);
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
        for (let i = 0; i < this.row_headers.length; i++) {
            const header = this.row_headers[i];
            const data_line = data_lines[i];
            const line = `${header} | ${data_line}`;
            lines.push(line);
        }

        // prepend the column headers
        for (let i = 0; i < this.column_headers.length; i++) {
            // TODO these must be padded out
            for (let x = 0; x < this.column_headers[i].length; x++) {
                const ch = this.column_headers[i][x];
                console.log("!!");
                console.log(ch);
            }
            let line = this.column_headers[i].map(obj => obj.text).join("|");
            lines.unshift(line);
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

